import os
from datetime import datetime, date
from core.csv_utils import read_csv, write_csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASES_CSV_PATH = os.path.join(BASE_DIR, "data", "phases.csv")

FIELD_NAMES = ["start_date", "end_date", "phase_type", "weight_goal", "date_goal"]


def update_phase(phase_data: dict) -> str:
    """
    Cierra la fase activa con la fecha de hoy e inicia una nueva.
    Devuelve "added" cuando se completa.
    """
    current_date = datetime.now().strftime("%d/%m/%y")
    csv_list = read_csv(PHASES_CSV_PATH)

    csv_list[-1]["end_date"] = current_date
    csv_list.append({
        "start_date": current_date,
        "end_date": "",
        "phase_type": phase_data["phase_type"],
        "weight_goal": phase_data["weight_goal"],
        "date_goal": phase_data["date_goal"]
    })

    write_csv(csv_list, PHASES_CSV_PATH, FIELD_NAMES)
    return "added"


def parse_phases() -> list[dict]:
    """
    Lee todos los registros de phases y los devuelve en una lista parseados.
    """
    csv_list = read_csv(PHASES_CSV_PATH)
    phases = []

    for csv_row in csv_list:
        try:
            phases.append({
                "start_date": datetime.strptime(csv_row["start_date"], "%d/%m/%y").date(),
                "end_date":   datetime.strptime(csv_row["end_date"], "%d/%m/%y").date() if csv_row["end_date"].strip() else None,
                "weight_goal": float(csv_row["weight_goal"]) if csv_row["weight_goal"] else None,
                "phase_type": csv_row["phase_type"],
                "date_goal":  datetime.strptime(csv_row["date_goal"], "%d/%m/%y").date() if csv_row["date_goal"].strip() else None,
            })
        except (ValueError, KeyError):
            continue
    return phases


def get_active_phase() -> dict | None:
    """
    Devuelve la fase activa (última sin end_date) parseada, o None si no hay datos.
    """
    phases = parse_phases()
    return phases[-1] if phases else None