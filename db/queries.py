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
    Hace una consulta SELECT y devuelve todos los datos de la tabla "weights" del usuario.
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


def get_weight_on_date(user_id: int, target_date: date) -> dict | None:
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


def insert_weight(user_id: int, new_weight: float) -> str:
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


def update_weight(user_id: int, new_weight: float) -> str:
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
    Hace una consulta SELECT y devuelve todos los datos de la tabla "phases" del usuario.
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


def close_phase(user_id: int, end_date: date) -> str:
    """
    Actualiza el "end_date" de la ultima fila en la tabla "phases".
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


def insert_phase(user_id: int, new_phase: dict) -> str:
    """
    Inserta un nuevo registro en la tabla "phases".
    Si se proporciona start_date la usa como fecha de inicio, si no usa hoy.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        start_date = new_phase.get("start_date") or datetime.now().date()
        date_goal = datetime.strptime(new_phase["date_goal"], "%d/%m/%y").date() if new_phase.get("date_goal") else None
        cursor.execute("INSERT INTO phases (start_date, phase_type, weight_goal, date_goal, user_id) "
                       "VALUES (%s, %s, %s, %s, %s)",
                       (start_date, new_phase["phase_type"],
                        new_phase.get("weight_goal"), date_goal, user_id))
        conn.commit()
        return "added"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_phase_goals(user_id: int, new_phase_goals: dict) -> str:
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
            (new_phase_goals["weight_goal"], new_phase_goals["date_goal"], user_id)
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


def insert_report(user_id: int, report_data: dict) -> str:
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


# Calories

def get_calories(user_id: int) -> list[dict]:
    """
    Hace una consulta SELECT y devuelve todos los datos de la tabla "calories" del usuario.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM calories WHERE user_id = %s", (user_id,))
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        conn.close()


def get_active_calories(user_id: int) -> dict | None:
    """
    Hace una consulta SELECT y devuelve el dato de la tabla "calories" que no tiene "end_date"
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM calories WHERE user_id = %s AND end_date IS NULL", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        conn.close()


def insert_calories(user_id: int, new_calories: dict) -> str:
    """
    Inserta un nuevo registro en la tabla "calories".
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        start_date = datetime.now().date()
        cursor.execute("INSERT INTO calories (start_date, calories, user_id) "
                       "VALUES (%s, %s, %s)",
                       (start_date, new_calories["calories"], user_id,))
        conn.commit()
        return "added"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def close_calories(user_id: int) -> str:
    """
    Cierra el objetivo calórico activo poniendo end_date a hoy.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "UPDATE calories SET end_date = %s WHERE user_id = %s AND end_date IS NULL",
            (datetime.now().date(), user_id)
        )
        conn.commit()
        return "closed"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Exercise types

def get_exercise_type(user_id: int) -> list[dict]:
    """
    Hace una consulta SELECT y devuelve todos los datos de la tabla "exercise_types" del usuario.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM exercise_types WHERE user_id IS NULL OR user_id = %s ORDER BY category, name",
            (user_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        conn.close()


def insert_exercise_type(user_id: int, new_exercise_type: dict):
    """
    Inserta un nuevo registro en la tabla "exercise_types".
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("INSERT INTO exercise_types (name, category, user_id) "
                       "VALUES (%s, %s, %s)",
                       (new_exercise_type["name"], new_exercise_type["category"], user_id,))
        conn.commit()
        return "added"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



# Gym logs

def get_gym_logs(user_id: int) -> list[dict]:
    """
    Devuelve todos los gym_logs del usuario con nombre y categoría del ejercicio.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT gl.id, gl.start_date, gl.end_date, gl.weight, gl.reps, gl.user_id,
                   et.id as exercise_type_id, et.name, et.category
            FROM gym_logs gl
            JOIN exercise_types et ON gl.exercise_type_id = et.id
            WHERE gl.user_id = %s
            ORDER BY gl.start_date
        """, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        conn.close()


def insert_gym_log(user_id: int, log_data: dict) -> str:
    """
    Inserta un nuevo registro en la tabla "gym_logs".
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "INSERT INTO gym_logs (start_date, exercise_type_id, weight, reps, user_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (datetime.now().date(), log_data["exercise_type_id"],
             log_data.get("weight"), log_data.get("reps"), user_id)
        )
        conn.commit()
        return "added"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def close_gym_log(user_id: int, log_id: int, end_date: date) -> str:
    """
    Pone end_date en el gym_log con el id indicado.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "UPDATE gym_logs SET end_date = %s WHERE id = %s AND user_id = %s",
            (end_date, log_id, user_id)
        )
        conn.commit()
        return "closed"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_active_gym_logs(user_id: int) -> list[dict]:
    """
    Devuelve todos los gym_logs activos del usuario (sin end_date),
    con el nombre y categoría del ejercicio incluidos.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT gl.id, gl.start_date, gl.weight, gl.reps, gl.user_id,
                   et.id as exercise_type_id, et.name, et.category
            FROM gym_logs gl
            JOIN exercise_types et ON gl.exercise_type_id = et.id
            WHERE gl.user_id = %s AND gl.end_date IS NULL
            ORDER BY et.category, et.name
        """, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        conn.close()