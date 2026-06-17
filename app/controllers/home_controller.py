from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.extensions import db
from app.models.comanda import Comanda
from app.models.item_comanda import ItemComanda
from app.models.produto import Produto
from app.forms.comanda_form import ComandaForm
from datetime import datetime
from flask_login import current_user, login_required


home_bp = Blueprint("home", __name__) #bp da home


@home_bp.route('/', methods=["GET", "POST"]) #rota home
@login_required
def home():
    produtos     = Produto.query.all() #select em todos os produtos
    form_comanda = ComandaForm() #intância o formulário da comanda

    if not form_comanda.itens.entries:
        for produto in produtos:
            form_comanda.itens.append_entry({
                "produto_id": produto.id,
                "nome":       produto.nome,
                "preco":      produto.preco_venda,
                "quantidade": 0,
            }) #Para cada produto, adiciona uma entrada no formulário com seus dados e quantidade zero.
    
    if form_comanda.validate_on_submit():
        if current_user.perfil != "garçom":
            flash("Apenas garçons podem abrir comandas.", "danger")
            return redirect(url_for("home.home"))

    if form_comanda.validate_on_submit(): #verifica se o formulário foi submetido
        itens, total = _processar_itens(form_comanda.itens.data) #Chama _processar_itens que retorna a lista de itens com quantidade maior que zero e o total calculado.    

        if not itens: #Se nenhum item foi selecionado, exibe aviso e redireciona.
            flash("Adicione ao menos um item à comanda.", "danger")
            return redirect(url_for("home.home"))

        if Comanda.query.filter_by(mesa=form_comanda.mesa.data, status="Aberta").first(): #select com base no status aberta
            flash("Mesa com comanda aberta!", "danger") #se a mesa estiver aberta, redireciona
            return redirect(url_for("home.home"))

        _salvar_comanda(form_comanda, itens, total)
        flash("Comanda aberta com sucesso!", "success") #Salva a comanda, exibe mensagem de sucesso e redireciona.
        return redirect(url_for("home.home"))

    return render_template(
        'pages/home.html',
        form_comanda=form_comanda,
        produtos=produtos,
        dataHoje=datetime.now(),
        **_stats_do_dia(),
    )

#funções auxiliares

def _processar_itens(itens_data: list) -> tuple[list[ItemComanda], float]: #Recebe lista de dados dos itens, retorna tupla com lista de ItemComanda e o total.
    itens = []
    total = 0.0

    for item_data in itens_data: #Percorre cada item do formulário.
        quantidade = item_data.get("quantidade") or 0 #Pega a quantidade. 
        if quantidade <= 0: #Se for zero ou negativa, pula o item.
            continue

        preco    = float(item_data["preco"])
        subtotal = quantidade * preco
        total   += subtotal

        itens.append(ItemComanda( #Cria um objeto ItemComanda com os dados e adiciona na lista.
            produto_id     = item_data["produto_id"],
            nome           = item_data["nome"],
            valor_unitario = preco,
            quantidade     = quantidade,
            subtotal       = subtotal,
        ))

    return itens, total


def _salvar_comanda(form: ComandaForm, itens: list[ItemComanda], total: float) -> None: #Recebe o formulário, lista de itens e total. Não retorna nada.

    comanda = Comanda( #Cria a comanda
        mesa       = form.mesa.data,
        cliente    = form.cliente.data,
        observacao = form.observacao.data,
        total      = total,
    )
    db.session.add(comanda) #adiciona na sessão 

    db.session.flush() #faz flush() para gerar o id antes de associar os itens.

    for item in itens: # associa cada item a ela e adiciona na sessão.
        item.comanda_id = comanda.id
        db.session.add(item)

    db.session.commit()


def _stats_do_dia() -> dict: #Retorna um dicionário com estatísticas gerais das comandas.
    return {
        "listaComandas":       Comanda.query.order_by(Comanda.id).all(),
        "ultimosCinco":        Comanda.query.order_by(Comanda.id.desc()).limit(5).all(),
        "total_abertas":       Comanda.query.filter_by(status="Aberta").count(),
        "total_pagas":         Comanda.query.filter_by(status="Paga").count(),
        "total_inadimplentes": Comanda.query.filter_by(status="Inadimplente").count(),
        "total_comandas":      Comanda.query.count(),
        "faturamento":         db.session.query(
                                   db.func.coalesce(db.func.sum(Comanda.total), 0)
                               ).scalar(),
    }