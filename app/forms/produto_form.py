from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProdutoForm(FlaskForm): #formulário de produto
    nome = StringField(
        "Nome",
        validators=[DataRequired()]
    )

    preco_venda = DecimalField( #campo decimal para o preço
        "Preço do produto",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ]
    )

    submit = SubmitField("Cadastrar produto")