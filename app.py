from flask import Flask, render_template, request, jsonify

from intelligence.conversation import procesar_identificacion
from auth.auth_service import obtener_usuario_para_login, verificar_password

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()

    respuesta = data.get("respuesta", "").strip()

    if not respuesta:
        return jsonify({
            "ok": False,
            "mensaje": "Por favor escribe una respuesta."
        })

    # Por ahora solamente devolvemos la respuesta.
    # Más adelante aquí podremos guardar en PostgreSQL,
    # procesar con IA, etc.
    return jsonify({
        "ok": True,
        "respuesta": respuesta
    })

@app.route("/identify", methods=["POST"])
def identify():
    data = request.get_json()

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email:
        return jsonify({
            "ok": False,
            "mensaje": "El correo electrónico es obligatorio."
        }), 400

    if not password:
        return jsonify({
            "ok": False,
            "mensaje": "La contraseña es obligatoria."
        }), 400

    usuario = obtener_usuario_para_login(email)

    if not usuario:
        return jsonify({
            "ok": False,
            "mensaje": "Correo o contraseña incorrectos."
        }), 401

    id_usuario, username, email_usuario, password_hash, perfil = usuario

    if not password_hash:
        return jsonify({
            "ok": False,
            "mensaje": "El usuario aún no tiene una contraseña configurada."
        }), 401

    if not verificar_password(password, password_hash):
        return jsonify({
            "ok": False,
            "mensaje": "Correo o contraseña incorrectos."
        }), 401

    flujo = procesar_identificacion(email)

    return jsonify({
        "ok": True,
        "usuario": username,
        "perfil": perfil,
        "flujo": flujo["flujo"]
    })

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))