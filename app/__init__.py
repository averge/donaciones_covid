from flask import Flask, render_template, Response
from app.db import db_session, init_db
from app.helpers.initial_db import load_database
from flask_scss import Scss
from flask_session import Session
from config import config, ENVIRONMENT, UPLOADS_PUBLIC_DIRECTORY
from werkzeug.http import dump_cookie
from flask_cors import CORS


class CookiesLaxResponse(Response):
    def set_cookie(self, *args, **kwargs):
        cookie = dump_cookie(*args, **kwargs)
        if (
            'samesite' in kwargs and kwargs['samesite'] is None or
            'samesite' not in kwargs
        ):
            cookie = "{}; {}".format(cookie, 'SameSite=Lax;')

        self.headers.add(
            'Set-Cookie',
            cookie
        )


def create_app(environment="development"):
    """
    Setup de la aplicacion
    """

    app = Flask(__name__)

    app.response_class = CookiesLaxResponse

    # Compilacion de archivos scss
    Scss(app, static_dir='app/static', asset_dir='app/assets/scss')

    cors = CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        support_credentials=True
    )

    app.config['CORS_HEADERS'] = 'Content-Type'

    # Configuracion de variables de flask
    app.config.from_object(config[ENVIRONMENT])

    # Inicializacion de la base de datos
    init_db()
    load_database()

    # Global de jinja para obtener los permisos en navbar
    from app.helpers.permission import user_permissions
    app.jinja_env.globals.update(user_permissions=user_permissions)
    from app.helpers.auth import check_login
    app.jinja_env.globals.update(check_login=check_login)
    # Global de jinja para el path de los archivos publicos
    app.jinja_env.globals.update(
        UPLOADS_PUBLIC_DIRECTORY=UPLOADS_PUBLIC_DIRECTORY.replace('./app', ''))

    # Reglas de ruteo
    from app.resources import user
    app.register_blueprint(user.bp)
    from app.resources import auth
    app.register_blueprint(auth.bp)
    from app.resources import configuration
    app.register_blueprint(configuration.bp)
    from app.resources import center
    app.register_blueprint(center.bp)
    from app.resources.api import center as center_api
    app.register_blueprint(center_api.bp)
    from app.resources.api import tipo as tipo_api
    app.register_blueprint(tipo_api.bp)
    from app.resources.api import configuration as configuration_api
    app.register_blueprint(configuration_api.bp)
    from app.resources.api import statistics as statistics_api
    app.register_blueprint(statistics_api.bp)
    from app.resources import turn
    app.register_blueprint(turn.bp)

    # Config de la sesion
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # Config del directorio publico de archivos
    app.config["UPLOADS_PUBLIC_DIRECTORY"] = UPLOADS_PUBLIC_DIRECTORY

    @app.route('/')
    def home():
        """
        Página inicial del sistema.
        """
        from app.models.configuration import Configuration as Config
        config = Config.query.filter(Config.name.like('home%')).all()
        homeConfig = {}
        from app.helpers.auth import desloguear_usuario_inactivo
        from app.models.user import User
        from flask import session
        if check_login():
            desloguear_usuario_inactivo(
                User.query.filter(User.username == session["username"]).first()
            )
        for element in config:
            homeConfig[element.name] = element.value
        return (render_template('home.html', homeConfiguration=homeConfig))

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """
        Codigo para que se puede bajar la base de datos automaticamente
        """
        db_session.remove()

    return app
