from flask import (
    request,
    Blueprint,
    render_template,
    redirect, url_for,
    flash,
    abort,
    )
from app.models.center import Center
from app.models.type import Type
from app.models.state import State
from app.helpers.auth import login_required, permission_check
from app.helpers.security import (
     sql_and_tag_escape,
     check_token,
     generate_token,
     save_pdf_file,
     delete_pdf_file,
     )
from app.db import db_session
from app.helpers.flash_messages import flash_messages
from app.helpers.paginate import number_of_pages, paginate, get_page
from datetime import datetime, timedelta
import requests


bp = Blueprint('centers', __name__, url_prefix="/centers")


@bp.route('/', methods=['GET'])
@login_required
@permission_check
def index():
    """
    Retorna todos los centros aprobados para su publicacion, paginados a
    partir los parametros de la request
    """
    query = Center.query
    searchQ = {}
    estado = request.args.get("estado")
    if not estado:
        query = query.join(State).filter(State.name == "Aprobado")
    else:
        query = query.join(State).filter(State.name == estado)

    busqueda = request.args.get("busqueda")
    if busqueda:
        busqueda = sql_and_tag_escape(busqueda)
        query = query.filter(Center.name.like("%" + busqueda + "%"))
    else:
        busqueda = ""

    searchQ["busqueda"] = busqueda
    searchQ["estado"] = estado
    page = request.args.get("page")
    estados = State.query.all()
    return render_template(
        'center/index.html',
        centros=paginate(query, page),
        total_pages=number_of_pages(query),
        current_page=get_page(page),
        searchQ=searchQ,
        estados=estados,
    )


@bp.route('/new', methods=['GET', 'POST'])
@login_required
@permission_check
def new():
    """
    Vista de creacion de un centro de ayuda, devuelve la vista en el metodo
    GET o valida en el metodo POST, si la validacion es correcta guarda
    el centro en la base, si no flashea mensajes de error de las
    validaciones que fallaron
    """

    if (request.method == 'POST'):
        if not (check_token(request.form["csrf_token"])):
            return render_template(
                'centers/new.html',
                center_types=Type.query.order_by(Type.name).all(),
                )
        form = request.form
        nuevo_centro = Center(
            name=form['nombre-centro'],
            address=form['direccion'],
            phone_number=form['phone'],
            opens_at=f"{form['opens_at_hour']}:{form['opens_at_min']}",
            close_at=f"{form['close_at_hour']}:{form['close_at_min']}",
            municipio=form["muni"],
            coordinates=f"{form['lat']},{form['lng']}"
        )
        nuevo_centro.types.append(
            Type.query.filter_by(name=form["tipo"]).first())
        if "email" in form:
            nuevo_centro.email = form["email"]
        if "web" in form:
            nuevo_centro.web = form["web"]
        if "publication_state" in form:
            nuevo_centro.publication_state = True
        # Solo pueden acceder usuarios con permisos
        estado = State.query.filter_by(name="Aprobado").first()
        estado.centers.append(nuevo_centro)
        msj = "Centro cargado correctamente."

        try:
            if request.files["protocolo"]:
                # Validate and save si tiene pdf
                nuevo_centro.validate_and_save(pdf=request.files["protocolo"])
                save_pdf_file(
                    request.files["protocolo"], nuevo_centro.protocolo)
            else:
                # Validate and save si no tiene pdf
                nuevo_centro.validate_and_save()
            flash(msj, "success")
            return redirect(url_for('centers.index'))
        except AssertionError as e:
            flash_messages(str(e))
            return render_template(
                'center/new.html',
                last_form=request.form,
                center_types=Type.query.order_by(Type.name).all(),
                )

        return redirect('/center')
    else:  # method=GET
        CSRF_TOKEN = generate_token()
        return render_template(
            '/center/new.html',
            center_types=Type.query.order_by(Type.name).all(),
            CSRF_TOKEN_STRING=CSRF_TOKEN,
            )


@bp.route("/pending", methods=['GET'])
@login_required
@permission_check
def pending_index():
    """
    Vista que permite ver únicamente los centros en estado Pendiente
    """
    centers = Center.query.join(State).filter(State.name == "Pendiente")
    search = request.args.get("busqueda")
    if search:
        search = sql_and_tag_escape(search)
        centers = centers.filter(Center.name.like("%" + search + "%"))
    else:
        search = ""
    page = request.args.get("page")
    return render_template(
        'center/pending.html',
        centros=paginate(centers, page),
        total_pages=number_of_pages(centers),
        current_page=get_page(page),
        search=search,
    )


@bp.route("/<string:id>/turns", methods=['GET'])
@login_required
@permission_check
def turns_index(id):
    """
    Vista de todos los turnos de un centro especifico para un dia especifico
    """
    from app.models.turno import Turno
    center = Center.query.filter_by(id=id).first()
    if not center:
        abort(404)
    date = request.args.get("fecha")
    if date:
        fecha_send = date
    else:
        fecha_send = datetime.strftime(datetime.now(), "%d/%m/%Y")
    fecha = datetime.strptime(fecha_send, "%d/%m/%Y")
    cierra = timedelta(
        hours=center.close_at.hour,
        minutes=center.close_at.minute,
        seconds=center.close_at.second,
    )
    abre = timedelta(
        hours=center.opens_at.hour,
        minutes=center.opens_at.minute,
        seconds=center.opens_at.second,
    )
    if cierra < abre:
        cierra += timedelta(minutes=1440)
    cant_t = (cierra - abre) / timedelta(minutes=30)
    turns1 = []
    turns2 = []
    turns = []
    mixed = False
    for td in (abre + timedelta(minutes=30*it) for it in range(int(cant_t))):
        hora_inicio = str(td)
        if hora_inicio.startswith("1 day, "):
            hora_inicio = hora_inicio.replace("1 day, ", "")
            mixed = True
        turno = Turno.query.filter(
            Turno.center == id,
            Turno.hour_block == hora_inicio,
            Turno.date == datetime.strftime(fecha, "%Y-%m-%d")
        ).first()
        if not turno:
            hora_fin = str(td + timedelta(minutes=30))
            if hora_fin.startswith("1 day, "):
                hora_fin = hora_fin.replace("1 day, ", "")
            turno = Turno(
                id=-1,
                hour_block=datetime.strptime(hora_inicio, "%H:%M:%S").time(),
                email="",
                phone_number="",
                date=fecha.date(),
                center=center.id
            )
        if mixed:
            turns1.append(turno)
        else:
            turns2.append(turno)
    if mixed:
        turns = turns1
        turns.extend(turns2)
    else:
        turns = turns2
    today = datetime.now().date()
    today_show = datetime.strftime(datetime.now(), "%d/%m/%Y")
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = datetime.strftime(tomorrow, "%d/%m/%Y")
    day_after_tomorrow = datetime.now() + timedelta(days=2)
    day_after_tomorrow = datetime.strftime(day_after_tomorrow, "%d/%m/%Y")
    return render_template(
        'center/turns.html', center=center,
        today=today, tomorrow=tomorrow, today_show=today_show,
        day_after_tomorrow=day_after_tomorrow,
        time_now=datetime.now().time(),
        date=fecha_send, turns=turns, mixed=mixed,
    )


@bp.route("/<string:id>/approve", methods=['POST'])
@login_required
@permission_check
def approve(id):
    """
    Método para aprobar un centro de ayuda
    """
    center = Center.query.filter_by(id=id).first()
    if not center:
        abort(404)
    center.publication_state = True
    estado = State.query.filter_by(name="Pendiente").first()
    estado.centers.remove(center)
    estado = State.query.filter_by(name="Aprobado").first()
    estado.centers.append(center)
    db_session.commit()
    from_page = request.form["from_page"]
    if from_page == "pending":
        return redirect(url_for('centers.pending_index'))
    elif from_page == "center_show":
        return redirect(url_for('centers.show', id=id))


@bp.route("/<string:id>/reject", methods=['POST'])
@login_required
@permission_check
def reject(id):
    """
    Método para rechazar un centro de ayuda.
    """
    center = Center.query.filter_by(id=id).first()
    if not center:
        abort(404)
    center.publication_state = False
    estado = State.query.filter_by(name="Pendiente").first()
    estado.centers.remove(center)
    estado = State.query.filter_by(name="Rechazado").first()
    estado.centers.append(center)
    db_session.commit()
    from_page = request.form["from_page"]
    if from_page == "pending":
        return redirect(url_for('centers.pending_index'))
    elif from_page == "center_show":
        return redirect(url_for('centers.show', id=id))


@bp.route("/<string:id>/destroy", methods=['GET', 'POST'])
@login_required
@permission_check
def destroy(id):
    """
    Eliminar un centro de la base de datos
    """
    centers = Center.query.filter_by(id=id).first()
    if not centers:
        abort(404)
    centers.state = 4
    centers.delete_date = datetime.now()
    centers.publication_state = False
    db_session.commit()
    return redirect(url_for('centers.index'))


@bp.route("/<string:id>/show", methods=['GET'])
@login_required
@permission_check
def show(id):
    """
    Muestra un centro de ayuda especifico
    """
    center = Center.query.filter_by(id=id).first()
    if not center:
        abort(404)
    url = "https://api-referencias.proyecto2020.linti.unlp.edu.ar/"
    munis = requests.get(url + "municipios?per_page=300")
    for m in munis.json()["data"]["Town"].values():
        if int(m['id']) == int(center.municipio):
            muni_nombre = m['name']
    return render_template(
        "center/show.html", center=center, muni_nombre=muni_nombre)


@bp.route("/<string:id>/publicar", methods=['POST'])
@login_required
@permission_check
def publicar(id):
    """
    Metodo para cambiar el estado de publicacion de un metodo a
    'Publicado'
    """
    center = Center.query.filter_by(id=id).first()
    if not center:
        abort(404)
    center.publication_state = True
    db_session.commit()
    return redirect(url_for('centers.show', id=id))


@bp.route("/<string:id>/despublicar", methods=['POST'])
@login_required
@permission_check
def despublicar(id):
    """
    Metodo para cambiar el estado de publicacion de un metodo a
    'Despublicado'
    """
    center = Center.query.filter_by(id=id).first()
    if not center:
        abort(404)
    center.publication_state = False
    db_session.commit()
    return redirect(url_for('centers.show', id=id))


@bp.route('/<string:center_id>/update', methods=['GET', 'POST'])
@login_required
@permission_check
def update(center_id):
    """
    Actualiza el Centro pasado por la url
    """
    center = Center.query.filter_by(id=center_id).first()
    if not center:
        abort(404)
    if (request.method == 'POST'):
        if not (check_token(request.form["csrf_token"])):
            CSRF_TOKEN = generate_token()
            return render_template(
                "center/update.html",
                center=center,
                center_types=Type.query.order_by(Type.name).all(),
                CSRF_TOKEN_STRING=CSRF_TOKEN
                )
        else:
            CSRF_TOKEN = request.form["csrf_token"]
            form = request.form
            center.name = form['nombre-centro']
            center.address = form['direccion']
            center.phone_number = form['phone']
            center.municipio = form["muni"]
            center.coordinates = f"{form['lat']},{form['lng']}"
            if center.types[0].name != form['tipo']:
                center.types.remove(center.types[0])
                center.types.append(
                    Type.query.filter_by(name=form["tipo"]).first())
            if "email" in form:
                center.email = form["email"]
            if "web" in form:
                center.web = form["web"]

            if "publication_state" in form:
                if center.state == 1:
                    center.publication_state = True
                else:
                    center.publication_state = False

            if center.state == 3:
                estado = State.query.filter_by(name="Rechazado").first()
                estado.centers.remove(center)
                estado = State.query.filter_by(name="Pendiente").first()
                estado.centers.append(center)

            if (
                (
                    center.opens_at != (
                                        datetime.strptime(
                                            f"{form['opens_at_hour']}"
                                            f":{form['opens_at_min']}",
                                            '%H:%M').time()
                    ) or (
                    center.close_at != (datetime.strptime(
                                            f"{form['close_at_hour']}"
                                            f":{form['close_at_min']}",
                                            '%H:%M').time())
                    ))):  # Si se intenta modificar algun horario:
                if center.tiene_turnos_futuros():
                    flash(
                        "No se puede actualizar el horario del centro si le"
                        " quedan turnos futuros", "error")
                    return render_template(
                            'center/update.html',
                            center=center,
                            center_types=Type.query.order_by(Type.name).all(),
                            CSRF_TOKEN_STRING=CSRF_TOKEN
                            )

            center.opens_at = (
                                f"{form['opens_at_hour']}:"
                                f"{form['opens_at_min']}"
                                )
            center.close_at = (
                                f"{form['close_at_hour']}:"
                                f"{form['close_at_min']}"
                                )
            try:
                if request.files["protocolo"]:
                    # Validate and save si tiene pdf
                    if center.protocolo:
                        delete_pdf_file(center.protocolo)
                    center.validate_and_save(
                        update=True,
                        pdf=request.files["protocolo"])
                    save_pdf_file(
                        request.files["protocolo"], center.protocolo)
                else:
                    # Validate and save si no tiene pdf
                    center.validate_and_save(update=True)
                flash("Centro actualizado correctamente.", "success")
                return redirect(url_for('centers.index'))
            except AssertionError as e:
                flash_messages(str(e))

                return render_template(
                    'center/update.html',
                    center=center,
                    center_types=Type.query.order_by(Type.name).all(),
                    CSRF_TOKEN_STRING=CSRF_TOKEN
                    )
    else:  # Method: GET
        CSRF_TOKEN = generate_token()
        return render_template(
            "center/update.html",
            center_types=Type.query.order_by(Type.name).all(),
            CSRF_TOKEN_STRING=CSRF_TOKEN,
            center=center
            )
