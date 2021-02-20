from app.db import base
from .role import roles_to_permissions
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Permission(base):
    """
    Modelo que representa a la tabla Permission de la base de datos,
    que guarda la los permisos que pueden ser asignados a los roles
    """
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    roles = relationship(
        "Role",
        secondary=roles_to_permissions,
        back_populates="permissions"
    )

    def __repr__(self):
        return '<Permiso %r>' % self.name
