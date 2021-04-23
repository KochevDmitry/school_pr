import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Casting(SqlAlchemyBase):
    __tablename__ = 'castings'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    name_cast = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation('User')