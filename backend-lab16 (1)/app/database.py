from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine("sqlite:///chat.db", echo=True)   # echo=True prints every SQL statement
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass
