from flask_wtf import FlaskForm #Importa a classe base FlaskForm que integra WTForms 
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, HiddenField, FieldList, FormField, SelectField #importa os tipos de campos
from wtforms.validators import DataRequired, Optional, NumberRange #importa validadores


class ItemForm(FlaskForm):  #Formulário de cada item. 
    class Meta:
        csrf = False # desativa a proteção CSRF porque ele é um subformulário embutido dentro de outro — o CSRF já é tratado pelo formulário pai.
    #Campos ocultos que carregam os dados do produto sem aparecer para o usuário na tela.
    produto_id = HiddenField()
    nome       = HiddenField()
    preco      = HiddenField()
    #Campo de quantidade, opcional, mínimo zero, começa em zero por padrão.
    quantidade = IntegerField(validators=[Optional(), NumberRange(min=0)], default=0)

class ComandaForm(FlaskForm): #formulário de criação da comanda
    cliente    = StringField("Cliente", validators=[DataRequired()]) #cliente - texto - obrigatório
    mesa       = IntegerField("Mesa", validators=[DataRequired()]) #mesa - inteiro 0 obrigatório
    observacao = TextAreaField("Observação") #observação - texto 
    itens      = FieldList(FormField(ItemForm)) #lista de itens
    submit     = SubmitField("Salvar")


class EditarComandaForm(FlaskForm): #formulário de edição da comanda
    cliente    = StringField("Cliente", validators=[DataRequired()])
    mesa       = IntegerField("Mesa", validators=[DataRequired()])
    observacao = TextAreaField("Observação")
    status     = SelectField("Status", choices=[
        ("Aberta",       "Aberta"),
        ("Paga",         "Paga"),
        ("Inadimplente", "Inadimplente"), #seleção do status na edição da comanda
    ])
    submit     = SubmitField("Salvar")


class AdicionarItensForm(FlaskForm): #"Usado apenas na página de detalhes para adicionar itens.
    itens  = FieldList(FormField(ItemForm))
    submit = SubmitField("Adicionar itens")