from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class RecipesForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    image = FileField('Изображение')
    content = TextAreaField('Рецепт', validators=[DataRequired()])
    is_private = BooleanField('Личное')
    submit = SubmitField('Добавить')