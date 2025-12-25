# Arquitetura "PDF → Grafo elétrico → Simulador"

## Visão geral
O sistema recebe um PDF de diagrama unifilar, extrai informação vetorial ou rasterizada e transforma em um grafo elétrico enriquecido (nós, arestas e metadados). O mesmo grafo alimenta a reconstrução gráfica (canvas) e o motor lógico de energização/fluxo. A aplicação foi dividida em backend (FastAPI) e frontend (HTML/JS), com APIs REST e modelo de dados consistente em Pydantic e TypeScript.

### Componentes principais
- **Ingestão de PDF** (backend): upload, contagem de páginas, criação de job assíncrono e pipeline de interpretação.
- **Pipeline de interpretação**: tentativa vetorial → fallback raster (OpenCV) → detecção geométrica/simbólica → OCR → fusão em grafo elétrico + layout.
- **Motor de simulação**: resolve conectividade, energização, detecção de paralelismo de fontes e fluxo lógico.
- **Frontend**: canvas interativo com pan/zoom, seleção de página, edição manual (arrastar, renomear, trocar tipo), painel de equipamentos e simulador.
- **Armazenamento**: mock em memória para jobs; preparado para persistência futura (S3/DB). Exportação JSON do modelo é suportada.

## Pipeline detalhado
1. **Upload & pré-processamento**: usuário envia PDF e escolhe página. Backend registra job, tenta extrair vetor (pdfplumber) e, se a camada vetorial for vazia, rasteriza com `pdf2image` (300–600 dpi). Progresso é exposto pelo endpoint `/status`.
2. **Extração vetorial**: para cada página, capturar linhas, curvas e textos; normalizar coordenadas e agrupar por camada/espessura para identificar barramentos.
3. **Fallback raster**: imagem passa por filtro adaptativo; usar Hough transform para linhas e contornos; agrupar endpoints próximos com “snap” e criar nós iniciais.
4. **Detecção de símbolos**: matching por templates (SVG/PNG) ou modelo leve (YOLO/DETR). Cada símbolo é ancorado na linha mais próxima e vira um equipamento (switch/trafo/etc.).
5. **OCR e rótulos**: Tesseract/TrOCR para textos; associação por distância + alinhamento (mesma horizontal/vertical). Rótulos são guardados em `metadata` e em `Equipment`.
6. **Geração do grafo elétrico**: nós = junções, terminais de equipamentos e barramentos; arestas = segmentos; switches ganham `state`; transformadores conectam níveis de tensão distintos.
7. **Layout/canvas**: coordenadas são normalizadas para o canvas; há opção de “auto-limpeza” (grid + ortogonalização). Editor manual permite mover nós, recasar conexões, definir tipo e estado.
8. **Simulação**: motor percorre grafo fechado para energização a partir de fontes, marca caminhos ativos até cargas, calcula fluxo relativo (1.0 = presente) e sinaliza backfeed.

## Pseudocódigo do pipeline
```pseudo
function interpret_pdf(pdf_path, page):
    layer = extract_vector_layer(pdf_path, page)
    if layer.is_empty():
        bitmap = rasterize(pdf_path, page, dpi=400)
        segments = detect_segments_hough(bitmap)
    else:
        segments = parse_vector_paths(layer)

    nodes = snap_and_merge_endpoints(segments)
    junctions = detect_junctions(nodes, segments)

    symbols = detect_symbols(layer or bitmap)
    texts = ocr_text(layer or bitmap)
    label_map = associate_labels(symbols, texts)

    graph = build_graph(nodes, segments, symbols, label_map)
    graph = infer_switch_states(graph)
    graph = normalize_layout(graph)
    return graph
```

## Modelo de dados
- **Pydantic**: `GraphModel`, `GraphNode`, `GraphEdge`, `Equipment`, `SimulationResult`, `SimulationRequest` (ver `backend/models.py`).
- **TypeScript** (frontend/types.ts): espelha os mesmos campos para integração segura na UI.
- **Export JSON**: exemplo completo em `examples/sample_model.json` (serviço `/projects/mock/model`).

## Motor de simulação
Regras implementadas em `backend/simulation.py`:
- Fonte energiza o nó onde está conectada.
- Arestas conduzem se não forem chave aberta; transformadores conduzem logicamente (sem cálculo de tap) e conectam níveis distintos.
- Nó é energizado se existir caminho fechado a partir de uma fonte.
- Fluxo relativo é marcado (1.0) quando uma aresta energizada conecta dois nós energizados.
- Alerta de paralelo de fontes quando duas fontes estão conectadas pelo mesmo subgrafo fechado.

## Telas (UX)
1. **Upload**: PDF + seletor de página → POST `/upload` e pooling em `/status`.
2. **Preview**: overlay com bounding boxes e confiança; usuário pode corrigir tipo/label.
3. **Simulador**: canvas com pan/zoom, clique em chave para abrir/fechar, painel lateral com lista de equipamentos, estados e alertas, log de manobras, botões de desfazer/refazer/reset/exportar JSON.
4. **Editor**: modo para arrastar nós, refazer conexões e editar metadados manualmente.

## Limitações e próximos passos
- Detecção de símbolos usa mock; necessidade de dataset anotado e treinamento de YOLO/DETR + augmentations.
- OCR pode falhar em diagrama borrado; combinar visões multi-escala e correção ortográfica de nomes de bays/feeds.
- Não há cálculo de carga/curto-circuito; apenas lógica binária de energização.
- Persistência está em memória; para produção usar banco (PostgreSQL) e armazenamento de arquivos (S3/minio).
- Multi-nível de tensão é representado, mas regras de isolamento poderiam incluir intertravamentos e checagem de tap de trafo.
- Jobs não são distribuídos; ideal usar fila (RQ/Celery) e workers com GPU para visão computacional.

## Execução local
Backend:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```
Frontend (estático):
```bash
cd frontend
npm install
npm run dev
```
A UI espera o backend em `http://localhost:8000` e consome o modelo mock (`/projects/mock/model`).
