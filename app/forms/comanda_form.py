from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, HiddenField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange


class ItemForm(FlaskForm):
    class Meta:
        csrf = False

    produto_id = HiddenField()
    nome       = HiddenField()
    preco      = HiddenField()
    quantidade = IntegerField(validators=[Optional(), NumberRange(min=0)], default=0)


class ComandaForm(FlaskForm):
    """Usado na criação e edição de comanda."""
    cliente    = StringField("Cliente", validators=[DataRequired()])
    mesa       = IntegerField("Mesa", validators=[DataRequired()])
    observacao = TextAreaField("Observação")
    status     = SelectField("Status", choices=[
        ("Aberta",       "Aberta"),
        ("Paga",         "Paga"),
        ("Inadimplente", "Inadimplente"),
    ])
    itens  = FieldList(FormField(ItemForm))
    submit = SubmitField("Salvar")  


class AdicionarItensForm(FlaskForm):
    """Usado apenas na página de detalhes para adicionar itens."""
    itens  = FieldList(FormField(ItemForm))
    submit = SubmitField("Adicionar itens")