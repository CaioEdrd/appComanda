# app/forms/user_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, SelectField
from wtforms.validators import DataRequired, EqualTo

class LoginForm(FlaskForm):
    email = EmailField(
        "E-mail",
        validators=[DataRequired()]
    )
    senha = PasswordField(
        "Senha",
        validators=[DataRequired()]
    )
    submit = SubmitField("Entrar")


class UserForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[DataRequired()]
    )
    email = EmailField(
        "E-mail",
        validators=[DataRequired()]
    )
    senha = PasswordField(
        "Senha",
        validators=[DataRequired()]
    )
    confirma_senha = PasswordField(
        "Confirmar Senha",
        validators=[DataRequired(), EqualTo("senha", message="As senhas não coincidem")]
    )
    perfil = SelectField(
        "Perfil",
        validators=[DataRequired()],
        choices=["admin", "garçom"]
    )
    submit = SubmitField("Criar conta")