from flask import Blueprint, jsonify
from app.models.type import Type

bp = Blueprint('tipos', __name__, url_prefix="/api/tipos")


@bp.route('/', methods=['GET'])
def index():
    json = [tipo.name for tipo in Type.query.all()]
    return jsonify(datos=json)
