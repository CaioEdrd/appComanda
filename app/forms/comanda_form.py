from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ComandaForm(FlaskForm):
    cliente = StringField(
        "Cliente",
        validators=[DataRequired()]
    )

    mesa = IntegerField(
        "Mesa",
        validators=[DataRequired()]
    )

    observacao = TextAreaField("Observação")

    submit = SubmitField("Nova Comanda")

    