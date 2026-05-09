"""
Script de migración y generación de datos.
- user_id=1: datos demo con lógica nutricional
- user_id=2: migra datos reales desde CSVs

Ejecutar una sola vez desde la raíz del proyecto:
    python3 migrate.py
"""

import os
import csv
from datetime import datetime, date, timedelta
from db.database import get_connection
import random
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_CSV  = os.path.join(BASE_DIR, "data", "weights.csv")
PHASES_CSV   = os.path.join(BASE_DIR, "data", "phases.csv")
REPORTS_CSV  = os.path.join(BASE_DIR, "data", "reports.csv")


def read_csv(path: str) -> list[dict]:
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── Migración datos reales ────────────────────────────────────────────────────

def migrate_weights(conn, user_id: int):
    rows = read_csv(WEIGHTS_CSV)
    cursor = conn.cursor()
    for row in rows:
        try:
            d = datetime.strptime(row["date"].strip(), "%d/%m/%y").date()
            w = float(row["weight"].strip())
            cursor.execute(
                "INSERT INTO weights (date, weight, user_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (d, w, user_id)
            )
        except Exception as e:
            print(f"  ✗ weights fila {row}: {e}")
    conn.commit()
    print(f"  ✓ weights reales — {len(rows)} filas")


def migrate_phases(conn, user_id: int):
    rows = read_csv(PHASES_CSV)
    cursor = conn.cursor()
    for row in rows:
        try:
            start = datetime.strptime(row["start_date"].strip(), "%d/%m/%y").date()
            end   = datetime.strptime(row["end_date"].strip(), "%d/%m/%y").date() if row["end_date"].strip() else None
            ptype = row["phase_type"].strip()
            wgoal = float(row["weight_goal"].strip()) if row["weight_goal"].strip() else None
            dgoal = datetime.strptime(row["date_goal"].strip(), "%d/%m/%y").date() if row["date_goal"].strip() else None
            cursor.execute(
                """INSERT INTO phases (start_date, end_date, phase_type, weight_goal, date_goal, user_id)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (start, end, ptype, wgoal, dgoal, user_id)
            )
        except Exception as e:
            print(f"  ✗ phases fila {row}: {e}")
    conn.commit()
    print(f"  ✓ phases reales — {len(rows)} filas")


def migrate_reports(conn, user_id: int):
    rows = read_csv(REPORTS_CSV)
    cursor = conn.cursor()
    for row in rows:
        try:
            def f(key):
                val = row.get(key, "").strip()
                return float(val) if val else None
            cursor.execute(
                """INSERT INTO reports (date, body_fat_pct, skeletal_muscle_mass, fat_free_mass,
                   visceral_fat_index, muscle_quality, trunk_fat_kg, trunk_fat_pct,
                   total_body_water, neck_cm, chest_cm, bicep_cm, hip_cm, thigh_cm, user_id)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    datetime.strptime(row["date"].strip(), "%d/%m/%y").date(),
                    f("body_fat_pct"), f("skeletal_muscle_mass"), f("fat_free_mass"),
                    f("visceral_fat_index"), f("muscle_quality"), f("trunk_fat_kg"),
                    f("trunk_fat_pct"), f("total_body_water"), f("neck_cm"),
                    f("chest_cm"), f("bicep_cm"), f("hip_cm"), f("thigh_cm"),
                    user_id
                )
            )
        except Exception as e:
            print(f"  ✗ reports fila {row}: {e}")
    conn.commit()
    print(f"  ✓ reports reales — {len(rows)} filas")


# ── Datos demo ────────────────────────────────────────────────────────────────

DEMO_PHASES = [
    (date(2023, 1,  1), date(2023, 6,  1), "bulk",        82.0, date(2023, 6,  1)),
    (date(2023, 6,  1), date(2023, 12, 1), "cut",         74.0, date(2023, 12, 1)),
    (date(2023, 12, 1), date(2024, 6,  1), "bulk",        80.0, date(2024, 6,  1)),
    (date(2024, 6,  1), date(2024, 12, 1), "cut",         73.0, date(2024, 12, 1)),
    (date(2024, 12, 1), None,              "maintenance",  76.0, date(2025, 12, 1)),
]

DEMO_WEIGHT_TARGETS = [
    (date(2023, 1,  1), 75.0,  date(2023, 6,  1), 82.0),
    (date(2023, 6,  1), 82.0,  date(2023, 12, 1), 74.5),
    (date(2023, 12, 1), 74.5,  date(2024, 6,  1), 80.5),
    (date(2024, 6,  1), 80.5,  date(2024, 12, 1), 73.5),
    (date(2024, 12, 1), 73.5,  date(2025, 5,  9), 76.0),
]

DEMO_REPORTS = [
    (date(2023, 1,  15), 18.5, 32.1, 61.4, 4, None, 7.2, 19.0, 43.5, 37.0, 96.0, 33.0, 88.0, 55.0),
    (date(2023, 4,  10), 19.2, 33.8, 62.8, 4, 62,   7.9, 19.8, 44.8, 37.5, 98.0, 34.5, 89.0, 56.5),
    (date(2023, 7,   5), 17.1, 33.5, 62.2, 3, 64,   6.8, 17.5, 44.2, 37.0, 96.0, 34.0, 87.0, 55.5),
    (date(2023, 10,  2), 15.8, 33.2, 62.8, 3, 65,   5.9, 16.2, 44.9, 36.5, 95.0, 33.5, 86.0, 54.5),
    (date(2024, 1,  20), 16.2, 34.5, 63.5, 3, 66,   6.2, 16.5, 45.2, 37.0, 97.0, 34.8, 87.0, 55.0),
    (date(2024, 4,  14), 17.8, 35.8, 64.8, 4, 67,   7.1, 18.0, 46.1, 37.5, 99.0, 36.0, 88.5, 56.0),
    (date(2024, 7,   8), 15.2, 35.4, 64.2, 3, 68,   5.8, 15.8, 45.8, 37.0, 97.0, 35.5, 86.5, 55.0),
    (date(2024, 10,  7), 14.1, 35.1, 63.5, 2, 69,   5.2, 14.9, 45.5, 36.5, 96.0, 35.0, 85.0, 54.0),
    (date(2025, 1,  13), 14.8, 35.6, 64.0, 3, 70,   5.5, 15.2, 45.8, 37.0, 97.0, 35.5, 85.5, 54.5),
    (date(2025, 4,   7), 14.5, 35.9, 64.5, 3, 71,   5.3, 15.0, 46.0, 37.0, 97.5, 35.8, 85.0, 54.5),
]


def generate_demo_weights(conn, user_id: int):
    cursor = conn.cursor()
    count = 0
    for (start, w_start, end, w_end) in DEMO_WEIGHT_TARGETS:
        total_days = (end - start).days
        for i in range(total_days):
            d = start + timedelta(days=i)
            progress = i / total_days
            base = w_start + (w_end - w_start) * progress
            noise = random.gauss(0, 0.25)
            weekly = 0.3 * math.sin(2 * math.pi * d.weekday() / 7)
            weight = round(base + noise + weekly, 2)
            try:
                cursor.execute(
                    "INSERT INTO weights (date, weight, user_id) VALUES (%s, %s, %s)",
                    (d, weight, user_id)
                )
                count += 1
            except Exception as e:
                print(f"  ✗ demo weight {d}: {e}")
    conn.commit()
    print(f"  ✓ weights demo — {count} filas")


def generate_demo_phases(conn, user_id: int):
    cursor = conn.cursor()
    for (start, end, ptype, wgoal, dgoal) in DEMO_PHASES:
        cursor.execute(
            """INSERT INTO phases (start_date, end_date, phase_type, weight_goal, date_goal, user_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (start, end, ptype, wgoal, dgoal, user_id)
        )
    conn.commit()
    print(f"  ✓ phases demo — {len(DEMO_PHASES)} filas")


def generate_demo_reports(conn, user_id: int):
    cursor = conn.cursor()
    for r in DEMO_REPORTS:
        cursor.execute(
            """INSERT INTO reports (date, body_fat_pct, skeletal_muscle_mass, fat_free_mass,
               visceral_fat_index, muscle_quality, trunk_fat_kg, trunk_fat_pct,
               total_body_water, neck_cm, chest_cm, bicep_cm, hip_cm, thigh_cm, user_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (*r, user_id)
        )
    conn.commit()
    print(f"  ✓ reports demo — {len(DEMO_REPORTS)} filas")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    conn = get_connection()
    try:
        print("→ Generando datos demo (user_id=1)...")
        generate_demo_phases(conn, user_id=1)
        generate_demo_weights(conn, user_id=1)
        generate_demo_reports(conn, user_id=1)

        print("\n→ Migrando datos reales (user_id=2)...")
        migrate_weights(conn, user_id=2)
        migrate_phases(conn, user_id=2)
        migrate_reports(conn, user_id=2)

        print("\n✓ Migración completada.")
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error: {e}")
    finally:
        conn.close()