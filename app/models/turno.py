from app.db import base, db_session
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Time,
    Date,
    DateTime
)
from app.helpers.security import email_is_valid, sql_and_tag_escape
from app.models.center import Center
from datetime import datetime


def validate_turno_tomado(turno):
    """
    Valida que el turno pasado por parametro no colisione en cuanto a
    fecha, hora y centro con otro turno
    """
    turno_tomado = Turno.query.join(Center).filter(
            Center.id == turno.center,
            Turno.hour_block == turno.hour_block,
            Turno.date == datetime.strftime(turno.date, "%Y-%m-%d"),
        ).first()
    if turno_tomado:
        if (turno.id) and (turno.id == turno_tomado.id):
            return ""
        return "El turno ya esta tomado,"
    return ""


def validate_email(turno):
    """
    Valida que el turno pasado por parametro tenga un email valido
    """
    if not turno.email.strip():
        return "El email no puede ser vacio,"

    if not email_is_valid(turno.email):
        return "El email no tiene un formato valido,"

    return ""


def validate_phone_number(turno):
    """
    Valida que el turno pasado por parametro tenga un formato valido
    """
    turno.phone_number = sql_and_tag_escape(turno.phone_number)
    phone = turno.phone_number.replace('+', '').replace('(', '').replace(
        ')', ''
    ).replace('-', '').replace(' ', '')
    if not (phone.isnumeric()) or not (9 < len(phone) < 17):
        return "Numero de telefono invalido,"
    return ""


def validate_hora_correcta(turno):
    """
    Valida que el turno pasado por parametro tenga hora y fecha que aun no
    hayan pasado y que este dentro del rango horario del centro
    """
    center = Center.query.filter_by(id=turno.center).first()
    abre = center.opens_at
    cierra = center.close_at
    bloque_datetime = datetime.strptime(turno.hour_block, "%H:%M")
    bloque = bloque_datetime.time()
    hora_ahora = datetime.now().time()
    fecha_hoy = datetime.now()

    if bloque < hora_ahora and turno.date <= fecha_hoy:
        return "No se puede sacar turnos que ya pasaron,"

    if abre < cierra:
        if bloque < abre or bloque >= cierra:
            return "La hora no esta entre las horas permitidas del centro,"
    else:
        if bloque < abre and bloque >= cierra:
            return "La hora no esta entre las horas permitidas del centro,"
    return ""


def validate_centro_disponible(turno):
    """
    Valida que el centro exista o este disponible,
    devuelve un string vacio si es valido
    """
    centro = Center.query.filter_by(id=turno.center).first()
    if centro and centro.publication_state:
        return ""
    return "El centro no existe o no esta disponible,"


class Turno(base):
    """
    Modelo que representa a la tabla Turno de la base de datos,
    que guarda los centros
    """
    __tablename__ = "turno"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    center = Column(Integer, ForeignKey('center.id'))
    hour_block = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, default=datetime.now,
        onupdate=datetime.now)

    def validate_and_save(self, update=False):
        """
        Valida y guarda un turno, si falla levanta AssertionError
        con los errores encontrados
        """
        errors = ""
        errors += validate_turno_tomado(self)
        errors += validate_email(self)
        errors += validate_phone_number(self)
        errors += validate_hora_correcta(self)
        errors += validate_centro_disponible(self)
        if errors:
            raise AssertionError(errors)
        if not update:
            db_session.add(self)
        db_session.commit()

    def __repr__(self):
        return '<Turno %r>' % self.date
