from functools import wraps
from flask import session, redirect, abort, flash
from app.models.user import User


def check_login():
    """
    Devuelve True si hay un usuario logueado
    """
    if session.get("username") is None:
        return False
    return True


def desloguear_usuario_inactivo(user):
    """
    Desloguea al usuario si esta inactivo
    """
    if not (user.es_activo()):
        del session["username"]
        session.clear()
        flash("Usuario inactivo.", "error")
        return redirect("/")


def login_required(f):
    """
    Wrapper/Decorator que se puede aplicar a metodos para chequear logueo
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_login():
            return redirect("/login", code=307)
        user = User.query.filter(User.username == session["username"]).first()
        if not user.es_activo():
            return desloguear_usuario_inactivo(user)
        return f(*args, **kwargs)
    return decorated_function


def permission_check(base_f):
    """
    Wrapper/Decorator que se puede aplicar a metodos y chequea los permisos
    del usuario logueado y redirige a 403 en caso de no tener permisos
    correspondientes a la accion que se quiera realizar.
    """
    @wraps(base_f)
    def decorated_function(*args, **kwargs):
        if not check_login():
            return redirect("/login", code=307)
        user = User.query.filter(User.username == session["username"]).first()
        if not user.es_activo():
            return desloguear_usuario_inactivo(user)

        f = base_f.__module__.split('.')[-1] + '_' + base_f.__name__
        if not (user.has_permission_to(f)):
            abort(403)
        return base_f(*args, **kwargs)
    return decorated_function
