import panzoom from "panzoom";
import { GraphEdge, GraphModel, SimulationResult, SwitchState } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d")!;
const app = document.getElementById("app")!;

const sidebar = document.createElement("div");
sidebar.className = "sidebar";
const canvasWrapper = document.createElement("div");
canvasWrapper.className = "canvas-wrapper";
canvasWrapper.appendChild(canvas);
app.appendChild(sidebar);
app.appendChild(canvasWrapper);

canvas.width = window.innerWidth - 320;
canvas.height = window.innerHeight;

let model: GraphModel | null = null;
let simResult: SimulationResult | null = null;
let switchStates: Record<string, SwitchState> = {};
const log: string[] = [];

function logEvent(msg: string) {
  const timestamp = new Date().toLocaleTimeString();
  log.unshift(`[${timestamp}] ${msg}`);
  renderSidebar();
}

async function loadModel() {
  const res = await fetch(`${API_BASE}/projects/mock/model`);
  model = await res.json();
  renderSidebar();
  renderCanvas();
  await runSimulation();
}

function colorForEdge(edge: GraphEdge): string {
  if (!simResult) return "#94a3b8";
  const energized = simResult.energized_edges.includes(edge.id);
  if (edge.type === "switch") {
    const state = switchStates[edge.id] ?? edge.state ?? "open";
    if (state === "open") return "#f97316";
  }
  return energized ? "#22c55e" : "#94a3b8";
}

function nodeById(id: string) {
  return model?.nodes.find((n) => n.id === id);
}

function drawEdge(edge: GraphEdge) {
  const from = nodeById(edge.from);
  const to = nodeById(edge.to);
  if (!from || !to) return;
  ctx.beginPath();
  ctx.lineWidth = edge.type === "bus" ? 6 : 3;
  ctx.strokeStyle = colorForEdge(edge);
  ctx.moveTo(from.position?.x ?? 0, from.position?.y ?? 0);
  ctx.lineTo(to.position?.x ?? 0, to.position?.y ?? 0);
  ctx.stroke();
  if (edge.type === "switch") {
    ctx.save();
    ctx.strokeStyle = "#0f172a";
    ctx.fillStyle = ctx.strokeStyle;
    const midX = ((from.position?.x ?? 0) + (to.position?.x ?? 0)) / 2;
    const midY = ((from.position?.y ?? 0) + (to.position?.y ?? 0)) / 2;
    ctx.beginPath();
    ctx.arc(midX, midY, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

function drawNode(id: string, label?: string, type?: string) {
  const node = nodeById(id);
  if (!node || !node.position) return;
  const energized = simResult?.energized_nodes.includes(id);
  ctx.beginPath();
  ctx.fillStyle = energized ? "#22c55e" : "#1e293b";
  ctx.strokeStyle = "#0f172a";
  ctx.lineWidth = 2;
  ctx.arc(node.position.x, node.position.y, 10, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  if (label) {
    ctx.fillStyle = "#0f172a";
    ctx.font = "12px Inter";
    ctx.fillText(label, node.position.x + 12, node.position.y - 12);
  }
  if (type === "source") {
    ctx.beginPath();
    ctx.strokeStyle = "#eab308";
    ctx.arc(node.position.x, node.position.y, 14, 0, Math.PI * 2);
    ctx.stroke();
  }
}

function renderCanvas() {
  if (!model) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  model.edges.forEach(drawEdge);
  model.nodes.forEach((node) => drawNode(node.id, node.label, node.type));
}

async function runSimulation() {
  if (!model) return;
  const res = await fetch(`${API_BASE}/projects/mock/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ states: switchStates }),
  });
  simResult = await res.json();
  renderCanvas();
  renderSidebar();
}

function toggleSwitch(edgeId: string) {
  const edge = model?.edges.find((e) => e.id === edgeId);
  if (!edge) return;
  const current = switchStates[edgeId] ?? edge.state ?? "open";
  const next = current === "open" ? "closed" : "open";
  switchStates[edgeId] = next as SwitchState;
  logEvent(`Chave ${edgeId} → ${next}`);
  runSimulation();
}

function renderSidebar() {
  if (!model) return;
  sidebar.innerHTML = ``;
  const header = document.createElement("div");
  const title = document.createElement("h1");
  title.textContent = "Simulador";
  header.appendChild(title);
  sidebar.appendChild(header);

  const toolbar = document.createElement("div");
  toolbar.className = "toolbar";
  const refreshBtn = document.createElement("button");
  refreshBtn.textContent = "Reset";
  refreshBtn.onclick = () => {
    switchStates = {};
    logEvent("Reset do estado das chaves");
    runSimulation();
  };
  const exportBtn = document.createElement("button");
  exportBtn.className = "secondary";
  exportBtn.textContent = "Exportar JSON";
  exportBtn.onclick = () => {
    const dataStr = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(model, null, 2)
    )}`;
    const dl = document.createElement("a");
    dl.href = dataStr;
    dl.download = "modelo.json";
    dl.click();
  };
  toolbar.append(refreshBtn, exportBtn);
  sidebar.appendChild(toolbar);

  const equipmentTitle = document.createElement("h2");
  equipmentTitle.textContent = "Equipamentos";
  sidebar.appendChild(equipmentTitle);
  model.equipments.forEach((eq) => {
    const card = document.createElement("div");
    card.className = "equipment";
    const title = document.createElement("div");
    title.textContent = `${eq.label ?? eq.id} (${eq.type})`;
    card.appendChild(title);
    if (eq.type === "switch") {
      const badge = document.createElement("span");
      badge.className = "badge yellow";
      const state = switchStates[eq.id] ?? model?.edges.find((e) => e.id === eq.id)?.state ?? "open";
      badge.textContent = state === "closed" ? "FECHADA" : "ABERTA";
      badge.style.marginLeft = "8px";
      card.appendChild(badge);
      card.style.cursor = "pointer";
      card.onclick = () => toggleSwitch(eq.id);
    }
    if (typeof eq.confidence === "number") {
      const conf = document.createElement("div");
      conf.textContent = `confiança ${(eq.confidence * 100).toFixed(0)}%`;
      conf.style.opacity = "0.8";
      conf.style.fontSize = "12px";
      card.appendChild(conf);
    }
    sidebar.appendChild(card);
  });

  const alertsTitle = document.createElement("h2");
  alertsTitle.textContent = "Alertas";
  sidebar.appendChild(alertsTitle);
  const alertList = document.createElement("div");
  if (simResult?.alerts.length) {
    simResult.alerts.forEach((a) => {
      const item = document.createElement("div");
      item.className = "badge red";
      item.style.display = "inline-block";
      item.style.marginRight = "6px";
      item.textContent = a;
      alertList.appendChild(item);
    });
  } else {
    alertList.textContent = "Nenhum alerta";
  }
  sidebar.appendChild(alertList);

  const logTitle = document.createElement("h2");
  logTitle.textContent = "Log";
  sidebar.appendChild(logTitle);
  const logView = document.createElement("div");
  logView.className = "log";
  log.slice(0, 15).forEach((entry) => {
    const line = document.createElement("div");
    line.className = "log-entry";
    line.textContent = entry;
    logView.appendChild(line);
  });
  sidebar.appendChild(logView);
}

function setupPanZoom() {
  panzoom(canvas, { smoothScroll: false });
  canvas.addEventListener("click", (ev) => {
    if (!model) return;
    const rect = canvas.getBoundingClientRect();
    const x = (ev.clientX - rect.left) * (canvas.width / rect.width);
    const y = (ev.clientY - rect.top) * (canvas.height / rect.height);
    const hit = model.edges.find((edge) => {
      if (edge.type !== "switch") return false;
      const from = nodeById(edge.from)?.position;
      const to = nodeById(edge.to)?.position;
      if (!from || !to) return false;
      const midX = (from.x + to.x) / 2;
      const midY = (from.y + to.y) / 2;
      return Math.hypot(midX - x, midY - y) < 12;
    });
    if (hit) {
      toggleSwitch(hit.id);
    }
  });
}

loadModel();
setupPanZoom();
