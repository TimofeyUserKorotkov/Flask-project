from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField, SelectField
from wtforms import BooleanField, SubmitField

from wtforms.validators import DataRequired


class RecipesForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Рецепт', validators=[DataRequired()])
    category = SelectField('Категория', 
                           choices=['Завтрак', 'Обед', 'Ужин', 'Перекус'], 
                           validators=[DataRequired()])
    is_private = BooleanField('Личное')
    submit = SubmitField('Добавить')