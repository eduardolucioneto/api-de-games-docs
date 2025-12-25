from typing import Dict, List, Set
import networkx as nx

from .models import GraphModel, SimulationResult, SwitchState, ElementType


class SimulationEngine:
    def __init__(self, model: GraphModel):
        self.model = model
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self) -> None:
        for node in self.model.nodes:
            self.graph.add_node(node.id, type=node.type)
        for edge in self.model.edges:
            is_closed = edge.state != SwitchState.OPEN if edge.type == ElementType.SWITCH else True
            self.graph.add_edge(edge.from_node, edge.to_node, id=edge.id, type=edge.type, closed=is_closed)

    def _energized_from_sources(self) -> Set[str]:
        energized: Set[str] = set()
        for source in self.model.source_nodes:
            if source in self.graph:
                for component in nx.node_connected_component(self.graph, source):
                    energized.add(component)
        return energized

    def run(self, overrides: Dict[str, SwitchState]) -> SimulationResult:
        for edge in self.graph.edges:
            self.graph.edges[edge]["closed"] = True
        for edge in self.model.edges:
            closed = edge.state != SwitchState.OPEN if edge.type == ElementType.SWITCH else True
            override_state = overrides.get(edge.id)
            if override_state:
                closed = override_state == SwitchState.CLOSED
            self.graph.edges[edge.from_node, edge.to_node]["closed"] = closed
        closed_graph = nx.Graph(
            (
                (u, v, d)
                for u, v, d in self.graph.edges(data=True)
                if d.get("closed", True)
            )
        )
        energized_nodes: Set[str] = set()
        for source in self.model.source_nodes:
            if source in closed_graph:
                energized_nodes.update(nx.node_connected_component(closed_graph, source))
        energized_edges: List[str] = []
        flows: Dict[str, float] = {}
        for u, v, data in self.graph.edges(data=True):
            edge_id = data.get("id")
            if not edge_id:
                continue
            if data.get("closed", True) and u in energized_nodes and v in energized_nodes:
                energized_edges.append(edge_id)
                flows[edge_id] = 1.0
        alerts = []
        if len(self.model.source_nodes) > 1:
            for i in range(len(self.model.source_nodes)):
                for j in range(i + 1, len(self.model.source_nodes)):
                    src_a = self.model.source_nodes[i]
                    src_b = self.model.source_nodes[j]
                    if src_a in closed_graph and src_b in closed_graph:
                        if nx.has_path(closed_graph, src_a, src_b):
                            alerts.append(
                                f"Paralelo de fontes detectado entre {src_a} e {src_b}."
                            )
        return SimulationResult(
            energized_nodes=sorted(list(energized_nodes)),
            energized_edges=sorted(energized_edges),
            flows=flows,
            alerts=alerts,
        )
