from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class EditPerson(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    age = StringField('Возраст')
    city = StringField('Город')
    networks = StringField('Социльные сети')
    is_main = BooleanField('Основной состав')
    content = TextAreaField("информация")
    photo = FileField("Фото участинка")
    submit = SubmitField('Применить')