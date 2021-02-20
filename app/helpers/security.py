from flask import escape, session, current_app
import re
import uuid
import os
import jsonschema
from jsonschema import validate


# Esquema de como debe ser el json de un centro
center_schema = {
    "type": "object",
    "properties": {
        "nombre": {"type": "string"},
        "direccion": {"type": "string"},
        "telefono": {"type": "string"},
        "hora_apertura": {"type": "string"},
        "hora_cierre": {"type": "string"},
        "tipo": {"type": "string"},
        "web": {"type": "string"},
        "email": {"type": "string"},
        "municipio": {
            "type": "object",
            "oneOf": [
                {"properties": {"nombre": {"type": "string"}},
                    "required": ["nombre"]},
                {"properties": {"id": {"type": "number"}}, "required": ["id"]},
            ]
        },
        "coordenadas": {
            "type": "array",
            "items": [{"type": "number"}, {"type": "number"}]
        }
    },
    "required": [
        "nombre", "direccion", "telefono", "hora_apertura",
        "hora_cierre", "tipo", "web", "email", "municipio", "coordenadas",
    ],
    "additionalProperties": False,
}


def validate_json_center(json):
    """
    Valida que el json tenga el formato correcto para cargar un
    centro, devuelve los errores si los tiene, o un string vacío si el formato
    es correcto.
    """
    try:
        validate(instance=json, schema=center_schema)
    except jsonschema.exceptions.ValidationError as err:
        formato = (
            'El formato esperado es: \n'
            '{\n'
            '   "nombre": string,\n'
            '   "direccion": string,\n'
            '   "telefono": string\n'
            '   "hora_apertura": string\n'
            '   "hora_cierre": string\n'
            '   "tipo": string\n'
            '   "web": string\n'
            '   "email": string\n'
            '   "municipio": {\n'
            '       Una de las siguientes opciones\n'
            '       {"nombre": string\n'
            '       {"id": number}\n'
            '   },\n'
            '   "coordenadas":[number, number]\n'
            '}'
        )
        return f'{err.message}{formato}'
    return ""


def generate_token():
    """
    Genera un token para usar en formularios para evitar la tecnica
    csrf. Lo guarda en la sesión del usuario para asegurarse de poder
    volver a obtenerlo.
    """
    session["csrf_token"] = str(uuid.uuid1())
    return session["csrf_token"]


def check_token(token):
    """
    Verifica que el token ingresado sea el mismo que tiene el usuario.
    Retorna True si lo es, False caso contrario.
    """
    return token == session.get("csrf_token")


def string_escape(dato):
    """
    Devuelve el texto recibido como parámetro escapeado
    Ejemplo: "hola" COMO &#34;hola&#34;
    Devuelve el texto limpio.
    """
    return str(escape(dato))


def tag_escape(dato):
    """
    Limpia los tags declarados en script_list
    el texto que recibe.
    Ejemplo: <em> hola </em> COMO hola
    Devuelve el texto limpio.
    """
    tag_list = [
        "<b>", "</b>", "<i>", "</i>", "<u>", "</u>", "<em>", "</em>",
        "<strong>", "</strong>", "<object>", "</object>", "<embed>",
        "</embed>", "<link>", "</link>", "<script>", "</script>"
    ]
    dato1 = dato
    for element in tag_list:
        dato1 = re.sub(element, "", dato1, flags=re.IGNORECASE)
    return dato1


def sql_escape(dato):
    """
    Quita toda sentencia sql considerada en sql_list
    del texto original. También quita las ' sueltas al inicio, en
    el medio y al final. Ademas quita los espacios extras.
    Devuelve el texto limpio.
    """
    sql_list = [
        "' or ", '" or ', "' and ", '" and ', "' or '", '" or "',  "' and '",
        '" and "', "' or'", '" or"', "' and'", '" and"', '"or "', "'or '",
        '"and "', "'and '", "'or'", '"or"', "'and'", '"and"', "'='", '"="',
        "'--", '"--', "DROP", "SELECT *", "' UNION ", '" UNION', " FROM "
        ]
    dato1 = dato
    for element in sql_list:
        dato1 = re.sub(element, "", dato1, flags=re.IGNORECASE)
    dato1 = re.sub(" ' ", " ", dato1)
    dato1 = re.sub(' " ', " ", dato1)
    while ((dato1 != "") and (dato1[0] == "'")):
        dato1 = dato1.lstrip("'").strip(" ")
    while ((dato1 != "") and (dato1[-1] == "'")):
        dato1 = dato1.rstrip("'").strip(" ")
    return dato1


def sql_and_tag_escape(dato):
    """
    Quita toda sentencia sql y tag que se pueda encontrar en
    dato y devuelve el texto limpio.
    """
    return tag_escape(sql_escape(dato))


def name_is_valid(dato):
    """
    Verifica que un nombre tenga el formato válido
    Devuelve True si es válido, False si no lo es.
    """
    return (
        re.match(
            r"^(?=.{3,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$",
            dato)
    )


def is_only_text(dato):
    """
    Devuelve True si los caracteres que contiene el dato son
    sólamente de texto, False caso contrario.
    """
    return(
        re.match(
            r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$", dato
        )
    )


def is_only_text_and_numbers(dato):
    """
    Devuelve True si los caracteres que contiene el dato son
    sólamente de texto y números, False caso contrario.
    """
    return(
        re.match(
            r"^[a-zA-Z0-9]+(([',. -][a-zA-Z0-9 ])?[a-zA-Z0-9]*)*$",
            dato)
    )


def email_is_valid(email):
    """
    Retorna true si un mail tiene un formato valido, false si no
    """
    return (
        re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email)
    )


def validate_pdf(pdf_file):
    """
    Valida que el archivo recibido por parametro sea pdf
    Devuelve True si es valido o es None, Flaso otherwise
    """
    if pdf_file is not None:
        pdf_file.seek(0)
        if (
            (os.fstat(pdf_file.fileno()).st_size > 10485760) or
                (b'%PDF-' not in pdf_file.read(5))):  # 10485760=10MiB
            pdf_file.seek(0)
            return False
    pdf_file.seek(0)
    return True


def save_pdf_file(pdf, name):
    """
    Guarda el pdf que le pasan como parametro en la carpeta correspondiente
    """
    path = os.path.join(current_app.config["UPLOADS_PUBLIC_DIRECTORY"], name)
    pdf.save(path)


def delete_pdf_file(pdf_name):
    """
    Elimina el pdf que le pasen por parametro
    """
    path = os.path.join(
            current_app.config["UPLOADS_PUBLIC_DIRECTORY"],
            pdf_name
            )
    if os.path.exists(path):
        os.remove(path)


def formato_hora_valido(hora):
    return re.match(
            r"^(?:([01]?\d|2[0-3]):([0-5]?\d):)?([0-5]?\d)$", hora
        )
