from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
import db_working

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтверждение пароля', validators=[DataRequired(), EqualTo('password')])
    lastname = StringField('Фамилия', validators=[DataRequired()])
    firstname = StringField('Имя', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])
    submit = SubmitField('Отправить')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня', default=True)
    submit = SubmitField('Войти')

class Databoard_searchform(FlaskForm):
    types = db_working.get_ticket_types()
    #types.insert(0,(' ', ' '))
    ticket_types = SelectField('Category', choices= types)
    start_date = DateField('Начало')
    end_date = DateField('Окончание')
    is_done = BooleanField('Включая закрытые')