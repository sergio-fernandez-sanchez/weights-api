from datetime import datetime, timedelta, date
from db.queries import (
    get_weight_on_date,
    update_weight,
    insert_weight,
    get_weights,
    get_phases,
    close_phase,
    insert_phase,
    close_calories,
    insert_calories,
    close_gym_log,
    insert_gym_log
)


def add_weight(user_id: int, new_weight: dict) -> str:
    """
    Actualiza el ultimo peso o inserta uno nuevo dependiendo de si ya hay un registro en el dia actual.
    """
    status = update_weight(user_id, new_weight["weight"]) if get_weight_on_date(user_id, datetime.now().date()) else insert_weight(user_id, new_weight["weight"])
    return status


def get_weights_filtered(user_id: int, mode: str, phase_start: str = None) -> list[dict]:
    """
    Devuelve pesos filtrados según el modo:
    - "all":   todos los registros
    - "week":  semana en curso (lunes a hoy)
    - "phase": desde el start_date de la fase activa
    - "month": último mes
    - "year":  último año
    """
    weights = get_weights(user_id)
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


def get_weights_with_phase(user_id: int) -> list[dict]:
    """
    Devuelve todos los registros de peso con el tipo de fase
    correspondiente a cada fecha.
    """
    weights_list = get_weights(user_id)
    phases_list  = get_phases(user_id)

    weights_with_phase = []
    for w in weights_list:
        phase_name = "unknown"

        for p in phases_list:
            start = p["start_date"]
            end   = p["end_date"] if p["end_date"] is not None else datetime.now().date()
            if start <= w["date"] < end:
                phase_name = p["phase_type"]
                break

        weights_with_phase.append({
            "date":       w["date"],
            "weight":     w["weight"],
            "phase_type": phase_name
        })
    return weights_with_phase


def update_phase(user_id: int, phase_data: dict) -> dict:
    """
    Cierra la fase activa con end_date = start_date_nueva - 1 día, e inicia una nueva.
    Si se proporciona start_date la usa como fecha de inicio, si no usa hoy.
    """
    start_date = phase_data.get("start_date") or datetime.now().date()
    end_date = start_date - timedelta(days=1)
    close_result = close_phase(user_id, end_date)
    insert_result = insert_phase(user_id, phase_data)
    return {"close": close_result, "insert": insert_result}


def update_calories(user_id: int, calories_data: dict) -> dict:
    """
    Cierra las calorías activas con end_date = ayer, e inicia un nuevo registro desde hoy.
    """
    close_result  = close_calories(user_id)
    insert_result = insert_calories(user_id, calories_data)
    return {"close": close_result, "insert": insert_result}


def update_gym_log(user_id: int, log_id: int, log_data: dict) -> dict:
    """
    Cierra el gym_log con el id indicado e inserta uno nuevo con los datos actualizados.
    """
    close_result  = close_gym_log(user_id, log_id, datetime.now().date())
    insert_result = insert_gym_log(user_id, log_data)
    return {"close": close_result, "insert": insert_result}