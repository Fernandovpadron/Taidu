-- Preguntas fijas de configuración comercial para Taidu Selling Intelligence.
-- Ejecutar una vez en la base de datos PostgreSQL de Render.
-- Es idempotente: no duplica preguntas existentes por sección y orden.

INSERT INTO questions_t
    (section_code, section_name, question_text, answer_type, display_order, is_required, is_active)
VALUES
    ('A', 'La empresa y su propuesta de valor', '¿Cuál es el nombre de la empresa y qué hace? Describe brevemente la empresa, su historia, experiencia y principales actividades.', 'long_text', 1, TRUE, TRUE),
    ('A', 'La empresa y su propuesta de valor', '¿Cuál es el principal problema que la empresa resuelve para sus clientes? Describe el problema, no solamente el producto.', 'long_text', 2, TRUE, TRUE),
    ('A', 'La empresa y su propuesta de valor', '¿Cuáles son los principales productos o servicios que vende la empresa? Indica su nombre, descripción y principales aplicaciones.', 'long_text', 3, TRUE, TRUE),
    ('A', 'La empresa y su propuesta de valor', '¿Cuál es el producto o servicio que más interesa vender actualmente? Indica si existe algún producto estratégico o prioritario.', 'long_text', 4, TRUE, TRUE),
    ('A', 'La empresa y su propuesta de valor', '¿Cuál es la propuesta de valor de la empresa? ¿Por qué un cliente debería comprarles a ustedes y no a otra empresa?', 'long_text', 5, TRUE, TRUE),

    ('B', 'Cliente objetivo', '¿Quién es el cliente ideal? Describe industria, tamaño, ubicación, facturación, número de empleados u otras características relevantes.', 'long_text', 1, TRUE, TRUE),
    ('B', 'Cliente objetivo', '¿Qué tipos de clientes atienden actualmente? Incluye los segmentos B2B o B2C que correspondan.', 'long_text', 2, TRUE, TRUE),
    ('B', 'Cliente objetivo', '¿Quién suele ser el contacto inicial dentro del cliente? Por ejemplo: compras, mantenimiento, producción, recursos humanos, dueño o dirección general.', 'long_text', 3, TRUE, TRUE),
    ('B', 'Cliente objetivo', '¿Quién utiliza normalmente el producto o servicio?', 'long_text', 4, TRUE, TRUE),
    ('B', 'Cliente objetivo', '¿Quién toma la decisión final de compra? Indica quién influye, quién decide y quién autoriza el gasto.', 'long_text', 5, TRUE, TRUE),

    ('C', 'Necesidades y problemas', '¿Cuáles son los 10 problemas más frecuentes que tienen sus clientes?', 'long_text', 1, TRUE, TRUE),
    ('C', 'Necesidades y problemas', '¿Cuáles son las necesidades que normalmente el cliente expresa directamente?', 'long_text', 2, TRUE, TRUE),
    ('C', 'Necesidades y problemas', '¿Cuáles son las necesidades o problemas que el cliente normalmente NO expresa al inicio de la conversación?', 'long_text', 3, TRUE, TRUE),
    ('C', 'Necesidades y problemas', '¿Qué consecuencias tiene para el cliente no resolver esos problemas? Considera dinero, tiempo, productividad, riesgo, seguridad, calidad, ventas o personal.', 'long_text', 4, TRUE, TRUE),
    ('C', 'Necesidades y problemas', '¿Qué preguntas debería hacer un buen comercial para descubrir la necesidad real del cliente?', 'long_text', 5, TRUE, TRUE),

    ('D', 'Proceso de compra', '¿Cómo es normalmente el proceso de compra del cliente, desde el primer contacto hasta la firma o el pago?', 'long_text', 1, TRUE, TRUE),
    ('D', 'Proceso de compra', '¿Cuánto tiempo tarda normalmente una venta?', 'long_text', 2, TRUE, TRUE),
    ('D', 'Proceso de compra', '¿Cuántas personas suelen participar en la decisión de compra y qué papel tiene cada una?', 'long_text', 3, TRUE, TRUE),
    ('D', 'Proceso de compra', '¿Qué información necesita el cliente antes de tomar una decisión?', 'long_text', 4, TRUE, TRUE),
    ('D', 'Proceso de compra', '¿Cuáles son las razones más frecuentes por las que se pierde una oportunidad de venta?', 'long_text', 5, TRUE, TRUE),

    ('E', 'Producto, servicio y operación', '¿Cuáles son las principales características y beneficios de cada producto o servicio? Cuando sea posible, distingue característica, ventaja y beneficio para el cliente.', 'long_text', 1, TRUE, TRUE),
    ('E', 'Producto, servicio y operación', '¿Qué garantías ofrece la empresa?', 'long_text', 2, TRUE, TRUE),
    ('E', 'Producto, servicio y operación', '¿Cuáles son los tiempos habituales de entrega, instalación, implementación o respuesta?', 'long_text', 3, TRUE, TRUE),
    ('E', 'Producto, servicio y operación', '¿Qué cosas puede prometer el comercial y cuáles NO puede prometer al cliente?', 'long_text', 4, TRUE, TRUE),

    ('F', 'Precio y negociación', '¿Cómo se determina el precio de los productos o servicios? Por ejemplo: lista de precios, cotización personalizada, proyecto o volumen.', 'long_text', 1, TRUE, TRUE),
    ('F', 'Precio y negociación', '¿Qué descuentos puede autorizar directamente el comercial?', 'long_text', 2, TRUE, TRUE),
    ('F', 'Precio y negociación', '¿Qué condiciones comerciales puede negociar el comercial y cuáles requieren autorización? Considera precio, crédito, plazo de pago, entrega, garantía, instalación y servicio.', 'long_text', 3, TRUE, TRUE),

    ('G', 'Competencia y objeciones', '¿Quiénes son los principales competidores y por qué los clientes los eligen?', 'long_text', 1, TRUE, TRUE),
    ('G', 'Competencia y objeciones', '¿Cuáles son las 10 objeciones más frecuentes que reciben los comerciales?', 'long_text', 2, TRUE, TRUE),
    ('G', 'Competencia y objeciones', '¿Qué objeciones ocultas deberían aprender a reconocer los comerciales, cuáles podrían ser sus razones reales y cómo responde actualmente el equipo?', 'long_text', 3, TRUE, TRUE),

    ('H', 'Estándar del Director Comercial', '¿Cómo debería comportarse un comercial excelente durante una venta Taidu Selling? Describe tus expectativas desde iniciar la conversación y generar confianza hasta descubrir necesidades, identificar decisores, presentar la solución, cotizar, negociar, manejar objeciones y cerrar.', 'long_text', 1, TRUE, TRUE),
    ('H', 'Estándar del Director Comercial', '¿Qué comportamientos comerciales NO acepta la empresa?', 'long_text', 2, TRUE, TRUE)
ON CONFLICT (section_code, display_order) DO NOTHING;
