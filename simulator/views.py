from pathlib import Path
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import DiagramUploadForm
from .parser import SimulationTopology


STORAGE_ALIAS = 'diagram'


def _load_topology_from_session(request: HttpRequest) -> SimulationTopology | None:
    data = request.session.get('topology')
    if not data:
        return None
    return SimulationTopology(buses=data.get('buses', []), switches=data.get('switches', []))


def _persist_topology(request: HttpRequest, topology: SimulationTopology) -> None:
    request.session['topology'] = {
        'buses': topology.buses,
        'switches': topology.switches,
    }
    request.session.modified = True


def diagram_upload_view(request: HttpRequest) -> HttpResponse:
    topology = _load_topology_from_session(request)
    energized = topology.energized_buses() if topology else []

    if request.method == 'POST':
        form = DiagramUploadForm(request.POST, request.FILES)
        if form.is_valid():
            diagram_file = form.cleaned_data['diagram']
            storage = FileSystemStorage()
            filename = storage.save(diagram_file.name, diagram_file)
            saved_path = Path(storage.location) / filename
            topology = SimulationTopology.from_pdf(saved_path)
            _persist_topology(request, topology)
            energized = topology.energized_buses()
        else:
            return HttpResponseBadRequest("Arquivo inválido.")
    else:
        form = DiagramUploadForm()

    return render(
        request,
        'simulator/diagram.html',
        {
            'form': form,
            'topology': topology,
            'energized': energized,
        },
    )


def toggle_switch_view(request: HttpRequest, switch_id: str) -> HttpResponse:
    topology = _load_topology_from_session(request)
    if not topology:
        return redirect(reverse('diagram_upload'))

    topology.toggle(switch_id)
    _persist_topology(request, topology)
    return redirect(reverse('diagram_upload'))
