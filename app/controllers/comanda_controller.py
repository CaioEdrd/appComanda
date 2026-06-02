from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.extensions import db
from app.models.comanda import Comanda
from app.models.item_comanda import ItemComanda
from app.models.produto import Produto
from datetime import datetime

comanda_bp = Blueprint("comanda", __name__)

@comanda_bp.route('/<int:id>', methods=["GET", "POST"])
def detalhe_comanda(id):
    comanda = Comanda.query.get_or_404(id)


    fim = comanda.horarioPagamento if comanda.horarioPagamento else datetime.now()
    tempo_aberta = str(fim - comanda.horarioPedido).split(".")[0]

    if request.method == "POST":
        produtos = Produto.query.all()
        adicionou_algum = False

        for produto in produtos:
            quantidade = request.form.get(f'quantidade_{produto.id}')
            quantidade = int(quantidade) if quantidade else 0

            if quantidade > 0:
                item_existente = ItemComanda.query.filter_by(
                    comanda_id=comanda.id,
                    produto_id=produto.id
                ).first()

                if item_existente:
                    item_existente.quantidade += quantidade
                    item_existente.subtotal = (
                        item_existente.quantidade * item_existente.valor_unitario
                    )
                else:
                    novo_item = ItemComanda(
                        comanda_id=comanda.id,
                        produto_id=produto.id,
                        nome=produto.nome,
                        valor_unitario=produto.preco_venda,
                        quantidade=quantidade,
                        subtotal=quantidade * produto.preco_venda,
                    )
                    db.session.add(novo_item)

                adicionou_algum = True

        if adicionou_algum:
            db.session.flush()
            comanda.recalcular_total()
            db.session.commit()
            flash("Itens adicionados com sucesso!", "success")
        else:
            flash("Nenhum item selecionado", "warning")

        return redirect(url_for('comanda.detalhe_comanda', id=id))

    produtos = Produto.query.all()
    return render_template(
        'pages/comanda_detalhe.html',
        comanda=comanda,
        tempo_aberta=tempo_aberta,
        produtos=produtos,
    )


@comanda_bp.route('/<int:id>/editar', methods=["GET", "POST"])
def editar_comanda(id):
    comanda = Comanda.query.get_or_404(id)

    if request.method == "POST":
        comanda.cliente = request.form.get('cliente')
        comanda.mesa = int(request.form.get('mesa'))

        if comanda.status == "Aberta":
            novo_status = request.form.get('status')
            comanda.status = novo_status

        if comanda.status in ("Paga", "Inadimplente"):
            if not comanda.horarioPagamento:
                comanda.horarioPagamento = datetime.now()

        db.session.commit()
        flash("Comanda editada com sucesso!", "success")
        return redirect(url_for('comandas'))

    return render_template('comanda_editar.html', comanda=comanda)


@comanda_bp.route('/comanda/<int:id>/apagar')
def apagar_comanda(id):
    comanda = Comanda.query.get_or_404(id)
    db.session.delete(comanda)
    db.session.commit()
    flash("Comanda apagada com sucesso!", "success")
    return redirect(url_for('comanda.comandas'))



@comanda_bp.route('/<int:comanda_id>/item/<int:item_id>/editar', methods=['GET', 'POST'])
def editar_item(comanda_id, item_id):
    comanda = Comanda.query.get_or_404(comanda_id)
    item    = ItemComanda.query.get_or_404(item_id)

    if request.method == "POST":
        quantidade = int(request.form.get("quantidade"))
        item.quantidade = quantidade
        item.subtotal   = quantidade * item.valor_unitario
        comanda.recalcular_total()
        db.session.commit()
        flash("Item atualizado com sucesso!", "success")
        return redirect(url_for('comanda.detalhe_comanda', id=comanda_id))

    return render_template('pages/item_editar.html', comanda=comanda, item=item)


@comanda_bp.route('/<int:comanda_id>/item/<int:item_id>/apagar')
def apagar_item(comanda_id, item_id):
    comanda = Comanda.query.get_or_404(comanda_id)
    item    = ItemComanda.query.get_or_404(item_id)

    db.session.delete(item)
    db.session.flush()
    comanda.recalcular_total()
    db.session.commit()
    flash("Item apagado com sucesso!", "success")
    return redirect(url_for('comanda.detalhe_comanda', id=comanda_id))