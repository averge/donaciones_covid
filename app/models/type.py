from app.db import base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .center import centers_to_types


class Type(base):
    """
    Modelo que representa a la tabla Type de la base de datos,
    que guarda los tipos de cetro de ayuda
    """
    __tablename__ = "type"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    centers = relationship(
        "Center",
        secondary=centers_to_types,
        back_populates="types"
    )

    def __repr__(self):
        return '<tipo %r>' % self.name
