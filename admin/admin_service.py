"""Reglas de negocio y acceso a datos del panel administrativo."""
import re
from auth.auth_service import crear_password_hash
from database.connection import obtener_conexion

PERFILES_PERMITIDOS = {"director_comercial", "vendedor"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AdminValidationError(ValueError):
    pass


def listar_empresas():
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT company_id, company_name, industry, is_active
                           FROM companies_t WHERE is_active = TRUE
                           ORDER BY LOWER(company_name)""")
            return [{"company_id": r[0], "company_name": r[1], "industry": r[2], "is_active": r[3]}
                    for r in cur.fetchall()]


def listar_usuarios():
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT u.id, u.username, u.email, p.nombre, u.company_id, c.company_name
                           FROM users_t u JOIN profiles_t p ON p.id = u.profile_id
                           LEFT JOIN companies_t c ON c.company_id = u.company_id
                           ORDER BY u.id""")
            return [{"id": r[0], "username": r[1], "email": r[2], "perfil": r[3],
                     "company_id": r[4], "company_name": r[5]} for r in cur.fetchall()]


def crear_empresa(company_name, industry=None):
    company_name = (company_name or "").strip()
    industry = (industry or "").strip() or None
    if not company_name:
        raise AdminValidationError("El nombre de la empresa es obligatorio.")
    if len(company_name) > 200:
        raise AdminValidationError("El nombre de la empresa no puede superar 200 caracteres.")
    if industry and len(industry) > 150:
        raise AdminValidationError("La industria no puede superar 150 caracteres.")
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT company_id FROM companies_t WHERE LOWER(TRIM(company_name)) = LOWER(TRIM(%s)) LIMIT 1", (company_name,))
            if cur.fetchone():
                raise AdminValidationError("Ya existe una empresa con ese nombre.")
            cur.execute("""INSERT INTO companies_t (company_name, industry, is_active)
                           VALUES (%s, %s, TRUE)
                           RETURNING company_id, company_name, industry, is_active""", (company_name, industry))
            r = cur.fetchone()
    return {"company_id": r[0], "company_name": r[1], "industry": r[2], "is_active": r[3]}


def crear_usuario(username, email, password, perfil, company_id=None):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    password = password or ""
    perfil = (perfil or "").strip().lower()
    if not username or len(username) > 100:
        raise AdminValidationError("El nombre de usuario es obligatorio y debe tener máximo 100 caracteres.")
    if not EMAIL_RE.match(email) or len(email) > 254:
        raise AdminValidationError("Introduce un correo electrónico válido.")
    if len(password) < 12:
        raise AdminValidationError("La contraseña inicial debe tener al menos 12 caracteres.")
    if perfil not in PERFILES_PERMITIDOS:
        raise AdminValidationError("Solo se pueden crear usuarios director_comercial o vendedor.")
    try:
        company_id = int(company_id) if company_id not in (None, "") else None
    except (TypeError, ValueError):
        raise AdminValidationError("La empresa seleccionada no es válida.")
    # Regla requerida: el vendedor siempre debe estar ligado a empresa activa.
    if perfil == "vendedor" and company_id is None:
        raise AdminValidationError("Todo vendedor debe estar asociado a una empresa activa.")

    password_hash = crear_password_hash(password)
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM profiles_t WHERE nombre = %s", (perfil,))
            profile = cur.fetchone()
            if not profile:
                raise AdminValidationError(f"No existe el perfil '{perfil}' en profiles_t.")
            if company_id is not None:
                cur.execute("SELECT company_id FROM companies_t WHERE company_id = %s AND is_active = TRUE", (company_id,))
                if not cur.fetchone():
                    raise AdminValidationError("La empresa seleccionada no existe o está inactiva.")
            cur.execute("""INSERT INTO users_t (username, email, profile_id, password_hash, company_id)
                           VALUES (%s, %s, %s, %s, %s)
                           RETURNING id, username, email, company_id""",
                        (username, email, profile[0], password_hash, company_id))
            r = cur.fetchone()
    return {"id": r[0], "username": r[1], "email": r[2], "perfil": perfil, "company_id": r[3]}


def eliminar_usuario(user_id, actor_user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise AdminValidationError("El identificador de usuario no es válido.")
    if user_id == actor_user_id:
        raise AdminValidationError("No puedes eliminar tu propia cuenta mientras tienes la sesión abierta.")
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT u.id, u.email, p.nombre FROM users_t u
                           JOIN profiles_t p ON p.id = u.profile_id WHERE u.id = %s FOR UPDATE OF u""", (user_id,))
            target = cur.fetchone()
            if not target:
                raise AdminValidationError("El usuario no existe.")
            if target[2] == "administrador":
                cur.execute("""SELECT COUNT(*) FROM users_t u JOIN profiles_t p ON p.id = u.profile_id
                               WHERE p.nombre = 'administrador'""")
                if cur.fetchone()[0] <= 1:
                    raise AdminValidationError("No se puede eliminar al último administrador.")
            cur.execute("DELETE FROM users_t WHERE id = %s", (user_id,))
    return {"id": user_id, "email": target[1]}


def desactivar_empresa(company_id):
    try:
        company_id = int(company_id)
    except (TypeError, ValueError):
        raise AdminValidationError("El identificador de empresa no es válido.")
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT company_id, company_name FROM companies_t
                           WHERE company_id = %s AND is_active = TRUE FOR UPDATE""", (company_id,))
            company = cur.fetchone()
            if not company:
                raise AdminValidationError("La empresa no existe o ya está inactiva.")
            cur.execute("SELECT COUNT(*) FROM users_t WHERE company_id = %s", (company_id,))
            if cur.fetchone()[0]:
                raise AdminValidationError("No se puede desactivar una empresa con usuarios asociados. Reasigna primero a sus usuarios.")
            cur.execute("UPDATE companies_t SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE company_id = %s", (company_id,))
    return {"company_id": company_id, "company_name": company[1]}
