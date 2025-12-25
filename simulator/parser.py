from pathlib import Path
from typing import Dict, List


class SimulationTopology:
    """Representa uma topologia simulável a partir de um diagrama unifilar."""

    def __init__(self, buses: List[str], switches: List[Dict[str, str]]):
        self.buses = buses
        self.switches = switches

    @classmethod
    def from_pdf(cls, file_path: Path) -> "SimulationTopology":
        """
        Placeholder de extração: em um cenário real este método faria OCR ou leitura
        vetorial do PDF para identificar símbolos e conexões. Aqui retornamos uma
        topologia básica com barras e chaves de exemplo para permitir testes manuais.
        """
        buses = ["Fonte", "ALIM-01", "ALIM-02", "Carga A", "Carga B"]
        switches = [
            {"id": "CH-01", "from": "Fonte", "to": "ALIM-01", "state": "closed"},
            {"id": "CH-02", "from": "Fonte", "to": "ALIM-02", "state": "closed"},
            {"id": "CH-03", "from": "ALIM-01", "to": "Carga A", "state": "closed"},
            {"id": "CH-04", "from": "ALIM-02", "to": "Carga B", "state": "open"},
        ]
        return cls(buses=buses, switches=switches)

    def toggle(self, switch_id: str) -> None:
        for switch in self.switches:
            if switch["id"] == switch_id:
                switch["state"] = "closed" if switch["state"] == "open" else "open"
                break

    def energized_buses(self) -> List[str]:
        """
        Calcula barras energizadas assumindo que "Fonte" é sempre energizada.
        As chaves fechadas propagam energia para barras conectadas.
        """
        energized = {"Fonte"}
        changed = True
        while changed:
            changed = False
            for switch in self.switches:
                if switch["state"] == "closed":
                    if switch["from"] in energized and switch["to"] not in energized:
                        energized.add(switch["to"])
                        changed = True
                    elif switch["to"] in energized and switch["from"] not in energized:
                        energized.add(switch["from"])
                        changed = True
        return sorted(energized)
