from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class SearchPerson(FlaskForm):
    search_info = StringField('Поиск')
    submit = SubmitField('Найти')