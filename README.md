# Interpretação de diagramas unifilares → Simulador de subestação

Este repositório contém um protótipo completo que transforma um PDF de diagrama unifilar em um grafo elétrico e disponibiliza um simulador interativo de energização/fluxo. Inclui backend (FastAPI) com pipeline mock de detecção e frontend (Vite + TS) com canvas manipulável.

## Estrutura
- `backend/`: API FastAPI, modelos Pydantic e motor de simulação.
- `frontend/`: Vite (TypeScript) para o canvas interativo.
- `docs/`: arquitetura detalhada, pipeline e limitações.
- `examples/`: JSON de exemplo do grafo/layout.

## Como rodar
### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
A interface espera o backend em `http://localhost:8000` e usa o modelo mock exposto em `/projects/mock/model`.

## Endpoints principais
- `POST /upload`: cria job de interpretação do PDF.
- `GET /projects/{id}/status`: progresso do job.
- `GET /projects/{id}/model`: retorna grafo e layout detectados.
- `POST /projects/{id}/simulate`: roda simulação lógica com estados de chave fornecidos.
- `GET /projects/mock/model`: modelo pronto para demonstração.

## Testes
```bash
pytest backend/tests
```
