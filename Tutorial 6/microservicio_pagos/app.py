"""
Microservicio de pagos (v2) - Tutorial 06, primer estrangulamiento.

Extrae la compra del monolito Django a un servicio Flask independiente. Nginx
envía aquí /api/v2/comprar y deja /api/v1/ en Django, así que el cliente no
nota que, al comprar, sale de un sistema y entra a otro.
"""

import logging

from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [pagos_flask] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/api/v2/comprar", methods=["POST"], strict_slashes=False)
def realizar_compra():
    # silent=True: un cuerpo vacío o que no es JSON no rompe el servicio con un
    # 400 en HTML; se responde con el error en JSON como el resto del API.
    data = request.get_json(silent=True) or {}

    # Simulación de la lógica de negocio extraída del monolito
    producto_id = data.get("producto_id")
    cantidad = data.get("cantidad", 1)

    if not producto_id:
        return jsonify({"error": "Falta el ID del producto"}), 400

    log.info("Compra recibida: producto=%s cantidad=%s", producto_id, cantidad)

    return jsonify({
        "mensaje": "Compra procesada exitosamente por el Microservicio Flask (v2)",
        "producto_id": producto_id,
        "cantidad": cantidad,
        "status": "Aprobado",
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"estado": "ok", "servicio": "pagos_flask"}), 200


@app.errorhandler(404)
def no_encontrado(_error):
    return jsonify({"error": "Ruta no encontrada"}), 404


@app.errorhandler(405)
def metodo_no_permitido(_error):
    return jsonify({"error": "Método no permitido"}), 405


@app.errorhandler(500)
def error_interno(_error):
    return jsonify({"error": "Error interno"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
