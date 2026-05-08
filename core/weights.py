import os
from datetime import datetime, timedelta, date
from core.csv_utils import read_csv, write_csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_CSV_PATH = os.path.join(BASE_DIR, "data", "weights.csv")
PHASES_CSV_PATH = os.path.join(BASE_DIR, "data", "phases.csv")
FIELD_NAMES = ["date", "weight"]


def add_weight(new_weight: dict) -> str:
    """
    Añade o actualiza el peso de hoy en el CSV.
    Devuelve "updated" si ya había un registro hoy,
    o "added" si es una entrada nueva.
    """
    current_date = datetime.now().strftime("%d/%m/%y")
    weights_list = read_csv(WEIGHTS_CSV_PATH)

    if weights_list and weights_list[-1]["date"] == current_date:
        weights_list[-1]["weight"] = f"{new_weight['weight']:.2f}"
        result = "updated"
    else:
        weights_list.append({"date": current_date, "weight": f"{new_weight['weight']:.2f}"})
        result = "added"

    write_csv(weights_list, WEIGHTS_CSV_PATH, FIELD_NAMES)
    return result


def parse_weights() -> list[dict]:
    """
    Lee todos los registros de weights y los devuelve en una lista parseados.
    """
    csv_list = read_csv(WEIGHTS_CSV_PATH)
    weights = []
    for csv_row in csv_list:
        try:
            weights.append({
                "date":   datetime.strptime(csv_row["date"], "%d/%m/%y").date(),
                "weight": float(csv_row["weight"])
            })
        except (ValueError, KeyError):
            continue
    return weights


def get_weight_on_date(target_date: date) -> float | None:
    """
    Recibe una fecha y devuelve el peso guardado en esa fecha o None si no existe.
    """
    for csv_row in parse_weights():
        if csv_row["date"] == target_date:
            return csv_row["weight"]
    return None


def get_today_weight() -> float | None:
    """
    Devuelve el peso de hoy si existe, o None si no hay registro.
    """
    return get_weight_on_date(datetime.now().date())


def get_last_weight() -> dict | None:
    """
    Devuelve el último registro de weights parseado, o None si no hay datos.
    """
    weights = parse_weights()
    return weights[-1] if weights else None


def get_weights_filtered(mode: str, phase_start: str = None) -> list[dict]:
    """
    Devuelve pesos filtrados según el modo:
    - "all":   todos los registros
    - "week":  semana en curso (lunes a hoy)
    - "phase": desde el start_date de la fase activa
    - "month": último mes
    - "year":  último año
    """
    weights = parse_weights()
    today = datetime.now().date()

    if mode == "all":
        return weights
    elif mode == "week":
        start_of_week = today - timedelta(days=today.weekday())
        return [w for w in weights if w["date"] >= start_of_week]
    elif mode == "phase" and phase_start:
        start = datetime.strptime(phase_start, "%d/%m/%y").date()
        return [w for w in weights if w["date"] >= start]
    elif mode == "month":
        cutoff = today - timedelta(days=30)
        return [w for w in weights if w["date"] >= cutoff]
    elif mode == "year":
        cutoff = today - timedelta(days=365)
        return [w for w in weights if w["date"] >= cutoff]
    return weights


def get_weights_with_phase() -> list[dict]:
    """
    Devuelve todos los registros de peso con el tipo de fase
    correspondiente a cada fecha.
    """
    weights_list = parse_weights()
    phases_raw   = read_csv(PHASES_CSV_PATH)

    weights_with_phase = []
    for w in weights_list:
        phase_name = "unknown"

        for p in phases_raw:
            try:
                start = datetime.strptime(p["start_date"], "%d/%m/%y").date()
                end = datetime.strptime(p["end_date"], "%d/%m/%y").date() if p["end_date"].strip() else datetime.now().date()
                if start <= w["date"] < end:
                    phase_name = p["phase_type"]
                    break
            except (ValueError, KeyError):
                continue

        weights_with_phase.append({
            "date":       w["date"],
            "weight":     w["weight"],
            "phase_type": phase_name
        })
    return weights_with_phase