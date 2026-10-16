
from database.connection import obtener_conexion


def obtener_usuario_por_email(email):
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.id,
                    u.username,
                    u.email,
                    p.nombre AS perfil,
                    u.company_id
                FROM users_t u
                INNER JOIN profiles_t p
                    ON u.profile_id = p.id
                WHERE u.email = %s
                """,
                (email,)
            )

            return cur.fetchone()
