from app.models.user import User


def user_permissions(user_name):
    """
    Retorna los permisos sin repetir del usuario al que el nombre de usuario
    pasado como parametro estan asignados
    """
    user = User.query.filter_by(username=user_name).first()
    permision_list = set([])
    for role in user.roles:
        for permission in role.permissions:
            permision_list.add(permission.name)
    return (permision_list)
