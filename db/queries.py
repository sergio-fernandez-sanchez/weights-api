import psycopg2
import psycopg2.extras
from datetime import date, datetime
from db.database import get_connection


# Auth

def get_user_by_email(email: str) -> dict | None:
    """
    Busca un usuario por email en la tabla "users".
    Devuelve un diccionario con id, email y password o None si no existe.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        conn.close()


def insert_user(email: str, hashed_password: str) -> str:
    """
    Inserta un nuevo usuario en la tabla "users".
    Recibe el email y la contraseña ya hasheada.
    Devuelve "added" si se ha creado correctamente.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)",
                       (email, hashed_password))
        conn.commit()
        return "added"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Weights

def get_weights(user_id: int) -> list[dict]:
    """
    Hace una consulta SELECT y devuelve todos los datos de la tabla "weights"
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)       # RealDictCursor hace que fetchall() devuelva lista de dicts en lugar de tuplas
        cursor.execute("SELECT * FROM weights WHERE user_id = %s", (user_id,))
        return cursor.fetchall()                                                   # fetchall() recoge todos los resultados de la query — están esperando en el cursor
    except Exception as e:
        raise e
    finally:
        conn.close()


def get_weight_on_date(target_date: date, user_id: int) -> dict | None:
    """
    Hace una consulta SELECT y devuelve el diccionario de la tabla "weights" de la fecha indicada
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM weights WHERE date = %s AND user_id = %s",   # %s es el placeholder — psycopg2 lo sustituye por target_date de forma segura (evita SQL injection), la coma después de target_date es necesaria para que sea una tupla
                       (target_date, user_id))
        return cursor.fetchone()                                                   # fetchone() devuelve solo la primera fila porque solo esperamos un resultado
    except Exception as e:
        raise e
    finally:
        conn.close()


def get_last_weight(user_id: int) -> dict | None:
    """
    Hace una consulta SELECT y devuelve un diccionario con la ultima fila de "weights"
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM weights WHERE user_id = %s ORDER BY date DESC LIMIT 1",
                       (user_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        conn.close()


def insert_weight(new_weight: float, user_id: int) -> str:
    """
    Inserta un nuevo registro en la tabla "weights" con la fecha de hoy.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("INSERT INTO weights (date, weight, user_id) VALUES (%s, %s, %s)",
                       (datetime.now().date(), new_weight, user_id))
        conn.commit()                                                      # commit() confirma los cambios en la BD, sin esto el INSERT no se guarda, los SELECT no necesitan commit(), solo INSERT/UPDATE/DELETE
        return "added"
    except Exception as e:
        conn.rollback()                                                    # rollback() deshace los cambios y deja la BD como estaba
        raise e
    finally:
        conn.close()


def update_weight(new_weight: float, user_id: int) -> str:
    """
    Actualiza el ultimo registro de peso con la fecha de hoy.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("UPDATE weights SET weight = %s WHERE date = %s AND user_id = %s",
                       (new_weight, datetime.now().date(), user_id))
        conn.commit()
        return "updated"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Phases

def get_phases(user_id: int) -> list[dict]:
    """
    Hace una consulta SELECT y devuelve todos los datos de la tabla "phases"
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM phases WHERE user_id = %s", (user_id,))
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        conn.close()


def get_active_phase(user_id: int) -> dict | None:
    """
    Hace una consulta SELECT y devuelve el dato de la tabla "phases" que no tiene "end_date"
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM phases WHERE end_date IS NULL AND user_id = %s",
                       (user_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        conn.close()


def close_phase(end_date: date, user_id: int) -> str:
    """
    Actualiza el "end_date" de la ultima fila.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("UPDATE phases SET end_date = %s WHERE end_date IS NULL AND user_id = %s",
                       (end_date, user_id))
        conn.commit()
        return "closed old phase"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def insert_phase(new_phase: dict, user_id: int) -> str:
    """
    Inserta un nuevo registro en la tabla "phases" con la fecha de hoy.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        date_goal = datetime.strptime(new_phase["date_goal"], "%d/%m/%y").date() if new_phase.get("date_goal") else None
        cursor.execute("INSERT INTO phases (start_date, phase_type, weight_goal, date_goal, user_id) "
                       "VALUES (%s, %s, %s, %s, %s)",
                       (datetime.now().date(), new_phase["phase_type"],
                        new_phase.get("weight_goal"), date_goal, user_id))
        conn.commit()
        return "added"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_phase_goals(weight_goal: float, date_goal: date, user_id: int) -> str:
    """
    Actualiza el peso objetivo y la fecha objetivo de la fase activa del usuario.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """
            UPDATE phases
            SET weight_goal = %s, date_goal = %s
            WHERE user_id = %s AND end_date IS NULL
            """,
            (weight_goal, date_goal, user_id)
        )
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Reports

def get_reports(user_id: int) -> list[dict]:
    """
    Hace una consulta SELECT y devuelve todos los datos de la tabla "reports"
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM reports WHERE user_id = %s", (user_id,))
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        conn.close()


def insert_report(report_data: dict, user_id: int) -> str:
    """
    Inserta un nuevo registro en la tabla "reports".
    Si no se proporciona fecha, usa la fecha de hoy.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """INSERT INTO reports (date, body_fat_pct, skeletal_muscle_mass, fat_free_mass,
                                    visceral_fat_index, muscle_quality, trunk_fat_kg, trunk_fat_pct,
                                    total_body_water, neck_cm, chest_cm, bicep_cm, hip_cm, thigh_cm,
                                    user_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                report_data.get("date") or datetime.now().date(),
                report_data.get("body_fat_pct"),
                report_data.get("skeletal_muscle_mass"),
                report_data.get("fat_free_mass"),
                report_data.get("visceral_fat_index"),
                report_data.get("muscle_quality"),
                report_data.get("trunk_fat_kg"),
                report_data.get("trunk_fat_pct"),
                report_data.get("total_body_water"),
                report_data.get("neck_cm"),
                report_data.get("chest_cm"),
                report_data.get("bicep_cm"),
                report_data.get("hip_cm"),
                report_data.get("thigh_cm"),
                user_id,
            )
        )
        conn.commit()
        return "added"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()