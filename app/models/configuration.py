from app.db import base
from sqlalchemy import (
    Column,
    String,
    DateTime,
)
import datetime


class Configuration(base):
    """
    Modelo que representa a la tabla Configuration de la base de datos,
    que guarda la configuración del sistema
    """
    __tablename__ = "configuration"

    name = Column(String(255), primary_key=True)
    value = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now,
        onupdate=datetime.datetime.now)

    def __repr__(self):
        return '<Configuracion %r>' % self.name + ':' + self.value


def validate(fila):
    """
    Valida que los atributos de la clase configuracion no sean vacíos,
    y que si alguno tiene un formato en especial, lo cumpla
    """
    from app.helpers.security import email_is_valid
    if not fila.value.strip():
        return(
            " El campo " +
            fila.name.split(".")[1] +
            " no puede ser vacío,")
    elif ("mail" in fila.name):
        if not email_is_valid(fila.value):
            return ("El mail de contacto debe ser un mail válido,")
    elif ("paginacion" in fila.name):
        try:
            int(fila.value)
            if int(fila.value) < 1:
                return("El valor de paginación debe ser mayor a 0,")
        except ValueError:
            return ("La paginación solo puede ser un número entero,")
    else:
        return("")
