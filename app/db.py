from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import config, ENVIRONMENT


engine = create_engine(
    config[ENVIRONMENT].SQLALCHEMY_DATABASE_URI,
    convert_unicode=True
)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
base = declarative_base()
base.query = db_session.query_property()


def init_db():
    """
    Crea las tablas en la base de datos si no existen
    """
    from app.models.user import User  # noqa: F401
    from app.models.role import Role  # noqa: F401
    from app.models.permission import Permission  # noqa: F401
    from app.models.configuration import Configuration  # noqa: F401
    from app.models.center import Center  # noqa: F401
    from app.models.type import Type  # noqa: F401
    from app.models.state import State  # noqa: F401
    from app.models.turno import Turno  # noqa: F401
    base.metadata.create_all(bind=engine)
