from app.db import base, db_session
from app.helpers.security import (
    name_is_valid, is_only_text, email_is_valid
)
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Table,
    ForeignKey
)
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

import datetime


def validate_username(user):
    """
    Valida que el nombre de usuario no se encuentre vacío y que no exista
    para otro usuario en el sistema. En caso de que suceda alguna de las dos
    retorna un mensaje de error. Si no sucede ninguna retorna un string
    vacío para indicar que no hay error.
    """
    if not user.username.strip():
        return "El nombre de usuario no puede ser vacio,"

    if User.query.filter(User.username == user.username).first():
        return "El nombre de usuario ya existe,"

    if not name_is_valid(user.username):
        return "El nombre de usuario no tiene un formato válido,"

    return ""


def validate_email(user):
    """
    Valida que el mail del usuario no se encuentre vacío y que no exista
    para otro usuario en el sistema. En caso de que suceda alguna de las
    dos retorna un mensaje de error. Si no sucede ninguna retorna un
    string vacío para indicar que no hay error.
    """

    if not user.email.strip():
        return "El email no puede ser vacio,"

    if User.query.filter(User.email == user.email).first():
        return "El email ya existe,"

    if not email_is_valid(user.email):
        return "El email no tiene un formato valido,"

    return ""


def validate_first_name(user):
    """
    Valida que el nombre del usuario no se encuentre vacío En caso de que
    suceda retorna un mensaje de error. Si no sucede retorna un string
    vacío para indicar que no hay error.
    """
    if not user.first_name.strip():
        return "El nombre no puede ser vacio,"

    if not is_only_text(user.first_name):
        return ("El nombre no puede contener caracteres especiales,")

    return ""


def validate_last_name(user):
    """
    Valida que el apellido del usuario no se encuentre vacío En caso de que
    suceda retorna un mensaje de error. Si no sucede retorna un string
    vacío para indicar que no hay error.
    """
    if not user.last_name.strip():
        return "El apellido no puede ser vacio,"

    if not is_only_text(user.last_name):
        return ("El apellido no puede contener caracteres especiales,")

    return ""


def validate_password(user):
    """
    Valida que la contraseña del usuario no se encuentre vacía, y que tenga
    entre 5 y 32 caracteres En caso de que suceda alguna retorna un mensaje de
    error. Si no sucede retorna un string vacío para indicar que no hay error
    """
    if not user.password:
        return "El password no puede ser vacio,"

    if len(user.password) < 4 or len(user.password) > 32:
        return "El password debe tener entre 4 y 32 caracteres,"

    return ""


users_to_roles = Table(
    'users_to_roles',
    base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
)


class User(base):
    """
    Modelo que representa a la tabla User de la base de datos,
    que guarda los usuarios
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now,
        onupdate=datetime.datetime.now)
    first_name = Column(String(255))
    last_name = Column(String(255))
    roles = relationship(
        "Role",
        secondary=users_to_roles,
        back_populates="users"
    )

    def validate_and_save(self, update=False, password_change=False):
        """
        Valida que el usuario creado/modificado tenga formato válido.
        Si es válido lo actualiza en la base de datos, caso contrario
        devuelve los errores que existieron en las validaciones.
        """
        errors = ""
        errors += validate_first_name(self)
        errors += validate_last_name(self)

        if not update:
            errors += validate_username(self)
            errors += validate_email(self)
            errors += validate_password(self)
            self.password = generate_password_hash(self.password)
            db_session.add(self)
        elif password_change:
            errors += validate_password(self)
            self.password = generate_password_hash(self.password)
        if errors:
            raise AssertionError(errors)

        db_session.commit()

    def __repr__(self):
        return '<Usuario %r>' % self.first_name + ' ' + self.last_name

    def check_password(self, pass_check):
        """
        Chequea la contrasenia en forma de hash
        """
        return check_password_hash(self.password, pass_check)

    def es_activo(self):
        """
        Devuelve si el usuario esta activo
        """
        return self.activo

    def has_permission_to(self, f_name):
        """
        Devuelve True si el usuario puede realizar la funcion f_name
        """

        for role in self.roles:
            if role.puede_hacer(f_name):
                return True
        return False

    def es_admin(self):
        """
        Devuelve True si el usuario es administrador del sistema
        """
        for role in self.roles:
            if "administrador_del_sistema" == role.name:
                return True
        return False

    def es_operador(self):
        """
        Devuelve True si el usuario es operador de un centro de ayuda
        """
        for role in self.roles:
            if "operador_centro_de_ayuda" == role.name:
                return True
        return False

    def has_role(self, this_role):
        for role in self.roles:
            if this_role == role.name:
                return True
        return False
