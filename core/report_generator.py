from datetime import datetime
from db.queries import get_weights, get_phases, get_reports


def generate_report(user_id: int) -> str:

    weights_data = get_weights(user_id)
    reports_data = get_reports(user_id)
    phases_data  = get_phases(user_id)

    def fmt(d):
        """Formatea un objeto date o None a string dd/mm/yy."""
        return d.strftime("%d/%m/%y") if d else "—"

    current_date = datetime.now().strftime("%d/%m/%y")
    report = []
    report.append("=" * 60)
    report.append("INFORME COMPLETO DE SEGUIMIENTO CORPORAL")
    report.append(f"Generado: {current_date}")
    report.append("=" * 60)
    report.append("")

    # ── Fases ─────────────────────────────────────────────────────────────────
    report.append("-- FASES --")
    for phase in phases_data:
        estado = "ACTIVA" if phase["end_date"] is None else "FINALIZADA"
        report.append(
            f" {fmt(phase['start_date'])} -> {fmt(phase['end_date'])}"
            f"  |  {phase['phase_type'].upper()}"
            f"  |  Objetivo: {phase['weight_goal']} antes del {fmt(phase['date_goal'])}"
            f"  |  [{estado}]\n"
        )

    # ── Pesos ─────────────────────────────────────────────────────────────────
    weights_sorted = sorted(weights_data, key=lambda w: w["date"])
    weights_values = [float(w["weight"]) for w in weights_sorted]

    report.append("-- PESOS --")
    if weights_sorted:
        report.append(f"  Total de registros: {len(weights_sorted)}")
        report.append(f"  Primer registro: {fmt(weights_sorted[0]['date'])}  {weights_sorted[0]['weight']} kg")
        report.append(f"  Último registro:  {fmt(weights_sorted[-1]['date'])}  {weights_sorted[-1]['weight']} kg")
        report.append(
            f"  Mínimo: {min(weights_values):.2f} kg"
            f"  |  Máximo: {max(weights_values):.2f} kg"
            f"  |  Media: {sum(weights_values)/len(weights_values):.2f} kg"
        )
    report.append("")
    report.append("-- HISTORIAL COMPLETO --")
    for row in weights_sorted:
        report.append(f"{fmt(row['date'])}  ->  {row['weight']}")

    # ── Informes nutricionista ────────────────────────────────────────────────
    report.append("")
    report.append("-- MEDICIONES DEL NUTRICIONISTA --")
    for row in sorted(reports_data, key=lambda r: r["date"]):
        report.append(f"Fecha: {fmt(row['date'])}")
        report.append(f"  % Grasa corporal: {row['body_fat_pct']}")
        report.append(f"  Masa muscular esquelética (kg): {row['skeletal_muscle_mass']}")
        report.append(f"  Masa libre de grasa (kg): {row['fat_free_mass']}")
        report.append(f"  Índice grasa visceral: {row['visceral_fat_index']}")
        if row['muscle_quality']:
            report.append(f"  Calidad muscular: {row['muscle_quality']}")
        report.append(f"  Grasa tronco (kg): {row['trunk_fat_kg']}")
        report.append(f"  Grasa tronco (%): {row['trunk_fat_pct']}")
        report.append(f"  Agua corporal total (kg): {row['total_body_water']}")
        if row['neck_cm']:
            report.append(f"  Cuello (cm): {row['neck_cm']}")
        if row['chest_cm']:
            report.append(f"  Pecho (cm): {row['chest_cm']}")
        if row['bicep_cm']:
            report.append(f"  Bícep (cm): {row['bicep_cm']}")
        if row['hip_cm']:
            report.append(f"  Cadera (cm): {row['hip_cm']}")
        if row['thigh_cm']:
            report.append(f"  Muslo (cm): {row['thigh_cm']}")
        report.append("")

    report.append("")
    report.append("=" * 60)
    report.append("FIN DEL INFORME")
    report.append("=" * 60)

    return "\n".join(report)