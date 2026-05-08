"""
Script de migración — lee los CSVs y los inserta en PostgreSQL.
Ejecutar una sola vez desde la raíz del proyecto:
    python3 migrate.py
"""

import os
import csv
from datetime import datetime
from db.database import get_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_CSV  = os.path.join(BASE_DIR, "data", "weights.csv")
PHASES_CSV   = os.path.join(BASE_DIR, "data", "phases.csv")
REPORTS_CSV  = os.path.join(BASE_DIR, "data", "reports.csv")


def read_csv(path: str) -> list[dict]:
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def migrate_weights(conn):
    rows = read_csv(WEIGHTS_CSV)
    cursor = conn.cursor()
    for row in rows:
        try:
            date   = datetime.strptime(row["date"].strip(), "%d/%m/%y").date()
            weight = float(row["weight"].strip())
            cursor.execute(
                "INSERT INTO weights (date, weight) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (date, weight)
            )
        except Exception as e:
            print(f"  ✗ weights fila {row}: {e}")
    conn.commit()
    print(f"  ✓ weights — {len(rows)} filas procesadas")


def migrate_phases(conn):
    rows = read_csv(PHASES_CSV)
    cursor = conn.cursor()
    for row in rows:
        try:
            start_date  = datetime.strptime(row["start_date"].strip(), "%d/%m/%y").date()
            end_date    = datetime.strptime(row["end_date"].strip(), "%d/%m/%y").date() if row["end_date"].strip() else None
            phase_type  = row["phase_type"].strip()
            weight_goal = float(row["weight_goal"].strip()) if row["weight_goal"].strip() else None
            date_goal   = datetime.strptime(row["date_goal"].strip(), "%d/%m/%y").date() if row["date_goal"].strip() else None
            cursor.execute(
                """INSERT INTO phases (start_date, end_date, phase_type, weight_goal, date_goal)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (start_date, end_date, phase_type, weight_goal, date_goal)
            )
        except Exception as e:
            print(f"  ✗ phases fila {row}: {e}")
    conn.commit()
    print(f"  ✓ phases — {len(rows)} filas procesadas")


def migrate_reports(conn):
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
                   total_body_water, neck_cm, chest_cm, bicep_cm, hip_cm, thigh_cm)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT DO NOTHING""",
                (
                    datetime.strptime(row["date"].strip(), "%d/%m/%y").date(),
                    f("body_fat_pct"), f("skeletal_muscle_mass"), f("fat_free_mass"),
                    f("visceral_fat_index"), f("muscle_quality"), f("trunk_fat_kg"),
                    f("trunk_fat_pct"), f("total_body_water"), f("neck_cm"),
                    f("chest_cm"), f("bicep_cm"), f("hip_cm"), f("thigh_cm"),
                )
            )
        except Exception as e:
            print(f"  ✗ reports fila {row}: {e}")
    conn.commit()
    print(f"  ✓ reports — {len(rows)} filas procesadas")


if __name__ == "__main__":
    print("Iniciando migración...")
    conn = get_connection()
    try:
        print("→ Migrando weights...")
        migrate_weights(conn)
        print("→ Migrando phases...")
        migrate_phases(conn)
        print("→ Migrando reports...")
        migrate_reports(conn)
        print("\n✓ Migración completada.")
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error durante la migración: {e}")
    finally:
        conn.close()