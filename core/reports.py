import os
from datetime import datetime
from core.csv_utils import read_csv, write_csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_CSV_PATH = os.path.join(BASE_DIR, "data", "reports.csv")

FIELD_NAMES = ["date", "body_fat_pct", "skeletal_muscle_mass", "fat_free_mass", "visceral_fat_index", "muscle_quality",
               "trunk_fat_kg", "trunk_fat_pct", "total_body_water", "neck_cm", "chest_cm", "bicep_cm", "hip_cm", "thigh_cm"]


def add_report(report_data: dict) -> None:
    """
    Añade un nuevo report usando un dict y le añade la fecha actual en el campo "date"
    """
    current_date = datetime.now().strftime("%d/%m/%y")
    csv_list = read_csv(REPORTS_CSV_PATH)

    report_data["date"] = current_date
    csv_list.append(report_data)

    write_csv(csv_list, REPORTS_CSV_PATH, FIELD_NAMES)


def parse_reports() -> list[dict]:
    """
    Lee todos los registros de reports del CSV y los devuelve
    en una lista parseados.
    Los campos opcionales que están vacíos se devuelven como None.
    """
    csv_list = read_csv(REPORTS_CSV_PATH)
    reports = []

    for csv_row in csv_list:
        try:
            reports.append({
                "date": datetime.strptime(csv_row["date"], "%d/%m/%y").date(),
                "body_fat_pct": float(csv_row["body_fat_pct"]) if csv_row["body_fat_pct"] else None,
                "skeletal_muscle_mass": float(csv_row["skeletal_muscle_mass"]) if csv_row["skeletal_muscle_mass"] else None,
                "fat_free_mass": float(csv_row["fat_free_mass"]) if csv_row["fat_free_mass"] else None,
                "visceral_fat_index": float(csv_row["visceral_fat_index"]) if csv_row["visceral_fat_index"] else None,
                "muscle_quality": float(csv_row["muscle_quality"]) if csv_row["muscle_quality"] else None,
                "trunk_fat_kg": float(csv_row["trunk_fat_kg"]) if csv_row["trunk_fat_kg"] else None,
                "trunk_fat_pct": float(csv_row["trunk_fat_pct"]) if csv_row["trunk_fat_pct"] else None,
                "total_body_water": float(csv_row["total_body_water"]) if csv_row["total_body_water"] else None,
                "neck_cm": float(csv_row["neck_cm"]) if csv_row["neck_cm"] else None,
                "chest_cm": float(csv_row["chest_cm"]) if csv_row["chest_cm"] else None,
                "bicep_cm": float(csv_row["bicep_cm"]) if csv_row["bicep_cm"] else None,
                "hip_cm": float(csv_row["hip_cm"]) if csv_row["hip_cm"] else None,
                "thigh_cm": float(csv_row["thigh_cm"]) if csv_row["thigh_cm"] else None
            })
        except (ValueError, KeyError):
            continue
    return reports