from flask import redirect, render_template, Blueprint, request, url_for, flash
from app.db import db_session
from app.helpers.flash_messages import flash_messages
from app.models.configuration import Configuration, validate
from app.helpers.auth import login_required, permission_check
from app.helpers.security import (
    sql_and_tag_escape, check_token, generate_token
)

bp = Blueprint('configuration', __name__, url_prefix="/configuration")


@bp.route("/", methods=['GET'])
@login_required
@permission_check
def index():
    """
    Vista del formulario de configuración
    """
    configurations = Configuration.query.order_by(Configuration.name).all()
    configs = {}
    first_name = ''
    for element in configurations:
        name = element.name.split('.')
        if first_name != name[0]:
            first_name = name[0]
            configs_content = []
            configs[name[0]] = configs_content
        content_elements = [element.name, element.value]
        configs[name[0]].append(content_elements)
    CSRF_TOKEN = generate_token()
    return render_template(
        "configuration/configuration.html",
        configs=configs,
        CSRF_TOKEN_STRING=CSRF_TOKEN
    )


@bp.route("/update", methods=["POST"])
@login_required
@permission_check
def update():
    """
    Actualiza la configuracion a partir de los campos rellenados en el
    formulario de configuracion o flashea un mensaje de error si falla
    alguna validacion
    """
    if(check_token(request.form["csrf_token"])):
        CSRF_TOKEN = request.form["csrf_token"]
        form = request.form.copy()
        if "home.habilitado" in request.form.keys():
            form["home.habilitado"] = "TRUE"
        else:
            form["home.habilitado"] = "FALSE"
        errors = ""
        del form["csrf_token"]
        for element in form:
            original = Configuration.query.filter_by(name=element).first()
            original.value = sql_and_tag_escape(form[element])
            error = validate(original)
            if error:
                errors += error
        if not errors:
            flash("Configuración guardada correctamente", "success")
            db_session.commit()
            return redirect(url_for("configuration.index"))
        else:
            flash_messages(errors)
            configurations = Configuration.query.order_by(
                Configuration.name
            ).all()
            configs = {}
            first_name = ''
            for element in configurations:
                name = element.name.split('.')
                if first_name != name[0]:
                    first_name = name[0]
                    configs_content = []
                    configs[name[0]] = configs_content
                content_elements = [element.name, form[element.name]]
                configs[name[0]].append(content_elements)
            return(render_template(
                "configuration/configuration.html",
                configs=configs,
                CSRF_TOKEN_STRING=CSRF_TOKEN
            ))
    else:
        return render_template("configuration/configuration.html")
