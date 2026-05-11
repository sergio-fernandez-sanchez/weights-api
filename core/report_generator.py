from datetime import datetime, timedelta
from db.queries import get_weights, get_phases, get_reports, get_calories, get_gym_logs


def fmt(d):
    return d.strftime("%d/%m/%y") if d else "—"


def volume(log):
    """Calcula el volumen de un log: peso * reps si hay reps, peso si no."""
    if log["weight"] and log["reps"]:
        return float(log["weight"]) * int(log["reps"])
    elif log["weight"]:
        return float(log["weight"])
    return None


def weekly_averages(weights_sorted):
    by_week = {}
    for w in weights_sorted:
        d = w["date"]
        monday = d - timedelta(days=d.weekday())
        if monday not in by_week:
            by_week[monday] = []
        by_week[monday].append(float(w["weight"]))
    result = []
    for monday in sorted(by_week.keys()):
        vals = by_week[monday]
        avg = sum(vals) / len(vals)
        week_end = monday + timedelta(days=6)
        result.append((monday, week_end, avg))
    return result


def calc_strength_by_phase(gym_logs, phases):
    results = {}
    for phase in phases:
        phase_start = phase["start_date"]
        phase_end   = phase["end_date"] or datetime.now().date()

        by_exercise = {}
        for log in gym_logs:
            if not log["weight"]:
                continue
            log_start = log["start_date"]
            log_end   = log["end_date"] or datetime.now().date()
            if log_start <= phase_end and log_end >= phase_start:
                eid = log["exercise_type_id"]
                if eid not in by_exercise:
                    by_exercise[eid] = {"name": log["name"], "logs": []}
                by_exercise[eid]["logs"].append(log)

        changes = []
        for eid, data in by_exercise.items():
            all_logs_exercise = sorted(
                [l for l in gym_logs if l["exercise_type_id"] == eid and l["weight"]],
                key=lambda l: l["start_date"]
            )
            before_phase = [l for l in all_logs_exercise if l["start_date"] < phase_start]
            during_phase = [l for l in all_logs_exercise if phase_start <= l["start_date"] <= phase_end]

            if not during_phase:
                continue

            last_during = during_phase[-1]

            if before_phase:
                base = before_phase[-1]
            elif len(during_phase) >= 2:
                base = during_phase[0]
            else:
                continue

            if base["id"] == last_during["id"]:
                continue

            vol_base    = volume(base)
            vol_current = volume(last_during)

            if not vol_base or not vol_current:
                continue

            pct = ((vol_current - vol_base) / vol_base) * 100
            changes.append({
                "name": data["name"],
                "pct": pct,
                "base": float(base["weight"]),
                "base_reps": base["reps"],
                "base_date": base["start_date"],
                "current": float(last_during["weight"]),
                "current_reps": last_during["reps"],
                "current_date": last_during["start_date"],
            })

        if changes:
            avg = sum(c["pct"] for c in changes) / len(changes)
            results[phase["id"]] = {"avg": avg, "exercises": changes}

    return results


def fmt_log(log_dict):
    """Formatea peso y reps de un log para mostrar en informe."""
    w = f"{log_dict['weight']:.1f}kg"
    r = f" x {log_dict['reps']} reps/serie" if log_dict.get("reps") else ""
    return f"{w}{r}"


def gym_section(gym_logs):
    lines = []
    by_exercise = {}
    for log in gym_logs:
        eid = log["exercise_type_id"]
        if eid not in by_exercise:
            by_exercise[eid] = {"name": log["name"], "logs": []}
        by_exercise[eid]["logs"].append(log)

    for eid, data in by_exercise.items():
        lines.append(f"  {data['name'].upper()}:")
        for log in sorted(data["logs"], key=lambda l: l["start_date"]):
            peso = f"{log['weight']} kg" if log["weight"] else "sin peso"
            reps = f" x {log['reps']} reps/serie" if log["reps"] else ""
            lines.append(f"    {fmt(log['start_date'])} -> {fmt(log['end_date'])}  |  {peso}{reps}")
        lines.append("")
    return lines


# ── Informe 1: Para IA (optimizado) ──────────────────────────────────────────

def generate_report(user_id: int) -> str:
    weights_data  = get_weights(user_id)
    phases_data   = get_phases(user_id)
    reports_data  = get_reports(user_id)
    calories_data = get_calories(user_id)
    gym_logs      = get_gym_logs(user_id)

    current_date   = datetime.now().strftime("%d/%m/%y")
    weights_sorted = sorted(weights_data, key=lambda w: w["date"])
    phases_sorted  = sorted(phases_data,  key=lambda p: p["start_date"])

    active_phase = next((p for p in phases_sorted if p["end_date"] is None), None)
    active_start = active_phase["start_date"] if active_phase else None

    strength_by_phase = calc_strength_by_phase(gym_logs, phases_sorted)

    r = []
    r.append("=" * 60)
    r.append("INFORME DE SEGUIMIENTO CORPORAL — RESUMEN PARA IA")
    r.append(f"Generado: {current_date}")
    r.append("=" * 60)
    r.append("")

    r.append("-- FASES --")
    for phase in phases_sorted:
        estado = "ACTIVA" if phase["end_date"] is None else "FINALIZADA"
        r.append(f" {fmt(phase['start_date'])} -> {fmt(phase['end_date'])}  |  {phase['phase_type'].upper()}  |  [{estado}]")
        if phase["id"] in strength_by_phase:
            s = strength_by_phase[phase["id"]]
            r.append(f"   Rendimiento gym: {s['avg']:+.1f}% media (volumen peso×reps)")
            for ex in s["exercises"]:
                base_str    = fmt_log({"weight": ex["base"],    "reps": ex["base_reps"]})
                current_str = fmt_log({"weight": ex["current"], "reps": ex["current_reps"]})
                r.append(f"     {ex['name']}: {fmt(ex['base_date'])} {base_str} -> {fmt(ex['current_date'])} {current_str}  ({ex['pct']:+.1f}%)")
        r.append("")

    r.append("-- PESOS --")
    if weights_sorted:
        r.append(f"  Primer registro: {fmt(weights_sorted[0]['date'])}  {weights_sorted[0]['weight']} kg")
        r.append(f"  Último registro:  {fmt(weights_sorted[-1]['date'])}  {weights_sorted[-1]['weight']} kg")

    r.append("")
    r.append("-- PROMEDIOS SEMANALES (fases pasadas) --")
    past_weights = [w for w in weights_sorted if not active_start or w["date"] < active_start]
    if past_weights:
        for monday, sunday, avg in weekly_averages(past_weights):
            r.append(f"  {fmt(monday)} - {fmt(sunday)}  ->  {avg:.2f} kg")
    else:
        r.append("  sin registros en fases pasadas")

    if active_start:
        r.append("")
        r.append(f"-- PESOS FASE ACTIVA (desde {fmt(active_start)}) --")
        for w in [w for w in weights_sorted if w["date"] >= active_start]:
            r.append(f"  {fmt(w['date'])}  ->  {w['weight']} kg")

    r.append("")
    r.append("-- HISTORIAL DE CALORÍAS --")
    calories_sorted = sorted(calories_data, key=lambda c: c["start_date"])
    if calories_sorted:
        for c in calories_sorted:
            estado = "ACTIVO" if c["end_date"] is None else "FINALIZADO"
            r.append(f"  {fmt(c['start_date'])} -> {fmt(c['end_date'])}  |  {c['calories']} kcal  |  [{estado}]")
    else:
        r.append("  sin registros")

    r.append("")
    r.append("-- HISTORIAL DE GYM --")
    r.extend(gym_section(gym_logs))

    r.append("-- MEDICIONES DEL NUTRICIONISTA --")
    for row in sorted(reports_data, key=lambda x: x["date"]):
        r.append(f"Fecha: {fmt(row['date'])}")
        r.append(f"  % Grasa: {row['body_fat_pct']}  |  M.M. Esq.: {row['skeletal_muscle_mass']}  |  M. Libre Grasa: {row['fat_free_mass']}")
        r.append(f"  Grasa visceral: {row['visceral_fat_index']}  |  Agua corporal: {row['total_body_water']}")
        if row['muscle_quality']:
            r.append(f"  Calidad muscular: {row['muscle_quality']}")
        r.append(f"  Tronco: {row['trunk_fat_kg']} kg / {row['trunk_fat_pct']}%")
        medidas = []
        for campo, label in [('neck_cm','Cuello'),('chest_cm','Pecho'),('bicep_cm','Bícep'),('hip_cm','Cadera'),('thigh_cm','Muslo')]:
            if row[campo]:
                medidas.append(f"{label}: {row[campo]} cm")
        if medidas:
            r.append(f"  Medidas: {' | '.join(medidas)}")
        r.append("")

    r.append("=" * 60)
    r.append("FIN DEL INFORME")
    r.append("=" * 60)
    return "\n".join(r)


# ── Informe 2: Datos en bruto ─────────────────────────────────────────────────

def generate_raw_report(user_id: int) -> str:
    weights_data  = get_weights(user_id)
    phases_data   = get_phases(user_id)
    reports_data  = get_reports(user_id)
    calories_data = get_calories(user_id)
    gym_logs      = get_gym_logs(user_id)

    current_date   = datetime.now().strftime("%d/%m/%y")
    weights_sorted = sorted(weights_data, key=lambda w: w["date"])
    phases_sorted  = sorted(phases_data,  key=lambda p: p["start_date"])
    weights_values = [float(w["weight"]) for w in weights_sorted]

    strength_by_phase = calc_strength_by_phase(gym_logs, phases_sorted)

    r = []
    r.append("=" * 60)
    r.append("INFORME COMPLETO — DATOS EN BRUTO")
    r.append(f"Generado: {current_date}")
    r.append("=" * 60)
    r.append("")

    r.append("-- FASES --")
    for phase in phases_sorted:
        estado = "ACTIVA" if phase["end_date"] is None else "FINALIZADA"
        r.append(f" {fmt(phase['start_date'])} -> {fmt(phase['end_date'])}  |  {phase['phase_type'].upper()}  |  [{estado}]")
        if phase["id"] in strength_by_phase:
            s = strength_by_phase[phase["id"]]
            r.append(f"   Rendimiento gym: {s['avg']:+.1f}% media (volumen peso×reps)")
            for ex in s["exercises"]:
                base_str    = fmt_log({"weight": ex["base"],    "reps": ex["base_reps"]})
                current_str = fmt_log({"weight": ex["current"], "reps": ex["current_reps"]})
                r.append(f"     {ex['name']}: {fmt(ex['base_date'])} {base_str} -> {fmt(ex['current_date'])} {current_str}  ({ex['pct']:+.1f}%)")
        r.append("")

    r.append("-- PESOS --")
    if weights_sorted:
        r.append(f"  Total registros: {len(weights_sorted)}")
        r.append(f"  Mínimo: {min(weights_values):.2f} kg  |  Máximo: {max(weights_values):.2f} kg")
    r.append("")
    r.append("-- HISTORIAL COMPLETO --")
    for w in weights_sorted:
        r.append(f"  {fmt(w['date'])}  ->  {w['weight']} kg")

    r.append("")
    r.append("-- HISTORIAL DE CALORÍAS --")
    calories_sorted = sorted(calories_data, key=lambda c: c["start_date"])
    if calories_sorted:
        for c in calories_sorted:
            estado = "ACTIVO" if c["end_date"] is None else "FINALIZADO"
            r.append(f"  {fmt(c['start_date'])} -> {fmt(c['end_date'])}  |  {c['calories']} kcal  |  [{estado}]")
    else:
        r.append("  sin registros")

    r.append("")
    r.append("-- HISTORIAL DE GYM --")
    r.extend(gym_section(gym_logs))

    r.append("-- MEDICIONES DEL NUTRICIONISTA --")
    for row in sorted(reports_data, key=lambda x: x["date"]):
        r.append(f"Fecha: {fmt(row['date'])}")
        r.append(f"  % Grasa corporal: {row['body_fat_pct']}")
        r.append(f"  Masa muscular esquelética (kg): {row['skeletal_muscle_mass']}")
        r.append(f"  Masa libre de grasa (kg): {row['fat_free_mass']}")
        r.append(f"  Índice grasa visceral: {row['visceral_fat_index']}")
        if row['muscle_quality']:
            r.append(f"  Calidad muscular: {row['muscle_quality']}")
        r.append(f"  Grasa tronco (kg): {row['trunk_fat_kg']}")
        r.append(f"  Grasa tronco (%): {row['trunk_fat_pct']}")
        r.append(f"  Agua corporal total (kg): {row['total_body_water']}")
        for campo, label in [('neck_cm','Cuello'),('chest_cm','Pecho'),('bicep_cm','Bícep'),('hip_cm','Cadera'),('thigh_cm','Muslo')]:
            if row[campo]:
                r.append(f"  {label} (cm): {row[campo]}")
        r.append("")

    r.append("=" * 60)
    r.append("FIN DEL INFORME")
    r.append("=" * 60)
    return "\n".join(r)