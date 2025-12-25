from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class VoltageLevel(str, Enum):
    MV_34 = "34.5kV"
    MV_13 = "13.8kV"
    LV = "0.38kV"
    UNKNOWN = "unknown"


class ElementType(str, Enum):
    BUS = "bus"
    LINE = "line"
    SWITCH = "switch"
    TRANSFORMER = "transformer"
    SOURCE = "source"
    LOAD = "load"
    GROUND = "ground"
    LABEL = "label"


class SwitchState(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class GraphNode(BaseModel):
    id: str
    label: Optional[str] = None
    type: ElementType = ElementType.LINE
    voltage: VoltageLevel = VoltageLevel.UNKNOWN
    position: Optional[Dict[str, float]] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    type: ElementType = ElementType.LINE
    state: Optional[SwitchState] = None
    capacity_hint_amp: Optional[float] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

    class Config:
        allow_population_by_field_name = True


class Equipment(BaseModel):
    id: str
    type: ElementType
    label: Optional[str]
    confidence: float = 1.0
    bbox: Optional[List[float]] = None  # [x1,y1,x2,y2]


class GraphModel(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    equipments: List[Equipment] = Field(default_factory=list)
    page: int = 0
    source_nodes: List[str] = Field(default_factory=list)
    load_nodes: List[str] = Field(default_factory=list)
    layout_size: Optional[Dict[str, float]] = None


class SimulationResult(BaseModel):
    energized_nodes: List[str]
    energized_edges: List[str]
    flows: Dict[str, float]
    alerts: List[str]


class ProjectSummary(BaseModel):
    id: str
    filename: str
    status: str
    page_count: int
    message: Optional[str] = None


class UploadResponse(BaseModel):
    project: ProjectSummary


class ProcessStatus(BaseModel):
    status: str
    progress: float
    message: Optional[str] = None


class SimulationRequest(BaseModel):
    states: Dict[str, SwitchState] = Field(default_factory=dict)
