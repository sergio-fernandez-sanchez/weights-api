import json
from datetime import datetime, timedelta
from db.queries import get_weights, get_phases, get_reports, get_calories, get_gym_logs


def one_rm(weight, reps):
    """1RM estimado (fórmula de Epley): peso * (1 + reps/30)."""
    if weight is None:
        return None
    if reps:
        return round(float(weight) * (1 + int(reps) / 30), 2)
    return float(weight)


def iso(d):
    return d.isoformat() if d else None


def weekly_averages(weights_list):
    """Agrupa pesos por semana (lunes a domingo) y devuelve lista con promedios."""
    by_week = {}
    for w in weights_list:
        d = w["date"]
        monday = d - timedelta(days=d.weekday())
        by_week.setdefault(monday, []).append(float(w["weight"]))

    result = []
    for monday in sorted(by_week.keys()):
        vals = by_week[monday]
        result.append({
            "week_start": iso(monday),
            "week_end":   iso(monday + timedelta(days=6)),
            "avg_weight": round(sum(vals) / len(vals), 2),
            "records":    len(vals),
        })
    return result


def get_phase_on_date(phases, date):
    for p in phases:
        start = p["start_date"]
        end = p["end_date"] or datetime.now().date()
        if start <= date <= end:
            return p["phase_type"]
    return None


# ── INFORME PARA IA ──────────────────────────────────────────────────────────

def generate_report(user_id: int) -> str:
    weights_data  = sorted(get_weights(user_id),  key=lambda w: w["date"])
    phases_data   = sorted(get_phases(user_id),   key=lambda p: p["start_date"])
    reports_data  = sorted(get_reports(user_id),  key=lambda r: r["date"])
    calories_data = sorted(get_calories(user_id), key=lambda c: c["start_date"])
    gym_logs      = sorted(get_gym_logs(user_id), key=lambda l: l["start_date"])

    today = datetime.now().date()
    active_phase = next((p for p in phases_data if p["end_date"] is None), None)
    active_start = active_phase["start_date"] if active_phase else None

    # ── Resumen ejecutivo ─────────────────────────────────────────────────────
    current_weight = float(weights_data[-1]["weight"]) if weights_data else None
    summary = {
        "generated_at": today.isoformat(),
        "current_weight_kg": current_weight,
        "active_phase": active_phase["phase_type"] if active_phase else None,
        "phase_start": iso(active_start),
        "days_in_phase": (today - active_start).days if active_start else None,
    }

    if active_phase:
        if active_phase["weight_goal"]:
            wg = float(active_phase["weight_goal"])
            summary["weight_goal_kg"] = wg
            summary["diff_to_goal_kg"] = round(wg - current_weight, 2) if current_weight else None
        if active_phase["date_goal"]:
            dg = active_phase["date_goal"]
            summary["date_goal"] = iso(dg)
            summary["days_to_goal"] = (dg - today).days

        # Tasa semanal de cambio durante la fase activa
        phase_weights = [w for w in weights_data if w["date"] >= active_start]
        if len(phase_weights) >= 2:
            first = float(phase_weights[0]["weight"])
            last  = float(phase_weights[-1]["weight"])
            days  = (phase_weights[-1]["date"] - phase_weights[0]["date"]).days
            if days > 0:
                weekly_rate = round((last - first) / days * 7, 3)
                summary["weekly_rate_kg"] = weekly_rate

    # ── Fases ─────────────────────────────────────────────────────────────────
    phases_out = []
    for phase in phases_data:
        phase_start = phase["start_date"]
        phase_end   = phase["end_date"] or today

        phase_weights = [w for w in weights_data if phase_start <= w["date"] <= phase_end]
        weights_in_phase = [float(w["weight"]) for w in phase_weights]

        is_active = phase["end_date"] is None
        days = (phase_end - phase_start).days

        # Cálculo de ritmo y cambio total
        weekly_rate = None
        weight_change = None
        if len(phase_weights) >= 2:
            first = float(phase_weights[0]["weight"])
            last  = float(phase_weights[-1]["weight"])
            d = (phase_weights[-1]["date"] - phase_weights[0]["date"]).days
            weight_change = round(last - first, 2)
            if d > 0:
                weekly_rate = round((last - first) / d * 7, 3)

        # Rendimiento gym en esta fase (1RM Epley)
        gym_progress = []
        ex_in_phase = {}
        for log in gym_logs:
            if not log["weight"]:
                continue
            log_start = log["start_date"]
            log_end = log["end_date"] or today
            if log_start <= phase_end and log_end >= phase_start:
                eid = log["exercise_type_id"]
                if eid not in ex_in_phase:
                    ex_in_phase[eid] = {"name": log["name"], "category": log["category"]}

        for eid, info in ex_in_phase.items():
            history = [l for l in gym_logs if l["exercise_type_id"] == eid and l["weight"]]
            current = history[-1] if history else None
            phase_history = [l for l in history if phase_start <= l["start_date"] <= phase_end]
            before_phase = [l for l in history if l["start_date"] < phase_start]

            base = None
            if len(phase_history) >= 2:
                base = phase_history[0]
            elif len(phase_history) == 1 and before_phase:
                base = before_phase[-1]

            if not base or not current or base["id"] == current["id"]:
                continue

            rm_base = one_rm(base["weight"], base["reps"])
            rm_curr = one_rm(current["weight"], current["reps"])
            if not rm_base or not rm_curr:
                continue

            pct = round(((rm_curr - rm_base) / rm_base) * 100, 2)
            gym_progress.append({
                "name": info["name"],
                "category": info["category"],
                "base":    {"date": iso(base["start_date"]),    "weight": float(base["weight"]),    "reps": base["reps"],    "one_rm": rm_base},
                "current": {"date": iso(current["start_date"]), "weight": float(current["weight"]), "reps": current["reps"], "one_rm": rm_curr},
                "change_pct_one_rm": pct,
            })

        avg_strength = round(sum(g["change_pct_one_rm"] for g in gym_progress) / len(gym_progress), 2) if gym_progress else None

        # Calorías que estuvieron activas en esta fase
        cals_in_phase = []
        for c in calories_data:
            c_start = c["start_date"]
            c_end = c["end_date"] or today
            if c_start <= phase_end and c_end >= phase_start:
                cals_in_phase.append(c["calories"])

        phase_obj = {
            "type": phase["phase_type"],
            "start_date": iso(phase_start),
            "end_date": iso(phase["end_date"]),
            "active": is_active,
            "days": days,
            "weight_stats": {
                "records": len(weights_in_phase),
                "start_weight_kg": round(weights_in_phase[0], 2) if weights_in_phase else None,
                "end_weight_kg":   round(weights_in_phase[-1], 2) if weights_in_phase else None,
                "min_kg": round(min(weights_in_phase), 2) if weights_in_phase else None,
                "max_kg": round(max(weights_in_phase), 2) if weights_in_phase else None,
                "avg_kg": round(sum(weights_in_phase) / len(weights_in_phase), 2) if weights_in_phase else None,
                "total_change_kg": weight_change,
                "weekly_rate_kg":  weekly_rate,
            },
            "calories_kcal_range": [min(cals_in_phase), max(cals_in_phase)] if cals_in_phase else None,
            "gym_strength": {
                "avg_change_pct_one_rm": avg_strength,
                "exercises": gym_progress,
            } if gym_progress else None,
        }

        # Solo añadir objetivos en la fase activa
        if is_active:
            phase_obj["weight_goal_kg"] = float(phase["weight_goal"]) if phase["weight_goal"] else None
            phase_obj["date_goal"] = iso(phase["date_goal"])

        phases_out.append(phase_obj)

    # ── Pesos: semanales en fases pasadas, últimos 31 días completos en la activa ──
    if active_start:
        past_weights   = [w for w in weights_data if w["date"] < active_start]
        active_weights = [w for w in weights_data if w["date"] >= active_start]
    else:
        past_weights   = weights_data
        active_weights = []

    cutoff_31 = today - timedelta(days=31)
    recent_31 = [w for w in active_weights if w["date"] >= cutoff_31]
    older_active = [w for w in active_weights if w["date"] < cutoff_31]

    weekly_past = weekly_averages(past_weights)
    weekly_active_older = weekly_averages(older_active)

    weights_section = {
        "weekly_past_phases":   weekly_past,
        "weekly_active_phase_older_than_31d": weekly_active_older,
        "last_31_days_full": [
            {
                "date": iso(w["date"]),
                "weight_kg": round(float(w["weight"]), 2),
                "phase": get_phase_on_date(phases_data, w["date"]),
            }
            for w in recent_31
        ],
    }

    # ── Calorías: cruzar con fases y cambio de peso del período ───────────────
    calories_out = []
    for c in calories_data:
        c_start = c["start_date"]
        c_end = c["end_date"] or today
        weights_period = [float(w["weight"]) for w in weights_data if c_start <= w["date"] <= c_end]
        weight_change_period = None
        if len(weights_period) >= 2:
            weight_change_period = round(weights_period[-1] - weights_period[0], 2)

        phases_overlap = []
        for p in phases_data:
            p_start = p["start_date"]
            p_end = p["end_date"] or today
            if p_start <= c_end and p_end >= c_start:
                phases_overlap.append(p["phase_type"])

        calories_out.append({
            "start_date": iso(c_start),
            "end_date":   iso(c["end_date"]),
            "calories":   c["calories"],
            "active":     c["end_date"] is None,
            "days":       (c_end - c_start).days,
            "phases":     list(dict.fromkeys(phases_overlap)),
            "weight_change_kg": weight_change_period,
        })

    # ── Gym: historial completo con 1RM ───────────────────────────────────────
    gym_by_exercise = {}
    for log in gym_logs:
        eid = log["exercise_type_id"]
        if eid not in gym_by_exercise:
            gym_by_exercise[eid] = {
                "id":       eid,
                "name":     log["name"],
                "category": log["category"],
                "history":  [],
            }
        gym_by_exercise[eid]["history"].append({
            "start_date": iso(log["start_date"]),
            "end_date":   iso(log["end_date"]),
            "active":     log["end_date"] is None,
            "weight_kg":  float(log["weight"]) if log["weight"] else None,
            "reps":       log["reps"],
            "one_rm":     one_rm(log["weight"], log["reps"]),
        })

    # ── Mediciones del nutricionista ──────────────────────────────────────────
    measurements = []
    for r in reports_data:
        measurements.append({
            "date": iso(r["date"]),
            "body_fat_pct":          float(r["body_fat_pct"])         if r["body_fat_pct"]         else None,
            "skeletal_muscle_mass":  float(r["skeletal_muscle_mass"]) if r["skeletal_muscle_mass"] else None,
            "fat_free_mass":         float(r["fat_free_mass"])        if r["fat_free_mass"]        else None,
            "visceral_fat_index":    float(r["visceral_fat_index"])   if r["visceral_fat_index"]   else None,
            "muscle_quality":        float(r["muscle_quality"])       if r["muscle_quality"]       else None,
            "trunk_fat_kg":          float(r["trunk_fat_kg"])         if r["trunk_fat_kg"]         else None,
            "trunk_fat_pct":         float(r["trunk_fat_pct"])        if r["trunk_fat_pct"]        else None,
            "total_body_water":      float(r["total_body_water"])     if r["total_body_water"]     else None,
            "neck_cm":               float(r["neck_cm"])               if r["neck_cm"]               else None,
            "chest_cm":              float(r["chest_cm"])              if r["chest_cm"]              else None,
            "bicep_cm":              float(r["bicep_cm"])              if r["bicep_cm"]              else None,
            "hip_cm":                float(r["hip_cm"])                if r["hip_cm"]                else None,
            "thigh_cm":              float(r["thigh_cm"])              if r["thigh_cm"]              else None,
        })

    # ── Resultado final ───────────────────────────────────────────────────────
    output = {
        "summary":              summary,
        "phases":               phases_out,
        "weights":              weights_section,
        "calories":             calories_out,
        "gym_exercises":        list(gym_by_exercise.values()),
        "nutritionist_reports": measurements,
        "notes": {
            "one_rm_formula":    "Epley: weight * (1 + reps / 30)",
            "weight_unit":       "kg",
            "rate_unit":         "kg/week",
            "data_organization": "Past phases use weekly averages; active phase uses weekly averages for data older than 31 days and daily records for the last 31 days.",
        },
    }

    return json.dumps(output, ensure_ascii=False, indent=2)


# ── INFORME EN BRUTO ─────────────────────────────────────────────────────────

def generate_raw_report(user_id: int) -> str:
    weights_data  = sorted(get_weights(user_id),  key=lambda w: w["date"])
    phases_data   = sorted(get_phases(user_id),   key=lambda p: p["start_date"])
    reports_data  = sorted(get_reports(user_id),  key=lambda r: r["date"])
    calories_data = sorted(get_calories(user_id), key=lambda c: c["start_date"])
    gym_logs      = sorted(get_gym_logs(user_id), key=lambda l: l["start_date"])

    output = {
        "generated_at": datetime.now().date().isoformat(),
        "phases": [
            {
                "id":         p["id"],
                "phase_type": p["phase_type"],
                "start_date": iso(p["start_date"]),
                "end_date":   iso(p["end_date"]),
                "active":     p["end_date"] is None,
            }
            for p in phases_data
        ],
        "weights": [
            {
                "id":        w["id"],
                "date":      iso(w["date"]),
                "weight_kg": float(w["weight"]),
            }
            for w in weights_data
        ],
        "calories": [
            {
                "id":         c["id"],
                "start_date": iso(c["start_date"]),
                "end_date":   iso(c["end_date"]),
                "calories":   c["calories"],
                "active":     c["end_date"] is None,
            }
            for c in calories_data
        ],
        "gym_logs": [
            {
                "id":               l["id"],
                "exercise_type_id": l["exercise_type_id"],
                "exercise_name":    l["name"],
                "category":         l["category"],
                "start_date":       iso(l["start_date"]),
                "end_date":         iso(l["end_date"]),
                "active":           l["end_date"] is None,
                "weight_kg":        float(l["weight"]) if l["weight"] else None,
                "reps":             l["reps"],
            }
            for l in gym_logs
        ],
        "nutritionist_reports": [
            {
                "id":                   r["id"],
                "date":                 iso(r["date"]),
                "body_fat_pct":         float(r["body_fat_pct"])         if r["body_fat_pct"]         else None,
                "skeletal_muscle_mass": float(r["skeletal_muscle_mass"]) if r["skeletal_muscle_mass"] else None,
                "fat_free_mass":        float(r["fat_free_mass"])        if r["fat_free_mass"]        else None,
                "visceral_fat_index":   float(r["visceral_fat_index"])   if r["visceral_fat_index"]   else None,
                "muscle_quality":       float(r["muscle_quality"])       if r["muscle_quality"]       else None,
                "trunk_fat_kg":         float(r["trunk_fat_kg"])         if r["trunk_fat_kg"]         else None,
                "trunk_fat_pct":        float(r["trunk_fat_pct"])        if r["trunk_fat_pct"]        else None,
                "total_body_water":     float(r["total_body_water"])     if r["total_body_water"]     else None,
                "neck_cm":              float(r["neck_cm"])               if r["neck_cm"]               else None,
                "chest_cm":             float(r["chest_cm"])              if r["chest_cm"]              else None,
                "bicep_cm":             float(r["bicep_cm"])              if r["bicep_cm"]              else None,
                "hip_cm":               float(r["hip_cm"])                if r["hip_cm"]                else None,
                "thigh_cm":             float(r["thigh_cm"])              if r["thigh_cm"]              else None,
            }
            for r in reports_data
        ],
    }

    return json.dumps(output, ensure_ascii=False, indent=2)