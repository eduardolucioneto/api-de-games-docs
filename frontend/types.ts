export type VoltageLevel = "34.5kV" | "13.8kV" | "0.38kV" | "unknown";
export type ElementType =
  | "bus"
  | "line"
  | "switch"
  | "transformer"
  | "source"
  | "load"
  | "ground"
  | "label";
export type SwitchState = "open" | "closed";

export interface GraphNode {
  id: string;
  label?: string;
  type: ElementType;
  voltage?: VoltageLevel;
  position?: { x: number; y: number };
  metadata?: Record<string, string>;
}

export interface GraphEdge {
  id: string;
  from: string;
  to: string;
  type: ElementType;
  state?: SwitchState;
  metadata?: Record<string, string>;
}

export interface Equipment {
  id: string;
  type: ElementType;
  label?: string;
  confidence?: number;
  bbox?: [number, number, number, number];
}

export interface GraphModel {
  nodes: GraphNode[];
  edges: GraphEdge[];
  equipments: Equipment[];
  page: number;
  source_nodes: string[];
  load_nodes: string[];
  layout_size?: { width: number; height: number };
}

export interface SimulationRequest {
  states: Record<string, SwitchState>;
}

export interface SimulationResult {
  energized_nodes: string[];
  energized_edges: string[];
  flows: Record<string, number>;
  alerts: string[];
}
