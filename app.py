from flask import Flask, render_template, request, jsonify

from intelligence.conversation import procesar_identificacion
from auth.auth_service import obtener_usuario_para_login, verificar_password
from database.connection import obtener_conexion

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json(silent=True) or {}
    id_usuario = data.get("id_usuario")
    question_id = data.get("question_id")
    respuesta = data.get("respuesta", "").strip()

    if not id_usuario or not question_id:
        return jsonify({
            "ok": False,
            "mensaje": "Falta identificar al usuario o la pregunta."
        }), 400

    if not respuesta:
        return jsonify({
            "ok": False,
            "mensaje": "Por favor escribe una respuesta."
        }), 400

    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.company_id, p.nombre
                    FROM users_t u
                    INNER JOIN profiles_t p ON p.id = u.profile_id
                    WHERE u.id = %s
                    """,
                    (id_usuario,)
                )
                usuario = cur.fetchone()

                if not usuario:
                    return jsonify({
                        "ok": False,
                        "mensaje": "No se encontró el usuario."
                    }), 404

                company_id, perfil = usuario

                if perfil != "director_comercial":
                    return jsonify({
                        "ok": False,
                        "mensaje": "Este flujo está disponible solo para Directores Comerciales."
                    }), 403

                if company_id is None:
                    return jsonify({
                        "ok": False,
                        "mensaje": "Primero debes configurar tu empresa."
                    }), 400

                cur.execute(
                    """
                    SELECT question_text
                    FROM questions_t
                    WHERE question_id = %s AND is_active = TRUE
                    """,
                    (question_id,)
                )
                pregunta = cur.fetchone()

                if not pregunta:
                    return jsonify({
                        "ok": False,
                        "mensaje": "La pregunta no existe o está inactiva."
                    }), 404

                # Actualiza la respuesta si ya existía; así evitamos duplicarla
                # si el usuario vuelve a contestar una pregunta pendiente.
                cur.execute(
                    """
                    SELECT answer_id
                    FROM answers_t
                    WHERE company_id = %s
                      AND question_id = %s
                      AND answer_source = 'fixed'
                    ORDER BY answer_id DESC
                    LIMIT 1
                    """,
                    (company_id, question_id)
                )
                respuesta_existente = cur.fetchone()

                if respuesta_existente:
                    cur.execute(
                        """
                        UPDATE answers_t
                        SET answer_text = %s,
                            question_text = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE answer_id = %s
                        """,
                        (respuesta, pregunta[0], respuesta_existente[0])
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO answers_t (
                            company_id,
                            question_id,
                            question_text,
                            answer_text,
                            answer_source
                        )
                        VALUES (%s, %s, %s, %s, 'fixed')
                        """,
                        (company_id, question_id, pregunta[0], respuesta)
                    )

        return jsonify({
            "ok": True,
            "mensaje": "Respuesta guardada correctamente."
        })

    except Exception:
        app.logger.exception("Error al guardar respuesta")
        return jsonify({
            "ok": False,
            "mensaje": "Ocurrió un error al guardar tu respuesta."
        }), 500


@app.route("/questions/next", methods=["POST"])
def siguiente_pregunta():
    data = request.get_json(silent=True) or {}
    id_usuario = data.get("id_usuario")

    if not id_usuario:
        return jsonify({
            "ok": False,
            "mensaje": "Falta identificar al usuario."
        }), 400

    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.company_id, p.nombre
                    FROM users_t u
                    INNER JOIN profiles_t p ON p.id = u.profile_id
                    WHERE u.id = %s
                    """,
                    (id_usuario,)
                )
                usuario = cur.fetchone()

                if not usuario:
                    return jsonify({
                        "ok": False,
                        "mensaje": "No se encontró el usuario."
                    }), 404

                company_id, perfil = usuario

                if perfil != "director_comercial":
                    return jsonify({
                        "ok": False,
                        "mensaje": "Este flujo está disponible solo para Directores Comerciales."
                    }), 403

                if company_id is None:
                    return jsonify({
                        "ok": False,
                        "mensaje": "Primero debes configurar tu empresa."
                    }), 400

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM questions_t
                    WHERE is_active = TRUE
                    """
                )
                total_preguntas = cur.fetchone()[0]

                cur.execute(
                    """
                    SELECT COUNT(DISTINCT question_id)
                    FROM answers_t
                    WHERE company_id = %s
                      AND answer_source = 'fixed'
                      AND question_id IS NOT NULL
                    """,
                    (company_id,)
                )
                respondidas = cur.fetchone()[0]

                cur.execute(
                    """
                    SELECT
                        q.question_id,
                        q.section_code,
                        q.section_name,
                        q.question_text,
                        q.display_order,
                        q.is_required
                    FROM questions_t q
                    WHERE q.is_active = TRUE
                      AND NOT EXISTS (
                          SELECT 1
                          FROM answers_t a
                          WHERE a.company_id = %s
                            AND a.question_id = q.question_id
                            AND a.answer_source = 'fixed'
                      )
                    ORDER BY q.section_code, q.display_order
                    LIMIT 1
                    """,
                    (company_id,)
                )
                pregunta = cur.fetchone()

        if not pregunta:
            return jsonify({
                "ok": True,
                "completado": True,
                "respondidas": respondidas,
                "total_preguntas": total_preguntas,
                "mensaje": "La configuración comercial de tu empresa está completa."
            })

        return jsonify({
            "ok": True,
            "completado": False,
            "respondidas": respondidas,
            "total_preguntas": total_preguntas,
            "pregunta": {
                "question_id": pregunta[0],
                "section_code": pregunta[1],
                "section_name": pregunta[2],
                "question_text": pregunta[3],
                "display_order": pregunta[4],
                "is_required": pregunta[5]
            }
        })

    except Exception:
        app.logger.exception("Error al consultar siguiente pregunta")
        return jsonify({
            "ok": False,
            "mensaje": "Ocurrió un error al consultar las preguntas."
        }), 500


@app.route("/identify", methods=["POST"])
def identify():
    data = request.get_json(silent=True) or {}

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

    if not flujo:
        return jsonify({
            "ok": False,
            "mensaje": "No se pudo obtener la información del usuario."
        }), 500

    company_id = flujo["company_id"]

    return jsonify({
        "ok": True,
        "id_usuario": flujo["id_usuario"],
        "usuario": username,
        "perfil": perfil,
        "flujo": flujo["flujo"],
        "company_id": company_id,
        "requiere_configurar_empresa": (
            perfil == "director_comercial" and company_id is None
        )
    })


@app.route("/company", methods=["POST"])
def configurar_empresa():
    data = request.get_json(silent=True) or {}

    id_usuario = data.get("id_usuario")
    company_name = data.get("company_name", "").strip()

    if not id_usuario or not company_name:
        return jsonify({
            "ok": False,
            "mensaje": "El usuario y el nombre de la empresa son obligatorios."
        }), 400

    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.company_id, p.nombre
                    FROM users_t u
                    INNER JOIN profiles_t p ON p.id = u.profile_id
                    WHERE u.id = %s
                    FOR UPDATE OF u
                    """,
                    (id_usuario,)
                )

                usuario = cur.fetchone()

                if not usuario:
                    return jsonify({
                        "ok": False,
                        "mensaje": "No se encontró el usuario."
                    }), 404

                company_id_actual, perfil = usuario

                if perfil != "director_comercial":
                    return jsonify({
                        "ok": False,
                        "mensaje": (
                            "Solo un Director Comercial puede configurar una empresa."
                        )
                    }), 403

                # Si ya tiene empresa, no le asignamos otra.
                if company_id_actual is not None:
                    cur.execute(
                        """
                        SELECT company_name
                        FROM companies_t
                        WHERE company_id = %s
                        """,
                        (company_id_actual,)
                    )
                    empresa = cur.fetchone()

                    return jsonify({
                        "ok": True,
                        "mensaje": "Ya tienes una empresa asignada.",
                        "company_id": company_id_actual,
                        "company_name": empresa[0] if empresa else None
                    })

                # Buscar una empresa con el mismo nombre.
                cur.execute(
                    """
                    SELECT company_id
                    FROM companies_t
                    WHERE LOWER(TRIM(company_name)) = LOWER(TRIM(%s))
                    LIMIT 1
                    """,
                    (company_name,)
                )
                empresa = cur.fetchone()

                if empresa:
                    company_id = empresa[0]
                else:
                    cur.execute(
                        """
                        INSERT INTO companies_t (company_name)
                        VALUES (%s)
                        RETURNING company_id
                        """,
                        (company_name,)
                    )
                    company_id = cur.fetchone()[0]

                # Asignar la empresa al Director Comercial.
                cur.execute(
                    """
                    UPDATE users_t
                    SET company_id = %s
                    WHERE id = %s AND company_id IS NULL
                    """,
                    (company_id, id_usuario)
                )

                if cur.rowcount != 1:
                    raise RuntimeError(
                        "No fue posible asignar la empresa al usuario."
                    )

        return jsonify({
            "ok": True,
            "mensaje": "Empresa configurada correctamente.",
            "company_id": company_id,
            "company_name": company_name
        })

    except Exception:
        app.logger.exception("Error al configurar la empresa")
        return jsonify({
            "ok": False,
            "mensaje": "Ocurrió un error al guardar la empresa."
        }), 500


if __name__ == "__main__":
    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
