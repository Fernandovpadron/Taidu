
from users.users_service import obtener_usuario_por_email
from intelligence.profile_router import obtener_flujo_por_perfil


def procesar_identificacion(email):
    usuario = obtener_usuario_por_email(email)

    if not usuario:
        return None

    id_usuario, username, email_usuario, perfil, company_id = usuario

    flujo = obtener_flujo_por_perfil(perfil)

    return {
        "id_usuario": id_usuario,
        "username": username,
        "email": email_usuario,
        "perfil": perfil,
        "company_id": company_id,
        "flujo": flujo
    }
