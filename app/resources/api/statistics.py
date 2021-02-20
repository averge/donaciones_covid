from flask import Blueprint, jsonify
from sqlalchemy import func
from app.models.center import Center
from app.models.type import Type
from app.models.turno import Turno


bp = Blueprint('statistics', __name__, url_prefix="/api/estadisticas")


@bp.route('/cantidad_municipios', methods=['GET'])
def munis_index():
    munis_centers = Center.query.with_entities(Center.municipio, func.count(
        Center.municipio)
        ).filter(Center.publication_state).group_by(Center.municipio).all()
    json = []
    for item in munis_centers:
        dic = {
            "municipio": item[0],
            "cantidad": item[1]
        }
        json.append(dic)
    return (jsonify(datos=json))


@bp.route('/tipos_centros', methods=['GET'])
def types_index():
    tipos_centro = Center.query.join(Center.types).with_entities(
        Type.name, func.count(Type.id)
        ).filter(Center.publication_state).group_by(Type.name).all()
    json = []
    for item in tipos_centro:
        dic = {
            "Tipo": item[0],
            "Cantidad": item[1]
        }
        json.append(dic)
    return (jsonify(datos=json))


@bp.route('/solicitud_horarios', methods=['GET'])
def appointments_index():
    appointments = Turno.query.with_entities(
        Turno.hour_block, func.count(Turno.hour_block)
        ).group_by(Turno.hour_block).all()
    json = []
    for item in appointments:
        dic = {
            "Hora": str(item[0])[:-3],
            "Cantidad": item[1]
        }
        json.append(dic)
    return (jsonify(datos=json))
