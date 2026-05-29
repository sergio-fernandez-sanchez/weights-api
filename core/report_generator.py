import json
from datetime import datetime, timedelta
from db.queries import (
    get_weights, get_phases, get_calories, get_gym_logs,
    get_user_profile, get_weekly_reports,
    get_bioimpedance_reports, get_dexa_reports, get_body_measurements
)


def one_rm(weight, reps):
    if weight is None:
        return None
    if reps:
        return round(float(weight) * (1 + int(reps) / 30), 2)
    return round(float(weight), 2)


def iso(d):
    if d is None:
        return None
    if isinstance(d, str):
        return d.split('T')[0]
    return d.isoformat()


def toISO(date):
    return f"{date.year}-{str(date.month).zfill(2)}-{str(date.day).zfill(2)}"


def get_monday(date):
    return date - timedelta(days=date.weekday())


def get_phase_on_date(phases, date):
    for p in phases:
        start = p["start_date"]
        end = p["end_date"] or datetime.now().date()
        if start <= date <= end:
            return p["phase_type"]
    return None


def get_calories_on_date(calories_data, date):
    for c in calories_data:
        start = c["start_date"]
        end = c["end_date"] or datetime.now().date()
        if start <= date <= end:
            return c["calories"]
    return None


# ── INFORME PARA IA ──────────────────────────────────────────────────────────

def generate_report(user_id: int) -> str:
    weights_data    = sorted(get_weights(user_id),              key=lambda w: w["date"])
    phases_data     = sorted(get_phases(user_id),               key=lambda p: p["start_date"])
    calories_data   = sorted(get_calories(user_id),             key=lambda c: c["start_date"])
    gym_logs        = sorted(get_gym_logs(user_id),             key=lambda l: l["start_date"])
    weekly_reports  = sorted(get_weekly_reports(user_id),       key=lambda w: w["week_start"])
    bioimpedance    = sorted(get_bioimpedance_reports(user_id), key=lambda r: r["date"])
    dexa            = sorted(get_dexa_reports(user_id),         key=lambda r: r["date"])
    measurements    = sorted(get_body_measurements(user_id),    key=lambda r: r["date"])
    profile_data    = get_user_profile(user_id)
    today           = datetime.now().date()

    # ── notes ─────────────────────────────────────────────────────────────────
    notes = {
        "one_rm_formula":             "Epley: weight * (1 + reps / 30)",
        "null_values":                "null means no data available for that field or period",
        "weekly_report_null":         "null weekly_report means the user did not fill in that week's report",
        "daily_weights_availability": "daily_weights only available for the last 4 weeks, null for older weeks",
        "gym_strength_vs_exercises":  "phases.gym_strength is a summary of strength progress per phase; gym_exercises contains the full granular history",
        "calories_in_phases":         "calories list within each phase shows all calorie targets active during that phase period",
        "phases_during_period":       "calories in weekly_blocks shows the active calorie target for that specific week",
    }

    # ── profile ────────────────────────────────────────────────────────────────
    profile = None
    if profile_data:
        age = None
        if profile_data.get("birth_date"):
            bd = profile_data["birth_date"]
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        profile = {
            "name":        profile_data.get("name"),
            "age":         age,
            "sex":         profile_data.get("sex"),
            "height_cm":   float(profile_data["height_cm"]) if profile_data.get("height_cm") else None,
            "allergies":   profile_data.get("allergies"),
            "supplements": profile_data.get("supplements"),
        }

    # ── phases ─────────────────────────────────────────────────────────────────
    phases_out = []
    for phase in phases_data:
        phase_start = phase["start_date"]
        phase_end   = phase["end_date"] or today
        is_active   = phase["end_date"] is None
        days        = (phase_end - phase_start).days

        phase_weights = [w for w in weights_data if phase_start <= w["date"] <= phase_end]
        start_w = float(phase_weights[0]["weight"])  if phase_weights else None
        end_w   = float(phase_weights[-1]["weight"]) if phase_weights else None
        change  = round(end_w - start_w, 2) if start_w and end_w else None
        weekly_rate = None
        if len(phase_weights) >= 2:
            d = (phase_weights[-1]["date"] - phase_weights[0]["date"]).days
            if d > 0:
                weekly_rate = round((end_w - start_w) / d * 7, 3)

        cals_in_phase = []
        for c in calories_data:
            c_start = c["start_date"]
            c_end   = c["end_date"] or today
            if c_start < phase_end and c_end >= phase_start:
                cals_in_phase.append({
                    "start_date": iso(c_start),
                    "end_date":   iso(c["end_date"]),
                    "kcal":       c["calories"],
                })

        by_exercise = {}
        for log in gym_logs:
            eid = log["exercise_type_id"]
            if eid not in by_exercise:
                by_exercise[eid] = {"name": log["name"], "category": log["category"], "logs": []}
            by_exercise[eid]["logs"].append(log)

        gym_changes = []
        for eid, data in by_exercise.items():
            sorted_logs = sorted(data["logs"], key=lambda l: l["start_date"])
            logs_until_end = [l for l in sorted_logs if l["start_date"] <= phase_end and l["weight"]]
            if not logs_until_end:
                continue
            current = logs_until_end[-1]
            phase_history = [l for l in logs_until_end if l["start_date"] >= phase_start]
            before_phase  = [l for l in sorted_logs if l["start_date"] < phase_start and l["weight"]]
            base = None
            if len(phase_history) >= 2:
                base = phase_history[0]
            elif len(phase_history) == 1 and before_phase:
                base = before_phase[-1]
            if not base or base["id"] == current["id"]:
                continue
            rm_base = one_rm(base["weight"], base["reps"])
            rm_curr = one_rm(current["weight"], current["reps"])
            if not rm_base or not rm_curr:
                continue
            pct = round(((rm_curr - rm_base) / rm_base) * 100, 2)
            gym_changes.append({
                "name":              data["name"],
                "base":              {"date": iso(base["start_date"]),    "weight_kg": float(base["weight"]),    "reps": base["reps"],    "one_rm": rm_base},
                "current":           {"date": iso(current["start_date"]), "weight_kg": float(current["weight"]), "reps": current["reps"], "one_rm": rm_curr},
                "change_pct_one_rm": pct,
            })

        avg_strength = round(sum(g["change_pct_one_rm"] for g in gym_changes) / len(gym_changes), 2) if gym_changes else None

        phase_obj = {
            "type":       phase["phase_type"],
            "start_date": iso(phase_start),
            "end_date":   iso(phase["end_date"]),
            "active":     is_active,
            "days":       days,
            "weight_stats": {
                "start_weight_kg": start_w,
                "end_weight_kg":   end_w,
                "total_change_kg": change,
                "weekly_rate_kg":  weekly_rate,
            },
            "calories":     cals_in_phase or None,
            "gym_strength": {"avg_change_pct_one_rm": avg_strength, "exercises": gym_changes} if gym_changes else None,
        }
        if is_active:
            phase_obj["weight_goal_kg"] = float(phase["weight_goal"]) if phase["weight_goal"] else None
            phase_obj["date_goal"]      = iso(phase["date_goal"])

        phases_out.append(phase_obj)

    # ── weekly_blocks ──────────────────────────────────────────────────────────
    first_date   = weights_data[0]["date"] if weights_data else today - timedelta(days=365)
    first_monday = get_monday(first_date)
    cutoff_4w    = today - timedelta(weeks=4)
    weekly_reports_map = {w["week_start"]: w for w in weekly_reports}

    weekly_blocks = []
    current_monday = first_monday
    while current_monday <= today:
        week_end       = current_monday + timedelta(days=6)
        week_start_iso = toISO(current_monday)
        week_end_iso   = toISO(min(week_end, today))

        week_weights = [float(w["weight"]) for w in weights_data if current_monday <= w["date"] <= min(week_end, today)]
        avg_weight   = round(sum(week_weights) / len(week_weights), 2) if week_weights else None

        daily_weights = [
            {"date": iso(w["date"]), "weight_kg": float(w["weight"])}
            for w in weights_data if current_monday <= w["date"] <= min(week_end, today)
        ] if current_monday >= cutoff_4w else None

        phase_of_week = get_phase_on_date(phases_data, current_monday) or get_phase_on_date(phases_data, min(week_end, today))
        cals_of_week  = get_calories_on_date(calories_data, current_monday)

        wr = weekly_reports_map.get(current_monday)
        weekly_report = None
        if wr:
            weekly_report = {
                "training_days":      wr["training_days"],
                "avg_daily_steps":    wr["avg_daily_steps"],
                "alcohol_drinks":     float(wr["alcohol_drinks"])     if wr["alcohol_drinks"]     else None,
                "cigarettes_per_day": float(wr["cigarettes_per_day"]) if wr["cigarettes_per_day"] else None,
                "avg_water_liters":   float(wr["avg_water_liters"])   if wr["avg_water_liters"]   else None,
                "notes":              wr["notes"],
            }

        if avg_weight or weekly_report:
            weekly_blocks.append({
                "week_start":    week_start_iso,
                "week_end":      week_end_iso,
                "phase":         phase_of_week,
                "calories_kcal": cals_of_week,
                "avg_weight_kg": avg_weight,
                "daily_weights": daily_weights,
                "weekly_report": weekly_report,
            })

        current_monday += timedelta(weeks=1)

    # ── gym_exercises ──────────────────────────────────────────────────────────
    gym_by_exercise = {}
    for log in gym_logs:
        eid = log["exercise_type_id"]
        if eid not in gym_by_exercise:
            gym_by_exercise[eid] = {"name": log["name"], "category": log["category"], "history": []}
        gym_by_exercise[eid]["history"].append({
            "start_date": iso(log["start_date"]),
            "end_date":   iso(log["end_date"]),
            "active":     log["end_date"] is None,
            "weight_kg":  float(log["weight"]) if log["weight"] else None,
            "reps":       log["reps"],
            "one_rm":     one_rm(log["weight"], log["reps"]),
        })

    # ── bioimpedance_reports ───────────────────────────────────────────────────
    bioimpedance_out = []
    for r in bioimpedance:
        bioimpedance_out.append({
            "date":                 iso(r["date"]),
            "body_fat_pct":         float(r["body_fat_pct"])         if r["body_fat_pct"]         else None,
            "skeletal_muscle_mass": float(r["skeletal_muscle_mass"]) if r["skeletal_muscle_mass"] else None,
            "fat_free_mass":        float(r["fat_free_mass"])        if r["fat_free_mass"]        else None,
            "visceral_fat_index":   float(r["visceral_fat_index"])   if r["visceral_fat_index"]   else None,
            "muscle_quality":       float(r["muscle_quality"])       if r["muscle_quality"]       else None,
            "trunk_fat_kg":         float(r["trunk_fat_kg"])         if r["trunk_fat_kg"]         else None,
            "trunk_fat_pct":        float(r["trunk_fat_pct"])        if r["trunk_fat_pct"]        else None,
            "total_body_water":     float(r["total_body_water"])     if r["total_body_water"]     else None,
        })

    # ── dexa_reports ───────────────────────────────────────────────────────────
    dexa_out = []
    for r in dexa:
        dexa_out.append({
            "date":                 iso(r["date"]),
            "fat_mass_kg":          float(r["fat_mass_kg"])          if r["fat_mass_kg"]          else None,
            "lean_mass_kg":         float(r["lean_mass_kg"])         if r["lean_mass_kg"]         else None,
            "body_fat_pct":         float(r["body_fat_pct"])         if r["body_fat_pct"]         else None,
            "muscle_mass_kg":       float(r["muscle_mass_kg"])       if r["muscle_mass_kg"]       else None,
            "bone_mineral_density": float(r["bone_mineral_density"]) if r["bone_mineral_density"] else None,
            "visceral_fat_kg":      float(r["visceral_fat_kg"])      if r["visceral_fat_kg"]      else None,
        })

    # ── body_measurements ──────────────────────────────────────────────────────
    measurements_out = []
    for r in measurements:
        measurements_out.append({
            "date":         iso(r["date"]),
            "neck_cm":      float(r["neck_cm"])      if r["neck_cm"]      else None,
            "shoulders_cm": float(r["shoulders_cm"]) if r["shoulders_cm"] else None,
            "chest_cm":     float(r["chest_cm"])     if r["chest_cm"]     else None,
            "bicep_cm":     float(r["bicep_cm"])     if r["bicep_cm"]     else None,
            "waist_cm":     float(r["waist_cm"])     if r["waist_cm"]     else None,
            "hip_cm":       float(r["hip_cm"])       if r["hip_cm"]       else None,
            "thigh_cm":     float(r["thigh_cm"])     if r["thigh_cm"]     else None,
        })

    output = {
        "notes":                  notes,
        "profile":                profile,
        "phases":                 phases_out,
        "weekly_blocks":          weekly_blocks,
        "gym_exercises":          list(gym_by_exercise.values()),
        "bioimpedance_reports":   bioimpedance_out,
        "dexa_reports":           dexa_out,
        "body_measurements":      measurements_out,

    }

    return json.dumps(output, ensure_ascii=False, indent=2)


# ── INFORME EN BRUTO ─────────────────────────────────────────────────────────

def generate_raw_report(user_id: int) -> str:
    weights_data   = sorted(get_weights(user_id),              key=lambda w: w["date"])
    phases_data    = sorted(get_phases(user_id),               key=lambda p: p["start_date"])
    calories_data  = sorted(get_calories(user_id),             key=lambda c: c["start_date"])
    gym_logs       = sorted(get_gym_logs(user_id),             key=lambda l: l["start_date"])
    weekly_reports = sorted(get_weekly_reports(user_id),       key=lambda w: w["week_start"])
    bioimpedance   = sorted(get_bioimpedance_reports(user_id), key=lambda r: r["date"])
    dexa           = sorted(get_dexa_reports(user_id),         key=lambda r: r["date"])
    measurements   = sorted(get_body_measurements(user_id),    key=lambda r: r["date"])
    profile_data   = get_user_profile(user_id)

    output = {
        "generated_at": datetime.now().date().isoformat(),
        "profile": {
            "name":        profile_data.get("name")                                    if profile_data else None,
            "birth_date":  iso(profile_data["birth_date"])                             if profile_data and profile_data.get("birth_date") else None,
            "sex":         profile_data.get("sex")                                     if profile_data else None,
            "height_cm":   float(profile_data["height_cm"])                            if profile_data and profile_data.get("height_cm") else None,
            "allergies":   profile_data.get("allergies")                               if profile_data else None,
            "supplements": profile_data.get("supplements")                             if profile_data else None,
        },
        "phases": [
            {"id": p["id"], "phase_type": p["phase_type"], "start_date": iso(p["start_date"]), "end_date": iso(p["end_date"]), "active": p["end_date"] is None}
            for p in phases_data
        ],
        "weights": [
            {"id": w["id"], "date": iso(w["date"]), "weight_kg": float(w["weight"])}
            for w in weights_data
        ],
        "calories": [
            {"id": c["id"], "start_date": iso(c["start_date"]), "end_date": iso(c["end_date"]), "calories": c["calories"], "active": c["end_date"] is None}
            for c in calories_data
        ],
        "weekly_reports": [
            {
                "id": w["id"], "week_start": iso(w["week_start"]),
                "training_days": w["training_days"], "avg_daily_steps": w["avg_daily_steps"],
                "alcohol_drinks": float(w["alcohol_drinks"]) if w["alcohol_drinks"] else None,
                "cigarettes_per_day": float(w["cigarettes_per_day"]) if w["cigarettes_per_day"] else None,
                "avg_water_liters": float(w["avg_water_liters"]) if w["avg_water_liters"] else None,
                "notes": w["notes"],
            }
            for w in weekly_reports
        ],
        "gym_logs": [
            {
                "id": l["id"], "exercise_type_id": l["exercise_type_id"],
                "exercise_name": l["name"], "category": l["category"],
                "start_date": iso(l["start_date"]), "end_date": iso(l["end_date"]),
                "active": l["end_date"] is None,
                "weight_kg": float(l["weight"]) if l["weight"] else None,
                "reps": l["reps"],
            }
            for l in gym_logs
        ],
        "bioimpedance_reports": [
            {
                "id": r["id"], "date": iso(r["date"]),
                "body_fat_pct":         float(r["body_fat_pct"])         if r["body_fat_pct"]         else None,
                "skeletal_muscle_mass": float(r["skeletal_muscle_mass"]) if r["skeletal_muscle_mass"] else None,
                "fat_free_mass":        float(r["fat_free_mass"])        if r["fat_free_mass"]        else None,
                "visceral_fat_index":   float(r["visceral_fat_index"])   if r["visceral_fat_index"]   else None,
                "muscle_quality":       float(r["muscle_quality"])       if r["muscle_quality"]       else None,
                "trunk_fat_kg":         float(r["trunk_fat_kg"])         if r["trunk_fat_kg"]         else None,
                "trunk_fat_pct":        float(r["trunk_fat_pct"])        if r["trunk_fat_pct"]        else None,
                "total_body_water":     float(r["total_body_water"])     if r["total_body_water"]     else None,
            }
            for r in bioimpedance
        ],
        "dexa_reports": [
            {
                "id": r["id"], "date": iso(r["date"]),
                "fat_mass_kg":          float(r["fat_mass_kg"])          if r["fat_mass_kg"]          else None,
                "lean_mass_kg":         float(r["lean_mass_kg"])         if r["lean_mass_kg"]         else None,
                "body_fat_pct":         float(r["body_fat_pct"])         if r["body_fat_pct"]         else None,
                "muscle_mass_kg":       float(r["muscle_mass_kg"])       if r["muscle_mass_kg"]       else None,
                "bone_mineral_density": float(r["bone_mineral_density"]) if r["bone_mineral_density"] else None,
                "visceral_fat_kg":      float(r["visceral_fat_kg"])      if r["visceral_fat_kg"]      else None,
            }
            for r in dexa
        ],
        "body_measurements": [
            {
                "id": r["id"], "date": iso(r["date"]),
                "neck_cm":      float(r["neck_cm"])      if r["neck_cm"]      else None,
                "shoulders_cm": float(r["shoulders_cm"]) if r["shoulders_cm"] else None,
                "chest_cm":     float(r["chest_cm"])     if r["chest_cm"]     else None,
                "bicep_cm":     float(r["bicep_cm"])     if r["bicep_cm"]     else None,
                "waist_cm":     float(r["waist_cm"])     if r["waist_cm"]     else None,
                "hip_cm":       float(r["hip_cm"])       if r["hip_cm"]       else None,
                "thigh_cm":     float(r["thigh_cm"])     if r["thigh_cm"]     else None,
            }
            for r in measurements
        ],
    }

    return json.dumps(output, ensure_ascii=False, indent=2)