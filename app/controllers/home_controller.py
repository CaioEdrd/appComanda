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
    dataHoje = datetime.now()

    form = ComandaForm()

    if form.validate_on_submit():
        mesa = request.form.get("mesa")
        cliente = request.form.get("cliente")
        observacao = request.form.get("observacao")

        if not cliente:
            flash("É necessário colocar o nome do cliente", "danger")
            return redirect(url_for("home.home"))

        if not mesa:
            flash("É necessário colocar a mesa do cliente", "danger")
            return redirect(url_for("home.home"))

        mesa_ocupada = Comanda.query.filter_by(mesa=int(mesa), status="Aberta").first()
        if mesa_ocupada:
            flash("Mesa com comanda aberta!", "danger")
            return redirect(url_for("home.home"))

        produtos = Produto.query.all()
        itens = []
        total = 0.0

        for produto in produtos:
            quantidade = request.form.get(f'quantidade_{produto.id}')
            quantidade = int(quantidade) if quantidade else 0

            if quantidade > 0:
                subtotal = quantidade * produto.preco_venda
                itens.append(ItemComanda(
                    produto_id=produto.id,
                    nome=produto.nome,
                    valor_unitario=produto.preco_venda,
                    quantidade=quantidade,
                    subtotal=subtotal,
                ))
                total += subtotal

        if total == 0:
            flash("Não há itens na comanda", "danger")
            return redirect(url_for("home.home"))

        comanda = Comanda(
            cliente=cliente,
            mesa=int(mesa),
            observacao=observacao,
            total=total,
        )
        db.session.add(comanda)
        db.session.flush()

        for item in itens:
            item.comanda_id = comanda.id
            db.session.add(item)

        db.session.commit()
        flash("Comanda aberta com sucesso!", "success")
        return redirect(url_for("home.home"))

    todas = Comanda.query.order_by(Comanda.id).all()
    produtos = Produto.query.all()

    total_abertas       = Comanda.query.filter_by(status="Aberta").count()
    total_pagas         = Comanda.query.filter_by(status="Paga").count()
    total_inadimplentes = Comanda.query.filter_by(status="Inadimplente").count()
    total_comandas      = Comanda.query.count()

    faturamento = db.session.query(
        db.func.coalesce(db.func.sum(Comanda.total), 0)
    ).scalar()

    ultimosCinco = Comanda.query.order_by(Comanda.id.desc()).limit(5).all()

    return render_template(
        'pages/comandas.html',
        listaComandas=todas,
        ultimosCinco=ultimosCinco,
        total_abertas=total_abertas,
        total_pagas=total_pagas,
        total_inadimplentes=total_inadimplentes,
        total_comandas=total_comandas,
        dataHoje=dataHoje,
        produtos=produtos,
        faturamento=faturamento,
    )
