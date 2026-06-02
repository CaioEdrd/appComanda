from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ItemComandaForm(FlaskForm):
    quantidade = IntegerField(
        "Quantidade",
        validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )

    submit = SubmitField("Atualizar item")