from app.models.configuration import Configuration as c
from math import ceil


def paginate(query, page):
    """
    Recibe como parametro una query y un número de página y devuelve una
    subquery en la que la cantidad de elementos son el valor de la
    configuracion 'global.paginacion' y el offset es el número de página
    """
    config_row = c.query.filter_by(name="global.paginacion").first()
    per_page = int(config_row.value)
    return query.limit(per_page).offset((get_page(page)-1) * per_page).all()


def get_page(page):
    """
    Retorna un entero del número de página que esta en los args de la request
    y si no esta el arg entonces retorna 1
    """
    if not page:
        return 1
    else:
        return int(page)


def number_of_pages(query):
    """
    Retorna el numero total de páginas de el parametro query
    """
    config_row = c.query.filter_by(name="global.paginacion").first()
    per_page = int(config_row.value)
    return ceil(len(query.all()) / per_page)
