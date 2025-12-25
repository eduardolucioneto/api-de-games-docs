import shutil
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models import (
    GraphModel,
    ProjectSummary,
    SimulationRequest,
    SimulationResult,
    UploadResponse,
)
from .processing import extract_page_count, job_store, process_pdf
from .simulation import SimulationEngine
from .sample_data import SAMPLE_MODEL

app = FastAPI(title="Substation Diagram Interpreter", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("/tmp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), page: int = 0):
    pdf_path = UPLOAD_DIR / file.filename
    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    page_count = extract_page_count(pdf_path)
    job_id = job_store.create_job(file.filename, page_count)
    background_tasks.add_task(process_pdf, job_id, pdf_path, page)
    project = ProjectSummary(id=job_id, filename=file.filename, status="queued", page_count=page_count)
    return UploadResponse(project=project)


@app.get("/projects/{project_id}/status")
async def status(project_id: str):
    payload = job_store.get(project_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    status, _ = payload
    return status


@app.get("/projects/{project_id}/model", response_model=GraphModel)
async def get_model(project_id: str):
    payload = job_store.get(project_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    status, model = payload
    if model is None:
        raise HTTPException(status_code=202, detail="Processando")
    return model


@app.post("/projects/{project_id}/simulate", response_model=SimulationResult)
async def simulate(project_id: str, req: SimulationRequest):
    payload = job_store.get(project_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    _, model = payload
    if model is None:
        raise HTTPException(status_code=202, detail="Processando")
    engine = SimulationEngine(model)
    return engine.run(req.states)


@app.get("/projects/mock/model", response_model=GraphModel)
async def mock_model():
    return SAMPLE_MODEL


@app.post("/projects/mock/simulate", response_model=SimulationResult)
async def mock_simulate(req: SimulationRequest):
    engine = SimulationEngine(SAMPLE_MODEL)
    return engine.run(req.states)


app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / "examples"), name="static")
