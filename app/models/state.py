from app.db import base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship


class State(base):
    """
    Modelo que representa a la tabla Centro de la base de datos,
    que guarda los centros
    """
    __tablename__ = "state"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    centers = relationship('Center')

    def __repr__(self):
        return '<Estado %r>' % self.name
