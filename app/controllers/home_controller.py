from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.extensions import db
from app.models.comanda import Comanda
from app.models.item_comanda import ItemComanda
from app.models.produto import Produto
from app.forms.comanda_form import ComandaForm
from datetime import datetime

home_bp = Blueprint("home", __name__)


@home_bp.route('/', methods=["GET", "POST"])
def home():
    produtos     = Produto.query.all()
    form_comanda = ComandaForm()

    # Popula os itens apenas no GET
    if request.method == "GET":
        for produto in produtos:
            form_comanda.itens.append_entry({
                "produto_id": produto.id,
                "nome":       produto.nome,
                "preco":      produto.preco_venda,
                "quantidade": 0,
            })

    if form_comanda.validate_on_submit():
        itens, total = _processar_itens(form_comanda.itens.data)

        if not itens:
            flash("Adicione ao menos um item à comanda.", "danger")
            return redirect(url_for("home.home"))

        if Comanda.query.filter_by(mesa=form_comanda.mesa.data, status="Aberta").first():
            flash("Mesa com comanda aberta!", "danger")
            return redirect(url_for("home.home"))

        _salvar_comanda(form_comanda, itens, total)
        flash("Comanda aberta com sucesso!", "success")
        return redirect(url_for("home.home"))

    return render_template(
        'pages/home.html',
        form_comanda=form_comanda,
        produtos=produtos,
        dataHoje=datetime.now(),
        **_stats_do_dia(),
    )


def _processar_itens(itens_data: list) -> tuple[list[ItemComanda], float]:
    itens = []
    total = 0.0

    for item_data in itens_data:
        quantidade = item_data.get("quantidade") or 0
        if quantidade <= 0:
            continue

        preco    = float(item_data["preco"])
        subtotal = quantidade * preco
        total   += subtotal

        itens.append(ItemComanda(
            produto_id     = item_data["produto_id"],
            nome           = item_data["nome"],
            valor_unitario = preco,
            quantidade     = quantidade,
            subtotal       = subtotal,
        ))

    return itens, total


def _salvar_comanda(form: ComandaForm, itens: list[ItemComanda], total: float) -> None:
    comanda = Comanda(
        mesa       = form.mesa.data,
        cliente    = form.cliente.data,
        observacao = form.observacao.data,
        total      = total,
    )
    db.session.add(comanda)
    db.session.flush()

    for item in itens:
        item.comanda_id = comanda.id
        db.session.add(item)

    db.session.commit()


def _stats_do_dia() -> dict:
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