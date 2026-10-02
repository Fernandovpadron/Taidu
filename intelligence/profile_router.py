def obtener_flujo_por_perfil(perfil):
    flujos = {
        "vendedor": "vendedor",
        "director_comercial": "director_comercial",
        "administrador": "administrador"
    }

    return flujos.get(perfil)