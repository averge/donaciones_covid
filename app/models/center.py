from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Table,
    ForeignKey,
    Time,
    DateTime
)
from sqlalchemy.orm import relationship
from app.db import base, db_session
from app.helpers.security import (
    sql_and_tag_escape,
    email_is_valid,
    validate_pdf,
    formato_hora_valido,
)
from werkzeug.utils import secure_filename
from datetime import datetime
import re
import uuid

centers_to_types = Table(
    'centers_to_types',
    base.metadata,
    Column('center_id', Integer, ForeignKey('center.id')),
    Column('type_id', Integer, ForeignKey('type.id'))
)


class Center(base):
    """
    Modelo que representa a la tabla Centro de la base de datos,
    que guarda los centros
    """
    __tablename__ = "center"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)
    opens_at = Column(Time, nullable=False)
    close_at = Column(Time, nullable=False)
    types = relationship(
        "Type",
        secondary=centers_to_types,
        back_populates="centers"
    )
    municipio = Column(Integer, nullable=False)
    web = Column(String(255))
    email = Column(String(255))
    state = Column(Integer, ForeignKey('state.id'))
    publication_state = Column(Boolean, default=False)
    protocolo = Column(String(255))
    coordinates = Column(String(255))
    turnos = relationship("Turno")
    delete_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, default=datetime.now,
        onupdate=datetime.now)

    def __repr__(self):
        return '<Centro %r>' % self.name

    def validate_email(self):
        """
        Valida el email
        """
        if self.email != '':
            if email_is_valid(self.email):
                return ""
            else:
                return "El email no tiene un formato valido,"
        else:
            return ""

    def validate_phone(self):
        """
        Valida el numero de telefono, devuelve un string vacio si es valido
        """
        self.phone_number = sql_and_tag_escape(self.phone_number)
        phone = self.phone_number.replace('+', '').replace('(', '').replace(
            ')', '').replace('-', '').replace(' ', '')
        if not (phone.isnumeric()) or not (9 < len(phone) < 17):
            return "Numero de telefono invalido,"
        return ""

    def validate_url(self):
        """
        Valida la url, devuelve un string vacio si es valida
        """

        if self.web == '':
            return ""
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}' +
            r'[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not re.match(regex, self.web):
            return (
                "Direccion web invalida." +
                " Utilice el formato: http://ejemplo.com,"
                )
        return ""

    def validate_opens_closes(self):
        """
        Validador de los campos opens_at y closes_at
        Retorna errores cuando cierra antes de abrir y cuando son invalidos
        Si es valido retorna un string vacio
        """

        try:
            if formato_hora_valido(self.opens_at):
                self.opens_at = self.opens_at[0:self.opens_at.rfind(":")]
            if formato_hora_valido(self.close_at):
                self.close_at = self.close_at[0:self.close_at.rfind(":")]
            self.opens_at = datetime.strptime(
                                        self.opens_at, '%H:%M').time()
            self.close_at = datetime.strptime(
                                        self.close_at, '%H:%M').time()
        except ValueError:
            return (
                "Los horarios ingresados son invalidos. Por favor"
                " comuniquese con el administrador del sistema,"
                )

        if self.close_at == self.opens_at:
            return (
                    "El horario de cierre no puede ser el mismo que"
                    " el de apertura,"
                    )
        return ""

    def validate_protocol(self, pdf):
        """
        Valida el protocolo y guarda el nombre de manera segura y con el uuid
        Retorna string vacio si es valido
        """
        if pdf is None:
            return ""
        if validate_pdf(pdf):
            self.protocolo = (
                f"{secure_filename(pdf.filename)[:-4]}"
                f"_{str(uuid.uuid4())}.pdf"
            )
            return ""
        else:
            return "El archivo de visitas debe ser PDF menor a 10MB,"

    def validate_coordinates(self):
        """
        Valida las coordenadas: Devuelve string vacio si son validas
        """
        try:
            self_lat = float(self.coordinates.split(",")[0])
            self_lng = float(self.coordinates.split(",")[1])
        except ValueError:
            return "No se pueden convertir las coordenadas,"
        latitud = {"min": -55.959729, "max": -21.787168}
        longitud = {"min": -73.477843, "max": -53.658506}  # aprox. Argentina

        if not ((latitud["min"] < self_lat < latitud["max"]) and
                (longitud["min"] < self_lng < longitud["max"])):
            return "Las coordenadas no corresponden al territorio habilitado,"
        return ""

    def validate_municipio(self):
        """
        Valida que el municipio no este vacio y
        checkea que el municipio este en la api
        """
        if (self.municipio is None or not self.municipio.strip()):
            return "El municipio no puede estar vacio,"
        if not self.municipio.isnumeric():
            return "Error en la carga del municipio,"
        # Api check
        url = "https://api-referencias.proyecto2020.linti.unlp.edu.ar/"
        import requests
        munis = requests.get(f"{url}municipios?per_page=300")
        if munis.status_code != 200:
            return (
                "Error en la api de municipios. Por favor"
                " comuniquese con el administrador del sistema,"
                )
        ciudades = munis.json()["data"]["Town"]
        if not (
            int(self.municipio) in [
                mun_dic["id"] for mun_dic in ciudades.values()
            ]
        ):
            return(
                    "El municipio no es valido,"
                )

        return ""

    def validate_name(self):
        """
        Valida que el campo del nombre no este vacio
        Retorna un string vacio si es valido
        """
        if not self.name.strip():
            return "El nombre no puede ser vacio,"
        return ""

    def validate_address(self):
        """
        Valida que el campo de la direccion no este vacio
        Retorna un string vacio si es valido
        """
        if not self.address.strip():
            return "La direccion no puede estar vacia,"
        return ""

    def tiene_turnos_futuros(self):
        """
        Si tiene turnos futuros devuelve TRUE,
        si NO tiene turnos futuros devuelve FALSE
        """
        from app.models.turno import Turno as T

        if (T.query.filter(
                T.center == self.id,
                T.date > datetime.now().date()).count() != 0):
            return True
        if (T.query.filter(
                T.center == self.id,
                T.date == datetime.now().date(),
                T.hour_block > datetime.now().time()).count() != 0):
            return True
        return False

    def validate_and_save(self, update=False, pdf=None):
        """
        Valida que el centro creado/modificado tenga formato válido.
        Si es válido lo actualiza en la base de datos, caso contrario
        devuelve los errores que existieron en las validaciones.
        """
        errors = ""

        self.web = sql_and_tag_escape(self.web)
        self.name = sql_and_tag_escape(self.name)
        self.address = sql_and_tag_escape(self.address)
        self.municipio = sql_and_tag_escape(self.municipio)
        errors += self.validate_name()
        errors += self.validate_address()
        errors += self.validate_email()
        errors += self.validate_phone()
        errors += self.validate_url()
        errors += self.validate_opens_closes()
        errors += self.validate_coordinates()
        errors += self.validate_municipio()
        errors += self.validate_protocol(pdf)

        if not update:
            db_session.add(self)
        if errors:
            raise AssertionError(errors)
        db_session.commit()
