from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LayoutInfo:
    name: str
    relative_file_path: str
    relative_dir_path: str
    content: str
    components: List[str]


@dataclass
class PageInfo:
    route_path: str
    relative_file_path: str
    components: List[str]
    has_params: bool
    has_form_submission: bool


@dataclass
class ApiInfo:
    route_path: str
    relative_file_path: str
    methods: List[str]
    input_validation: bool
    dependencies: List[str]


@dataclass
class FileInfo:
    relative_file_path: str
    relative_dir_path: str
    absolute_file_path: str
    name: str
    extension: str
    content: Optional[str] = None
    ast_parsed: Optional[Any] = None


@dataclass
class FrameworkInfo:
    id: str
    name: str
    version: str
    dir_path: str


@dataclass
class FileAnalysisResult:
    framework: str
    path: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AppAnalysis:
    framework: FrameworkInfo
    router_type: str
    stats: Dict[str, int]
    layouts: List[LayoutInfo]
    routes: List[Dict[str, Any]]
    api_routes: List[Dict[str, Any]]
    all_paths: List[str]
