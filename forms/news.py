from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    name = StringField('Название кастинга', validators=[DataRequired()])
    content = TextAreaField("Текст редактора")
    submit = SubmitField('Применить')