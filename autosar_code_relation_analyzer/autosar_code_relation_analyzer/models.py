from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class SourceFile:
    path: Path
    content: str


@dataclass(slots=True)
class FunctionDef:
    name: str
    file_path: str
    start_line: int
    end_line: int
    body: str


@dataclass(slots=True, frozen=True)
class RelationEdge:
    source: str
    target: str
    relation_type: str
    file_path: str
    line_hint: int | None = None


@dataclass(slots=True)
class AnalysisResult:
    source_root: str
    source_files: list[str] = field(default_factory=list)
    functions: list[FunctionDef] = field(default_factory=list)
    external_functions: set[str] = field(default_factory=set)
    variables: set[str] = field(default_factory=set)
    call_relations: list[RelationEdge] = field(default_factory=list)
    condition_relations: list[RelationEdge] = field(default_factory=list)
    define_relations: list[RelationEdge] = field(default_factory=list)
    variable_relations: list[RelationEdge] = field(default_factory=list)
