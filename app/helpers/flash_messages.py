from flask import flash


def flash_messages(messages):
    """
    Flashea muchos mensajes pasados como parametros tal que cada mensaje
    termina con un caracter ','
    """
    array = messages[:-1].split(",")
    for message in array:
        flash(message, "error")
