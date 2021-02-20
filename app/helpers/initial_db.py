from app.models.configuration import Configuration as c
from app.models.role import Role as r
from app.models.permission import Permission as p
from app.models.user import User as u
from app.db import db_session
from app.models.type import Type as t
from app.models.state import State as s
from werkzeug.security import generate_password_hash

import time

# 6 rows
config_tables = [
    "home.titulo||""Donaciones COVID",
    "home.descripcion||Esta es la descripcion del sitio",
    "home.mail_de_contacto||contacto@example.com",
    "global.paginacion||13",
    "home.habilitado||TRUE",
    "home.mensaje_deshabilitado||El sitio se encuentra en mantenimiento"
]

# 2 roles
roles_table = [
    "administrador_del_sistema", "operador_centro_de_ayuda"
]

permissions_table = set([])

# Debe tener 22 permisos
admin_permissions_table = [
    "user_index", "user_new", "user_update", "user_destroy",
    "configuration_index", "configuration_update",
    "center_publicar", "center_despublicar", "center_index",
    "center_new", "center_update", "center_show",
    "center_destroy", "center_approve", "center_reject",
    "center_pending_index",
]

permissions_table.update(admin_permissions_table)

# Debe tener 15 permisos
operator_permissions_table = [
    "center_index", "center_new", "center_update", "center_show",
    "center_approve", "center_reject", "center_pending_index",
    "center_publicar", "center_despublicar", "center_turns_index",
    "turn_index", "turn_new", "turn_update", "turn_destroy", "turn_show"
]

# Deben quedar deben quedar 22 permisos (totales del sistema)
# roles_to_permissons deben ser 37 rows
permissions_table.update(operator_permissions_table)

# 5 tipos
types_table = [
    "Donacion_de_ropa", "Donacion_de_comida", "Merendero", "Otro",
    "Donacion_de_sangre_o_plasma"
]

# 4 estados
states = [
    "Aprobado", "Pendiente", "Rechazado", "Eliminado"
]


def load_database():
    """
    Carga los datos iniciales en la base de datos
    """
    start = time.time()
    data_loaded = False

    for row in states:
        row_exists = s.query.filter(s.name == row).first()
        if not row_exists:
            data_loaded = True
            new_state = s(name=row)
            db_session.add(new_state)

    for row in config_tables:
        columns = row.split("||")
        row_exists = c.query.filter(c.name == columns[0]).first()
        if not row_exists:
            data_loaded = True
            new_config = c(name=columns[0], value=columns[1])
            db_session.add(new_config)

    for row in permissions_table:
        row_exists = p.query.filter(p.name == row).first()
        if not row_exists:
            data_loaded = True
            new_permission = p(name=row)
            db_session.add(new_permission)

    for row in roles_table:
        row_exists = r.query.filter(r.name == row).first()
        if not row_exists:
            data_loaded = True
            new_role = r(name=row)
            db_session.add(new_role)

    for row in types_table:
        row_exists = t.query.filter(t.name == row).first()
        if not row_exists:
            data_loaded = True
            new_type = t(name=row)
            db_session.add(new_type)

    if data_loaded:
        db_session.commit()

    admin_role = r.query.filter(
        r.name == "administrador_del_sistema"
    ).first()
    for row in permissions_table:
        permission = p.query.filter(p.name == row).first()
        if permission not in admin_role.permissions:
            admin_role.permissions.append(permission)
            data_loaded = True
    operator_role = r.query.filter(
        r.name == "operador_centro_de_ayuda"
    ).first()
    for row in operator_permissions_table:
        permission = p.query.filter(p.name == row).first()
        if permission not in operator_role.permissions:
            operator_role.permissions.append(permission)
            data_loaded = True

    admin_exists = u.query.filter(u.username == "admin").first()
    if not admin_exists:
        data_loaded = True
        new_user = u(
            first_name="Admin",
            password=generate_password_hash("admin123"),
            email="admin@gmail.com",
            last_name="Gonzalez",
            username="admin"
        )
        db_session.add(new_user)

    if data_loaded:
        db_session.commit()

    admin_exists = u.query.filter(u.username == "admin").first()
    role = r.query.filter(
        r.name == "administrador_del_sistema"
    ).first()
    admin_exists.roles.append(role)
    db_session.commit()

    end = time.time()
    if data_loaded:
        print("Tiempo de carga de base de datos inicial: " + str(end - start))
