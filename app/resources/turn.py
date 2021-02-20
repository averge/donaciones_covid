from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from app.models.turno import Turno
from app.models.center import Center
from app.helpers.auth import (
    login_required,
    permission_check,
)
from app.helpers.security import (
    sql_and_tag_escape,
    generate_token,
    check_token,
)
from app.db import db_session
from app.helpers.flash_messages import flash_messages
from app.helpers.paginate import number_of_pages, paginate, get_page
from datetime import datetime


bp = Blueprint('turns', __name__, url_prefix="/turns")


@bp.route('/', methods=['GET'])
@login_required
@permission_check
def index():
    """
    Muestra la barra de busqueda de turnos,
    por defecto busca turnos que aun no pasaron y por email
    """
    query = Turno.query
    searchQ = {}
    page = request.args.get("page")
    buscar = request.args.get("buscar")
    tipo = request.args.get("tipo_busqueda")
    searchQ["tipo"] = tipo
    if buscar:
        buscar = sql_and_tag_escape(buscar)

        searchQ["buscar"] = buscar
        if tipo == "email":
            query = query.filter(Turno.email.like(f"%{buscar}%"))
        elif tipo == "nombre_centro":
            query = query.join(Center).filter(Center.name.like(f"%{buscar}%"))

        antiguos = request.args.get("antiguos")
        searchQ["antiguos"] = "checked" if antiguos else ""
        if not antiguos:
            query = query.filter(Turno.date >= datetime.now().date())
    else:
        query = query.filter(Turno.id == -1)
    centers = {c.id: c.name for c in Center.query.all()}
    return render_template(
        'turn/index.html',
        turns=paginate(query, page),
        total_pages=number_of_pages(query),
        current_page=get_page(page),
        searchQ=searchQ,
        centros=centers
    )


@bp.route('/new', methods=['GET', 'POST'])
@login_required
@permission_check
def new():
    """
    Metodo para crear un nuevo turno
    Se debe mandar en el get los parametros inciales.
    """
    if request.method == 'POST':
        try:
            form = request.form
            center_id = form["center-id"]
            date = form["date"]
            start_hour = f"{form['start-hour']}:{form['start-minute']}:00"
            CSRF_TOKEN = form["csrf_token"]
            center_name = Center.query.filter_by(id=center_id).first().name
            start_hour = datetime.strptime(
                start_hour,
                "%H:%M:%S")
            start_hour = datetime.strftime(start_hour, "%H:%M")
            date_center = datetime.strptime(form["date"], "%Y-%m-%d")
            if(not check_token(CSRF_TOKEN)):
                error = "Cómo perdiste el token csrf?? Acá tenes otro ¬.¬"
                error += " No lo pierdas..."
                flash(error, "error")
                return render_template(
                    'turn/new.html', center_id=center_id,
                    center_name=center_name,
                    date=date, start_hour=start_hour
                )
            new_turn = Turno(
                center=form["center-id"],
                email=form["email"],
                phone_number=form["phone"],
                date=date_center,
                hour_block=start_hour,
            )
            new_turn.validate_and_save()
            date = date_center.date().strftime("%d/%m/%Y")
            flash("Turno creado correctamente", "success")
            return redirect(url_for(
                'centers.turns_index', id=center_id,
                fecha=date)
            )
        except ValueError:
            flash(
                "No se pudo guardar el turno. Intente nuevamente.",
                "error")
            return redirect(url_for("centers.index"))
        except AttributeError:
            center_name = ""
            error = (
                "El centro no existe, por favor vuelva a la vista de" +
                " turnos de un centro para seleccionar un nuevo turno")
            flash(error, "error")
            return redirect(url_for('centers.index'))
        except AssertionError as e:
            flash_messages(str(e))
            return render_template(
                'turn/new.html', center_id=center_id,
                center_name=center_name, date=date,
                start_hour=start_hour, last_form=request.form,
                CSRF_TOKEN_STRING=CSRF_TOKEN,
                )
    elif request.method == 'GET':
        try:
            center_id = request.args.get("center_id")
            date = request.args.get("date")
            start_hour = request.args.get("start_hour")
            CSRF_TOKEN = generate_token()
            center_name = Center.query.filter_by(id=center_id).first().name
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(start_hour, "%H:%M:%S")
            return render_template(
                'turn/new.html', center_id=center_id, center_name=center_name,
                date=date, start_hour=start_hour, CSRF_TOKEN_STRING=CSRF_TOKEN
            )
        except (AttributeError, ValueError):
            flash(
                "Hubo un error, intente nuevamente crear un turno",
                "error"
            )
            return redirect(url_for('centers.index', id=center_id))


@bp.route('/<int:id>/show/', methods=['GET'])
@login_required
@permission_check
def show(id):
    """
    Muestra un turno en especifico (por id)
    """
    turno = Turno.query.filter_by(id=sql_and_tag_escape(str(id))).first()
    if not turno:
        abort(404)
    return render_template(
        'turn/show.html',
        turno=turno,
        centro=(Center.query.filter_by(id=turno.center).first().name)
    )


@bp.route('/<int:id>/destroy', methods=['POST'])
@login_required
@permission_check
def destroy(id):
    """
    Elimina un turno especifico de la base de datos
    """
    turno = Turno.query.filter_by(id=sql_and_tag_escape(str(id))).first()
    if not turno:
        abort(404)
    db_session.delete(turno)
    db_session.commit()
    return redirect(url_for('turns.index'))


@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
@permission_check
def update(id):
    centers = {
        center.id: center.name for center in Center.query.filter_by(
            publication_state=True)
    }
    hours = [
        "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
        "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
        "20", "21", "22", "23"]
    if request.method == 'POST':
        form = request.form
        CSRF_TOKEN = form["csrf_token"]
        if not (check_token(request.form["csrf_token"])):
            return redirect(url_for('turns.update', id=id))
        if (not form["center-id"].isnumeric()) or (int(
            form["center-id"]) not in centers.keys()
        ):
            flash("El centro no existe o esta deshabilitado", "error")
            return redirect(url_for('turns.show', id=id))
        try:
            turn = Turno.query.filter_by(id=id).first()
            old_turn = Turno.query.filter_by(id=id).first()
            new_date = datetime.strptime(form["datepicker"], "%d/%m/%Y")
            new_hour = f"{form['start-hour']}:{form['start-minute']}"
            datetime.strptime(new_hour, "%H:%M")
            if not turn:
                abort(400)
            turn.phone_number = form["phone"]
            turn.email = form["email"]
            turn.center = int(form["center-id"])
            turn.date = new_date
            turn.hour_block = new_hour
            turn.validate_and_save(update=True)
            flash("El turno se modificó correctamente", "success")
            return redirect(url_for('turns.show', id=turn.id))
        except ValueError:
            flash("La hora debe tener formato de H:M:S", "error")
            flash("La fecha debe tener formado de DD/MM/YYYY", "error")
            send_date = old_turn.date.strftime("%d/%m/%Y")
            send_hour = old_turn.hour_block
            return render_template(
                'turn/update.html', turn=turn, hours=hours,
                date=send_date, hour_block=send_hour,
                centers=centers, CSRF_TOKEN_STRING=CSRF_TOKEN
                )
        except AttributeError:
            error = (
                "El centro no existe, por favor vuelva a la vista de" +
                " turnos de un centro para seleccionar un nuevo turno")
            flash(error, "error")
            return render_template(
                'turn/update.html', turn=turn, hours=hours,
                date=form["datepicker"], hour_block=send_hour,
                centers=centers, CSRF_TOKEN_STRING=CSRF_TOKEN
            )
        except AssertionError as e:
            flash_messages(str(e))
            new_hour += ":00"
            send_hour = datetime.strptime(new_hour, "%H:%M:%S")
            return render_template(
                'turn/update.html', turn=turn, hours=hours,
                date=form["datepicker"], hour_block=send_hour,
                centers=centers, CSRF_TOKEN_STRING=CSRF_TOKEN)
    elif request.method == 'GET':
        turn = Turno.query.filter_by(id=id).first()
        if not turn:
            abort(400)
        CSRF_TOKEN = generate_token()
        date = turn.date.strftime("%d/%m/%Y")
        hour_block = turn.hour_block
        return render_template(
            'turn/update.html', turn=turn, hours=hours, date=date,
            hour_block=hour_block,
            centers=centers, CSRF_TOKEN_STRING=CSRF_TOKEN)
