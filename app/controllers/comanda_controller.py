from flask import Blueprint, render_template, redirect, flash, url_for, request
from app.extensions import db
from app.models.comanda import Comanda
from app.models.item_comanda import ItemComanda
from app.models.produto import Produto
from app.forms.item_editar_form import ItemComandaForm
from app.forms.comanda_form import ComandaForm, ItemForm, AdicionarItensForm
from datetime import datetime

comanda_bp = Blueprint("comanda", __name__)


@comanda_bp.route('/<int:id>', methods=["GET", "POST"])
def detalhe_comanda(id):
    comanda  = Comanda.query.get_or_404(id)
    produtos = Produto.query.all()
    form     = AdicionarItensForm()  # ✅ sem cliente/mesa obrigatórios

    if request.method == "GET":
        for produto in produtos:
            form.itens.append_entry({
                "produto_id": produto.id,
                "nome":       produto.nome,
                "preco":      produto.preco_venda,
                "quantidade": 0,
            })

    if form.validate_on_submit():
        adicionou_algum = False

        for item_data in form.itens.data:
            quantidade = item_data.get("quantidade") or 0
            if quantidade <= 0:
                continue

            item_existente = ItemComanda.query.filter_by(
                comanda_id=comanda.id,
                produto_id=item_data["produto_id"],
            ).first()

            if item_existente:
                item_existente.quantidade += quantidade
                item_existente.subtotal    = item_existente.quantidade * item_existente.valor_unitario
            else:
                db.session.add(ItemComanda(
                    comanda_id     = comanda.id,
                    produto_id     = item_data["produto_id"],
                    nome           = item_data["nome"],
                    valor_unitario = float(item_data["preco"]),
                    quantidade     = quantidade,
                    subtotal       = quantidade * float(item_data["preco"]),
                ))

            adicionou_algum = True

        if adicionou_algum:
            db.session.flush()
            comanda.recalcular_total()
            db.session.commit()
            flash("Itens adicionados com sucesso!", "success")
        else:
            flash("Nenhum item selecionado.", "warning")

        return redirect(url_for('comanda.detalhe_comanda', id=id))

    fim          = comanda.horarioPagamento if comanda.horarioPagamento else datetime.now()
    tempo_aberta = str(fim - comanda.horarioPedido).split(".")[0]

    return render_template(
        'pages/comanda_detalhe.html',
        comanda=comanda,
        tempo_aberta=tempo_aberta,
        produtos=produtos,
        form=form,
    )


@comanda_bp.route('/<int:id>/editar', methods=["GET", "POST"])
def editar_comanda(id):
    comanda      = Comanda.query.get_or_404(id)
    form_comanda = ComandaForm(obj=comanda)

    if form_comanda.validate_on_submit():
        comanda.cliente = form_comanda.cliente.data
        comanda.mesa    = form_comanda.mesa.data

        # Só permite mudar status se ainda estiver aberta
        if comanda.status == "Aberta":
            comanda.status = form_comanda.status.data  # adicione o campo no form se necessário

        if comanda.status in ("Paga", "Inadimplente"):
            if not comanda.horarioPagamento:
                comanda.horarioPagamento = datetime.now()

        db.session.commit()
        flash("Comanda editada com sucesso!", "success")
        return redirect(url_for('home.home'))

    return render_template('pages/comanda_editar.html', comanda=comanda, form_comanda=form_comanda)


@comanda_bp.route('/<int:id>/apagar', methods=["POST"])  # ✅ POST, não GET
def apagar_comanda(id):
    comanda = Comanda.query.get_or_404(id)
    db.session.delete(comanda)
    db.session.commit()
    flash("Comanda apagada com sucesso!", "success")
    return redirect(url_for('home.home'))


@comanda_bp.route('/<int:comanda_id>/item/<int:item_id>/editar', methods=["GET", "POST"])
def editar_item(comanda_id, item_id):
    comanda  = Comanda.query.get_or_404(comanda_id)
    item     = ItemComanda.query.get_or_404(item_id)
    form     = ItemComandaForm(obj=item)  # ✅ instância, não a classe

    if form.validate_on_submit():
        item.quantidade = form.quantidade.data
        item.subtotal   = item.quantidade * item.valor_unitario
        comanda.recalcular_total()
        db.session.commit()
        flash("Item atualizado com sucesso!", "success")
        return redirect(url_for('comanda.detalhe_comanda', id=comanda_id))

    return render_template('pages/item_editar.html', comanda=comanda, item=item, form=form)


@comanda_bp.route('/<int:comanda_id>/item/<int:item_id>/apagar', methods=["POST"])  # ✅ POST, não GET
def apagar_item(comanda_id, item_id):
    comanda = Comanda.query.get_or_404(comanda_id)
    item    = ItemComanda.query.get_or_404(item_id)

    db.session.delete(item)
    db.session.flush()
    comanda.recalcular_total()
    db.session.commit()
    flash("Item apagado com sucesso!", "success")
    return redirect(url_for('comanda.detalhe_comanda', id=comanda_id))