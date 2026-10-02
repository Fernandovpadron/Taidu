from database.connection import obtener_conexion
from werkzeug.security import generate_password_hash, check_password_hash


def crear_password_hash(password):
    return generate_password_hash(password)


def verificar_password(password, password_hash):
    return check_password_hash(password_hash, password)


def establecer_password(email, password):
    password_hash = crear_password_hash(password)

    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users_t
                SET password_hash = %s
                WHERE email = %s
                """,
                (password_hash, email)
            )

        conn.commit()

    return True

def obtener_usuario_para_login(email):
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.id,
                    u.username,
                    u.email,
                    u.password_hash,
                    p.nombre AS perfil
                FROM users_t u
                INNER JOIN profiles_t p
                    ON u.profile_id = p.id
                WHERE u.email = %s
                """,
                (email,)
            )

            return cur.fetchone()