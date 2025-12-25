"""PDF processing and interpretation pipeline (simplified mock implementation)."""
from pathlib import Path
from typing import Dict, Tuple
import uuid

import pdfplumber

from .models import GraphModel, ProcessStatus
from .sample_data import SAMPLE_MODEL


class JobStore:
    def __init__(self):
        self.jobs: Dict[str, Tuple[ProcessStatus, GraphModel]] = {}

    def create_job(self, filename: str, pages: int) -> str:
        job_id = str(uuid.uuid4())
        status = ProcessStatus(status="queued", progress=0.05, message="Fila criada")
        self.jobs[job_id] = (status, None)
        return job_id

    def update(self, job_id: str, status: ProcessStatus, model: GraphModel = None) -> None:
        self.jobs[job_id] = (status, model)

    def get(self, job_id: str) -> Tuple[ProcessStatus, GraphModel]:
        return self.jobs.get(job_id)


job_store = JobStore()


def extract_page_count(pdf_path: Path) -> int:
    with pdfplumber.open(str(pdf_path)) as pdf:
        return len(pdf.pages)


def process_pdf(job_id: str, pdf_path: Path, page: int = 0) -> None:
    # Mock pipeline: populate sample model but mimic stages.
    stages = [
        ("extraindo vetor/bitmap", 0.2),
        ("detectando linhas e junções", 0.4),
        ("detectando símbolos e textos", 0.6),
        ("gerando grafo elétrico", 0.8),
        ("otimizando layout", 0.95),
    ]
    for message, progress in stages:
        job_store.update(job_id, ProcessStatus(status="running", progress=progress, message=message))
    model = SAMPLE_MODEL.copy()
    model.page = page
    job_store.update(
        job_id,
        ProcessStatus(status="succeeded", progress=1.0, message="Processamento concluído"),
        model,
    )
