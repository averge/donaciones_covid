from flask import redirect, render_template, Blueprint, request, url_for, flash
from flask import session, abort
from app.db import db_session
from app.helpers.flash_messages import flash_messages
from app.models.user import User, validate_email
from app.models.role import Role
from app.helpers.auth import login_required, permission_check
from app.helpers.paginate import paginate, number_of_pages, get_page
from app.helpers.security import (
    sql_escape, sql_and_tag_escape, check_token, generate_token
)

bp = Blueprint('users', __name__, url_prefix="/users")


@bp.route("/", methods=['GET'])
@login_required
@permission_check
def index():
    """
    Vista del listado de usuarios, retorna los usuarios paginados y filtra
    a partir de los argumentos de busqueda si hay alguno
    """
    query = User.query
    searchQ = {}
    activos = request.args.get("no_activos")
    if not activos:
        query = query.filter(User.activo == "1")

    busqueda = request.args.get("username")
    if busqueda:
        busqueda = sql_and_tag_escape(busqueda)
        query = query.filter(User.username.like("%" + busqueda + "%"))
    else:
        busqueda = ""

    searchQ["busqueda"] = busqueda
    searchQ["no_activo"] = "checked" if activos else ""

    page = request.args.get("page")
    return render_template(
        "user/index.html",
        users=paginate(query, page),
        total_pages=number_of_pages(query),
        current_page=get_page(page),
        searchQ=searchQ
    )


@bp.route("/new", methods=['POST', 'GET'])
@login_required
@permission_check
def new():
    """
    Vista de creacion de un usuario, devuelve la vista en el metodo GET o
    valida en el metodo POST, si la validacion es correcta guarda el usuario
    en la base, si no flashea mensajes de error de las validaciones que
    fallaron
    """
    if (request.method == 'POST'):
        if(check_token(request.form["csrf_token"])):
            nuevoUsuario = User(
                first_name=(sql_escape(request.form["nombre"])),
                password=request.form["password"],
                email=request.form["email"],
                last_name=(sql_escape(request.form["apellido"])),
                username=(request.form["usuario"])
            )
            try:
                nuevoUsuario.validate_and_save()
                flash("Usuario creado correctamente", "success")
                return redirect(url_for('users.index'))
            except AssertionError as e:
                flash_messages(str(e))
                return render_template('user/new.html', last_form=request.form)
        else:
            return render_template('user/new.html')
    else:
        CSRF_TOKEN = generate_token()
        return render_template("user/new.html", CSRF_TOKEN_STRING=CSRF_TOKEN)


def update_role(form, role, user):
    """
    Actualiza el rol
    """
    if role.name in form.keys() and form[role.name] == "on":
        user.roles.append(role)
    else:
        if role in user.roles:
            (user.roles.remove(role))


@bp.route("/<string:username>/update", methods=['GET', 'POST'])
@login_required
@permission_check
def update(username):
    """
    Vista de actualizacion de un usuario, devuelve la vista en el metodo GET o
    valida en el metodo POST, si la validacion es correcta actualiza el usuario
    en la base, si no flashea mensajes de error de las validaciones que
    fallaron
    """
    if (request.method == 'POST'):
        roles_query = Role.query.all()
        if(check_token(request.form["csrf_token"])):
            CSRF_TOKEN = request.form["csrf_token"]
            user = User.query.filter_by(
                username=request.form["usuario"]
            ).first()
            if (not user) or (user.username != username):
                flash("Hubo un error, por favor intente nuevamente", "error")
                return redirect(url_for("users.index"))
            user.first_name = (sql_escape(request.form["nombre"]))
            user.last_name = (sql_escape(request.form["apellido"]))
            if request.form["email"] != user.email:
                user.email = request.form["email"]
                if validate_email(user):
                    flash(validate_email(user)[:-1], "error")
                    return render_template(
                        'user/update.html',
                        user=user,
                        CSRF_TOKEN_STRING=CSRF_TOKEN, roles=roles_query,
                        new_form=False
                    )

            if (
                not user.es_admin() or
                (user.es_admin() and not user.es_activo())
            ):
                if (
                    "activo" in request.form.keys() and
                    request.form["activo"] == "on"
                ):
                    user.activo = True
                else:
                    user.activo = False

            for role in roles_query:
                if (role.name == 'administrador_del_sistema'):
                    if not (session.get('username') == user.username):
                        update_role(request.form, role, user)
                else:
                    update_role(request.form, role, user)

            new_password = False
            if request.form["password"]:
                if user.check_password(request.form["password"]):
                    if request.form["newPassword"]:
                        new_password = True
                        user.password = request.form["newPassword"]
                    else:
                        flash("Debe ingresar un nuevo password", "error")
                        return render_template(
                            'user/update.html',
                            user=user,
                            CSRF_TOKEN_STRING=CSRF_TOKEN, roles=roles_query,
                            new_form=False
                        )
                else:
                    flash("El password ingresado no es correcto", "error")
                    return render_template(
                        'user/update.html',
                        user=user,
                        CSRF_TOKEN_STRING=CSRF_TOKEN, roles=roles_query,
                        new_form=False
                    )

            try:
                user.validate_and_save(
                    update=True,
                    password_change=new_password
                )
                flash("Usuario modificado correctamente", "success")
                return redirect(url_for('users.index'))
            except AssertionError as e:
                flash_messages(str(e))
                return render_template(
                    'user/update.html',
                    user=user,
                    CSRF_TOKEN_STRING=CSRF_TOKEN, roles=roles_query,
                    new_form=False
                )
        else:
            return render_template("user/update.html", user=user)
    else:
        CSRF_TOKEN = generate_token()
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404)
        roles_query = Role.query.all()
        return render_template(
            "user/update.html",
            user=user,
            CSRF_TOKEN_STRING=CSRF_TOKEN,
            roles=roles_query, new_form=True
        )


@bp.route("/<string:username>/destroy", methods=['GET', 'POST'])
@login_required
@permission_check
def destroy(username):
    """
    Eliminar un usuario de la base de datos
    """
    users = User.query.filter_by(username=username).first()
    if not users:
        abort(404)
    # Si llega hasta aca para eliminarse, chequea que no se elimine a si mismo
    if users.username == session.get("username"):
        flash("No se puede eliminarse a si mismo.", "error")
        return redirect(url_for('users.index'))
    db_session.delete(users)
    db_session.commit()
    return redirect(url_for('users.index'))


@bp.route("/<string:username>/show", methods=['GET'])
@login_required
def show(username):
    """
    Muestra un usuario especifico
    """
    usuario = User.query.filter_by(username=username).first()
    if not usuario:
        abort(404)
    return render_template("user/show.html", user=usuario)
