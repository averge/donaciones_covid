from flask import Blueprint, jsonify
from app.models.configuration import Configuration

bp = Blueprint('configuraciones', __name__, url_prefix="/api/configuration")


@bp.route('/datos_pagina', methods=['GET'])
def index():
    fila_t = Configuration.query.filter_by(name='home.titulo')
    fila_d = Configuration.query.filter_by(name='home.descripcion')
    json = {
        "titulo": fila_t.first().value,
        "descripcion": fila_d.first().value
    }
    return jsonify(datos=json)
