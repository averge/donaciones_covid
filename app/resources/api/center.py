from flask import Blueprint, jsonify, request, abort
from app.models.center import Center
from app.models.turno import Turno
from app.helpers.paginate import paginate, get_page, number_of_pages
from app.helpers.security import validate_json_center
from app.models.state import State
from app.models.type import Type
from datetime import datetime, timedelta
import requests

bp = Blueprint('centros', __name__, url_prefix="/api/centros")


@bp.route('/', methods=['GET'])
def index():
    """
    Devuelve todos los centros del sistema en formato Json
    """
    page = request.args.get("page")
    if page and not page.isnumeric():
        abort(400, "Parametro de página inválido")
    centers = Center.query.filter(Center.publication_state)
    total = number_of_pages(centers)
    centers = paginate(centers, page)
    json = []
    for centro in centers:
        coord = centro.coordinates.split(",")
        coord[0] = float(coord[0])
        coord[1] = float(coord[1])
        dic = {
            "id": centro.id,
            "nombre": centro.name,
            "direccion": centro.address,
            "telefono": centro.phone_number,
            "hora_apertura": centro.opens_at.isoformat()[0:-3],
            "hora_cierre": centro.close_at.isoformat()[0:-3],
            "tipo": centro.types[0].name,
            "web": centro.web,
            "email": centro.email,
            "coordenadas": coord,
            "municipio": {
                "id": centro.municipio
            }
        }
        json.append(dic)
    return jsonify(datos=json, total=total, pagina=get_page(page))


@bp.route('/', methods=['POST'])
def new():
    """
    Crea un centro con los datos recibidos en formato Json a traves de POST
    """
    json = request.get_json(force=True)
    errors = validate_json_center(json)
    if errors:
        abort(400, f"El JSON no es valido, {errors}")
    url = "https://api-referencias.proyecto2020.linti.unlp.edu.ar/"
    munis = requests.get(url + "municipios?per_page=300")
    if munis.status_code != 200:
        abort(500)
    if "id" in json["municipio"]:
        pos = "id"
        search = json["municipio"]["id"]
    else:
        pos = "name"
        search = json["municipio"]["nombre"]

    found = False
    for m in munis.json()["data"]["Town"].values():
        if search == m[pos]:
            found = True
            id = m["id"]
            name = m["name"]
    if not found:
        return jsonify(messages="El municipio no se encontro"), 400
    new_center = Center(
        name=json["nombre"],
        address=json["direccion"],
        phone_number=json["telefono"],
        opens_at=json["hora_apertura"],
        close_at=json["hora_cierre"],
        web=json["web"],
        email=json["email"],
        publication_state=False,
        municipio=str(id),
        coordinates=(
            str(json["coordenadas"][0]) + "," +
            str(json["coordenadas"][1])
        )
    )
    try:
        tipo = Type.query.filter_by(name=json["tipo"]).first()
        if not tipo:
            tipos = [tipo.name for tipo in Type.query.all()]
            error = "no existe el tipo indicado en la aplicación,"
            error += " los tipos que existen son: "
            for tipo in tipos:
                error += " " + tipo + ","
            raise AssertionError(error)
        new_center.types.append(tipo)
        state = State.query.filter_by(name="Pendiente").first()
        state.centers.append(new_center)
        new_center.validate_and_save()
        dic = {
            "id": new_center.id,
            "nombre": new_center.name,
            "direccion": new_center.address,
            "telefono": new_center.phone_number,
            "hora_apertura": new_center.opens_at.isoformat()[0:-3],
            "hora_cierre": new_center.close_at.isoformat()[0:-3],
            "tipo": new_center.types[0].name,
            "web": new_center.web,
            "email": new_center.email,
            "coordenadas": json["coordenadas"],
            "municipio": {
                "id": id,
                "name": name
            }
        }
        return jsonify(atributos=dic), 201
    except AssertionError as err:
        return jsonify(messages=str(err)[0:-1]), 400


@bp.route("/<int:id>/turnos_disponibles/", methods=["GET"])
def turnos_index(id):
    """
    Devuelve un json con todos los turnos disponibles para un centro
    en una fecha especifica, si no recibe fecha, muestra los del dia.
    La fecha la recibe en la url
    """
    centro = Center.query.filter_by(id=id).first()
    if(not centro):
        return jsonify(messages="El centro consultado no existe"), 404
    if(not centro.publication_state):
        return jsonify(
            messages="El centro consultado no se encuentra publicado"
        ), 400
    cierra = timedelta(
        hours=centro.close_at.hour,
        minutes=centro.close_at.minute,
        seconds=centro.close_at.second,
    )
    abre = timedelta(
        hours=centro.opens_at.hour,
        minutes=centro.opens_at.minute,
        seconds=centro.opens_at.second,
    )
    if cierra < abre:
        cierra += timedelta(minutes=1440)
    cant_t = (cierra - abre) / timedelta(minutes=30)
    fecha = request.args.get("fecha")
    if fecha:
        try:
            fecha = datetime.strptime(fecha, "%d/%m/%Y")
        except ValueError:
            return jsonify(
                messages="La fecha es invalida, use el formato dia/mes/año"
            ), 400
    else:
        fecha = datetime.today()
    if fecha.date() < datetime.today().date():
        return jsonify(
            messages="No se pueden ver turnos disponibles de fechas pasadas"
        ), 400
    json = []
    hora_ahora = datetime.now().time()
    td_ahora = timedelta(
        hours=hora_ahora.hour,
        minutes=hora_ahora.minute,
        seconds=hora_ahora.second,
    )
    for td in (abre + timedelta(minutes=30*it) for it in range(int(cant_t))):
        if td >= td_ahora or fecha > datetime.today():
            hora_fin = str(td + timedelta(minutes=30))
            if hora_fin.startswith("1 day, "):
                hora_fin = hora_fin.replace("1 day, ", "")
            hora_inicio = str(td)
            if hora_inicio.startswith("1 day, "):
                hora_inicio = hora_inicio.replace("1 day, ", "")
            turno_tomado = Turno.query.join(Center).filter(
                Center.id == id,
                Turno.hour_block == hora_inicio,
                Turno.date == datetime.strftime(fecha, "%Y-%m-%d"),
            ).first()
            if not turno_tomado:
                turnos = {
                    "hora_inicio": hora_inicio[0:-3],
                    "hora_fin": hora_fin[0:-3],
                    "centro_id": id,
                    "fecha": datetime.strftime(fecha, "%d/%m/%Y"),
                }
                json.append(turnos)
    return jsonify(datos=json)


@bp.route("/<int:id>/reserva", methods=["POST"])
def turnos_create(id):
    """
    Crea un turno con los datos Json que recibe a traves de post
    """
    centro = Center.query.filter_by(id=id).first()
    if(not centro):
        return jsonify(messages="El centro consultado no existe"), 404
    if(not centro.publication_state):
        return jsonify(messages="El centro consultado no esta publicado"), 400
    turno_json = {}
    try:
        json = request.get_json(force=True)
        fecha = datetime.strptime(json["fecha"], "%d/%m/%Y")
        if fecha.date() < datetime.today().date():
            return jsonify(
                messages="No se pueden tomar turnos de fechas pasadas"
            ), 400
        turno = Turno(
            center=id,
            email=json["email_donante"],
            phone_number=json["telefono_donante"],
            date=fecha,
            hour_block=json["hora_inicio"],
        )
        turno.validate_and_save()
        turno_json["id"] = turno.id
        turno_json["center"] = turno.center
        turno_json["email"] = turno.email
        turno_json["phone_number"] = turno.phone_number
        turno_json["date"] = json["fecha"]
        turno_json["hour_block"] = json["hora_inicio"]
    except (KeyError, AssertionError, ValueError) as err:
        return jsonify(messages=str(err)[:-1]), 400
    return jsonify(atributos=turno_json)


@bp.route("/<int:id>/", methods=["GET"])
def show(id):
    """
    Devuelve un centro especifico en formato Json
    """
    centro = Center.query.filter_by(id=id).first()
    if(not centro):
        return jsonify(messages="El centro consultado no existe"), 404
    if (not centro.publication_state):
        return jsonify(messages="El centro consultado no esta publicado"), 400
    coord = centro.coordinates.split(",")
    coord[0] = float(coord[0])
    coord[1] = float(coord[1])
    return jsonify(
                atributos={
                    "id": centro.id,
                    "nombre": centro.name,
                    "direccion": centro.address,
                    "telefono": centro.phone_number,
                    "hora_apertura": centro.opens_at.isoformat()[0:-3],
                    "hora_cierre": centro.close_at.isoformat()[0:-3],
                    "tipo": centro.types[0].name,
                    "web": centro.web,
                    "email": centro.email,
                    "coordenadas": coord,
                    "municipio": {
                        "id": centro.municipio
                    }
                }
            )
