from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.extensions import db
from app.models.produto import Produto

produto_bp = Blueprint("produto", __name__)

@produto_bp.route('/')
def produto():
    produtos = Produto.query.all()
    return render_template('pages/produtos.html', produtos=produtos)


@produto_bp.route('/cadastrar', methods=['POST'])
def cadastrar_produto():
    nome  = request.form['nome']
    preco = float(request.form['preco_venda'])

    produto = Produto(nome=nome, preco_venda=preco)
    db.session.add(produto)
    db.session.commit()
    return redirect(url_for('produto.produto'))


@produto_bp.route('/<int:id>/editar', methods=['GET'])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    return render_template('pages/produto_editar.html', produto=produto)


@produto_bp.route('/<int:id>/atualizar', methods=['POST'])
def atualizar_produto(id):
    produto = Produto.query.get_or_404(id)
    produto.nome        = request.form['nome']
    produto.preco_venda = float(request.form['preco_venda'])
    db.session.commit()
    return redirect(url_for('produto.produto'))


@produto_bp.route('/<int:id>/apagar')
def apagar_produto(id):
    produto = Produto.query.get_or_404(id)

    if produto.itens:
        flash(
            "Não é possível excluir um produto que já foi utilizado em comandas.",
            "danger"
        )
        return redirect(url_for('produto.produto'))

    db.session.delete(produto)
    db.session.commit()

    flash("Produto excluído com sucesso!", "success")
    return redirect(url_for('produto.produto'))
