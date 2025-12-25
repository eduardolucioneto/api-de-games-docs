from .models import GraphModel, GraphNode, GraphEdge, Equipment, ElementType, SwitchState, VoltageLevel

SAMPLE_MODEL = GraphModel(
    nodes=[
        GraphNode(id="bus_A", label="SE-Primaria", type=ElementType.BUS, voltage=VoltageLevel.MV_13, position={"x": 100, "y": 100}),
        GraphNode(id="sw_1", label="SW-1", type=ElementType.SWITCH, position={"x": 220, "y": 100}),
        GraphNode(id="load_1", label="Alimentador 1", type=ElementType.LOAD, position={"x": 360, "y": 70}),
        GraphNode(id="trafo_1", label="TR-1", type=ElementType.TRANSFORMER, position={"x": 360, "y": 130}),
        GraphNode(id="bus_sec", label="Painel BT", type=ElementType.BUS, voltage=VoltageLevel.LV, position={"x": 500, "y": 130}),
        GraphNode(id="sw_2", label="SW-2", type=ElementType.SWITCH, position={"x": 620, "y": 130}),
        GraphNode(id="load_2", label="Carga BT", type=ElementType.LOAD, position={"x": 760, "y": 130}),
        GraphNode(id="source_main", label="Alimentador", type=ElementType.SOURCE, voltage=VoltageLevel.MV_13, position={"x": 40, "y": 100}),
        GraphNode(id="source_backup", label="Backup", type=ElementType.SOURCE, voltage=VoltageLevel.MV_13, position={"x": 40, "y": 200}),
        GraphNode(id="sw_3", label="Chave de Transferência", type=ElementType.SWITCH, position={"x": 220, "y": 200}),
        GraphNode(id="bus_B", label="SE-Secundaria", type=ElementType.BUS, voltage=VoltageLevel.MV_13, position={"x": 100, "y": 200}),
    ],
    edges=[
        GraphEdge(id="e1", from_node="source_main", to_node="bus_A", type=ElementType.LINE),
        GraphEdge(id="e2", from_node="bus_A", to_node="sw_1", type=ElementType.SWITCH, state=SwitchState.CLOSED),
        GraphEdge(id="e3", from_node="sw_1", to_node="load_1", type=ElementType.LINE),
        GraphEdge(id="e4", from_node="sw_1", to_node="trafo_1", type=ElementType.LINE),
        GraphEdge(id="e5", from_node="trafo_1", to_node="bus_sec", type=ElementType.TRANSFORMER),
        GraphEdge(id="e6", from_node="bus_sec", to_node="sw_2", type=ElementType.SWITCH, state=SwitchState.CLOSED),
        GraphEdge(id="e7", from_node="sw_2", to_node="load_2", type=ElementType.LINE),
        GraphEdge(id="e8", from_node="source_backup", to_node="bus_B", type=ElementType.LINE),
        GraphEdge(id="e9", from_node="bus_B", to_node="sw_3", type=ElementType.SWITCH, state=SwitchState.OPEN),
        GraphEdge(id="e10", from_node="sw_3", to_node="bus_A", type=ElementType.LINE),
    ],
    equipments=[
        Equipment(id="sw_1", type=ElementType.SWITCH, label="SW-1", confidence=0.93),
        Equipment(id="trafo_1", type=ElementType.TRANSFORMER, label="TR-1", confidence=0.88),
        Equipment(id="sw_2", type=ElementType.SWITCH, label="SW-2", confidence=0.92),
        Equipment(id="sw_3", type=ElementType.SWITCH, label="Chave Transferência", confidence=0.72),
    ],
    page=0,
    source_nodes=["source_main", "source_backup"],
    load_nodes=["load_1", "load_2"],
    layout_size={"width": 900, "height": 260},
)
