from flask import Blueprint, render_template, session, request, flash, redirect
from app.models.user import User
from app.helpers.auth import login_required
from app.models.configuration import Configuration
from app.helpers.security import (
    string_escape, check_token, generate_token
)

bp = Blueprint('auth', __name__)


@bp.route("/login", methods=['GET', 'POST'])
def login():
    """"
    Dependiendo del metodo HTTP devuelve el html o autentica
    tambien chequea si esta activo
    """
    if request.method == 'GET':
        if (session.get('username')):
            return redirect(location='/')
        CSRF_TOKEN = generate_token()
        return render_template("auth/login.html", CSRF_TOKEN_STRING=CSRF_TOKEN)
    else:
        if(check_token(request.form["csrf_token"])):
            params = request.form

            user = User.query.filter(
                User.username == string_escape(params["username"])
            ).first()

            if ((not user) or not(user.check_password(params["password"]))):
                flash("Usuario o clave incorrecto.", "error")
                return redirect("login")
            if not(user.es_activo()):
                flash("Usuario inactivo.", "error")
                return(redirect("/login"))
            if ((
                Configuration.query.filter_by(
                        name="home.habilitado").first().value == "FALSE"
            ) and (not(user.es_admin()))):
                flash(
                    "Sitio en mantenimiento, disculpe las molestias.", "error"
                )
                return(redirect("/"))
            session["username"] = user.username
            flash("La sesión se inició correctamente.", "success")
            return(redirect("/"))
        else:
            return redirect("/login")


@bp.route("/logout")
@login_required
def logout():
    """Cerrar sesion"""
    del session["username"]
    session.clear()
    flash("La sesión se cerró correctamente.", "success")
    return(redirect("/"))
