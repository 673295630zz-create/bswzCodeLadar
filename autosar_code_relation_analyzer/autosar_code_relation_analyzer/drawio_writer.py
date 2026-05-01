from __future__ import annotations

import xml.etree.ElementTree as ET

from .models import AnalysisResult


def write_drawio(result: AnalysisResult, output_path: str) -> None:
    mxfile = ET.Element('mxfile', host='app.diagrams.net')
    diagram = ET.SubElement(mxfile, 'diagram', name='Code Relation')
    model = ET.SubElement(diagram, 'mxGraphModel')
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    node_id = 2
    ids: dict[str, str] = {}

    def add_node(name: str, style: str, x: int, y: int) -> None:
        nonlocal node_id
        ids[name] = str(node_id)
        cell = ET.SubElement(root, 'mxCell', id=str(node_id), value=name, style=style, vertex='1', parent='1')
        ET.SubElement(cell, 'mxGeometry', {'x': str(x), 'y': str(y), 'width': '220', 'height': '40', 'as': 'geometry'})
        node_id += 1

    for idx, fn in enumerate(sorted({f.name for f in result.functions})):
        add_node(fn, 'rounded=1;whiteSpace=wrap;html=1;', 30, 30 + idx * 60)
    for idx, ext in enumerate(sorted(result.external_functions)):
        add_node(ext, 'rounded=1;dashed=1;whiteSpace=wrap;html=1;', 320, 30 + idx * 60)
    for idx, var in enumerate(sorted(result.variables)):
        add_node(var, 'shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;', 610, 30 + idx * 60)

    edge_styles = {'calls': 'calls', 'reads': 'reads', 'writes': 'writes', 'read_writes': 'read/writes', 'passed_by_address': 'addr'}
    for edge in result.call_relations + result.variable_relations:
        if edge.source not in ids or edge.target not in ids:
            continue
        cell = ET.SubElement(
            root,
            'mxCell',
            id=str(node_id),
            value=edge_styles.get(edge.relation_type, edge.relation_type),
            edge='1',
            parent='1',
            source=ids[edge.source],
            target=ids[edge.target],
        )
        ET.SubElement(cell, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        node_id += 1

    ET.ElementTree(mxfile).write(output_path, encoding='utf-8', xml_declaration=True)
