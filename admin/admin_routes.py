"""Blueprint protegido para la administración de Taidu."""
from functools import wraps
from flask import Blueprint, jsonify, render_template, request, session
from psycopg.errors import UniqueViolation, ForeignKeyViolation
from admin.admin_service import (AdminValidationError, listar_empresas, listar_usuarios,
                                 crear_empresa, crear_usuario, eliminar_usuario, desactivar_empresa)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def administrador_requerido(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"ok": False, "mensaje": "Debes iniciar sesión."}), 401
        if session.get("perfil") != "administrador":
            return jsonify({"ok": False, "mensaje": "No tienes permisos de administrador."}), 403
        return view(*args, **kwargs)
    return wrapped


@admin_bp.get("")
@administrador_requerido
def panel():
    return render_template("admin.html")


@admin_bp.get("/api/overview")
@administrador_requerido
def overview():
    return jsonify({"ok": True, "empresas": listar_empresas(), "usuarios": listar_usuarios()})


@admin_bp.post("/api/companies")
@administrador_requerido
def api_crear_empresa():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, "empresa": crear_empresa(data.get("company_name"), data.get("industry"))}), 201
    except AdminValidationError as exc:
        return jsonify({"ok": False, "mensaje": str(exc)}), 400
    except UniqueViolation:
        return jsonify({"ok": False, "mensaje": "Ya existe una empresa con ese nombre."}), 409


@admin_bp.post("/api/users")
@administrador_requerido
def api_crear_usuario():
    data = request.get_json(silent=True) or {}
    try:
        user = crear_usuario(data.get("username"), data.get("email"), data.get("password"),
                             data.get("perfil"), data.get("company_id"))
        return jsonify({"ok": True, "usuario": user}), 201
    except AdminValidationError as exc:
        return jsonify({"ok": False, "mensaje": str(exc)}), 400
    except UniqueViolation:
        return jsonify({"ok": False, "mensaje": "El correo o nombre de usuario ya está registrado."}), 409
    except ForeignKeyViolation:
        return jsonify({"ok": False, "mensaje": "El perfil o empresa seleccionados no son válidos."}), 400


@admin_bp.delete("/api/users/<int:user_id>")
@administrador_requerido
def api_eliminar_usuario(user_id):
    try:
        return jsonify({"ok": True, "eliminado": eliminar_usuario(user_id, session["user_id"])})
    except AdminValidationError as exc:
        return jsonify({"ok": False, "mensaje": str(exc)}), 400


@admin_bp.delete("/api/companies/<int:company_id>")
@administrador_requerido
def api_desactivar_empresa(company_id):
    try:
        return jsonify({"ok": True, "empresa": desactivar_empresa(company_id)})
    except AdminValidationError as exc:
        return jsonify({"ok": False, "mensaje": str(exc)}), 400
