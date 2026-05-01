from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import defaultdict, deque

from .models import AnalysisResult


NODE_W = 240
NODE_H = 44


def _build_function_levels(result: AnalysisResult) -> dict[str, int]:
    funcs = sorted({f.name for f in result.functions})
    indegree = {f: 0 for f in funcs}
    graph: dict[str, set[str]] = defaultdict(set)
    for e in result.call_relations:
        if e.source in indegree and e.target in indegree and e.target not in graph[e.source]:
            graph[e.source].add(e.target)
            indegree[e.target] += 1
    q = deque([f for f in funcs if indegree[f] == 0])
    levels = {f: 0 for f in q}
    while q:
        cur = q.popleft()
        for nxt in graph[cur]:
            levels[nxt] = max(levels.get(nxt, 0), levels[cur] + 1)
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)
    for f in funcs:
        levels.setdefault(f, 0)
    return levels


def write_drawio(result: AnalysisResult, output_path: str) -> None:
    mxfile = ET.Element('mxfile', host='app.diagrams.net')
    diagram = ET.SubElement(mxfile, 'diagram', name='Code Relation')
    model = ET.SubElement(diagram, 'mxGraphModel')
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    node_id = 2
    ids: dict[str, str] = {}
    positions: dict[str, tuple[int, int]] = {}

    def add_node(name: str, style: str, x: int, y: int) -> None:
        nonlocal node_id
        ids[name] = str(node_id)
        positions[name] = (x, y)
        cell = ET.SubElement(root, 'mxCell', id=str(node_id), value=name, style=style, vertex='1', parent='1')
        ET.SubElement(cell, 'mxGeometry', {'x': str(x), 'y': str(y), 'width': str(NODE_W), 'height': str(NODE_H), 'as': 'geometry'})
        node_id += 1

    levels = _build_function_levels(result)
    rows = defaultdict(int)
    for fn in sorted({f.name for f in result.functions}):
        lv = levels.get(fn, 0)
        y = 30 + rows[lv] * 70
        x = 30 + lv * 320
        add_node(fn, 'rounded=1;whiteSpace=wrap;html=1;', x, y)
        rows[lv] += 1

    edge_col = 30 + (max(levels.values(), default=0) + 1) * 320
    for idx, ext in enumerate(sorted(result.external_functions)):
        add_node(ext, 'rounded=1;dashed=1;whiteSpace=wrap;html=1;', edge_col, 30 + idx * 70)
    for idx, macro in enumerate(sorted({e.target for e in result.define_relations})):
        add_node(f'#define {macro}', 'shape=note;whiteSpace=wrap;html=1;', edge_col, 380 + idx * 54)
        ids[macro] = ids[f'#define {macro}']
        positions[macro] = positions[f'#define {macro}']
    for idx, cond in enumerate(sorted({e.target for e in result.condition_relations})):
        add_node(cond, 'shape=hexagon;whiteSpace=wrap;html=1;', edge_col, 620 + idx * 54)
    for idx, var in enumerate(sorted(result.variables)):
        add_node(var, 'shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;', edge_col + 320, 30 + idx * 48)

    edge_styles = {
        'calls': 'calls', 'reads': 'reads', 'writes': 'writes', 'read_writes': 'read/writes',
        'passed_by_address': 'addr', 'if_condition': 'if', 'uses_define': 'define',
    }

    route_counter: dict[tuple[str, str], int] = defaultdict(int)
    all_edges = result.call_relations + result.condition_relations + result.define_relations + result.variable_relations
    for edge in all_edges:
        if edge.source not in ids or edge.target not in ids:
            continue
        sx, sy = positions[edge.source]
        tx, ty = positions[edge.target]
        channel_key = (str(min(sx, tx)), str(max(sx, tx)))
        route_counter[channel_key] += 1
        offset = 20 + route_counter[channel_key] * 12
        mid_x = (sx + tx) // 2 + offset

        style = 'edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;rounded=0;jettySize=auto;html=1;'
        cell = ET.SubElement(root, 'mxCell', id=str(node_id), value=edge_styles.get(edge.relation_type, edge.relation_type), style=style, edge='1', parent='1', source=ids[edge.source], target=ids[edge.target])
        geo = ET.SubElement(cell, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        arr = ET.SubElement(geo, 'Array', {'as': 'points'})
        ET.SubElement(arr, 'mxPoint', {'x': str(mid_x), 'y': str(sy + NODE_H // 2)})
        ET.SubElement(arr, 'mxPoint', {'x': str(mid_x), 'y': str(ty + NODE_H // 2)})
        node_id += 1

    ET.ElementTree(mxfile).write(output_path, encoding='utf-8', xml_declaration=True)
