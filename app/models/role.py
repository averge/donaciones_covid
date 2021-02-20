from app.db import base
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from .user import users_to_roles

roles_to_permissions = Table(
    'roles_to_permissions',
    base.metadata,
    Column('role_id', Integer, ForeignKey('role.id')),
    Column('permission_id', Integer, ForeignKey('permission.id'))
)


class Role(base):
    """
    Modelo que representa a la tabla Role de la base de datos,
    que guarda los roles que pueden tener los usuarios
    """
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    users = relationship(
        "User",
        secondary=users_to_roles,
        back_populates="roles"
    )
    permissions = relationship(
        "Permission",
        secondary=roles_to_permissions,
        back_populates="roles"
    )

    def __repr__(self):
        return '<Rol %r>' % self.name

    def puede_hacer(self, f_name):
        """
        Devuelve True si el rol tiene permiso para realizar la funcion pasada
        por parametro
        """

        for perm in self.permissions:
            if (f_name) == perm.name:
                return True
        return False
