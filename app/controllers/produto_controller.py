from flask import Blueprint, render_template, redirect, flash, url_for
from app.extensions import db
from app.models.produto import Produto
from app.forms.produto_form import ProdutoForm

produto_bp = Blueprint("produto", __name__)


@produto_bp.route('/')
def produto():
    produtos = Produto.query.all()
    form = ProdutoForm()
    return render_template('pages/produtos.html', produtos=produtos, form=form)


@produto_bp.route('/cadastrar', methods=['POST'])
def cadastrar_produto():
    form = ProdutoForm()  # ✅ instância, não a classe
    if form.validate_on_submit():
        produto = Produto(
            nome        = form.nome.data,         # ✅ dados via form, não request.form
            preco_venda = form.preco_venda.data,
        )
        db.session.add(produto)
        db.session.commit()
        flash("Produto cadastrado com sucesso!", "success")
    else:
        for field, errors in form.errors.items():
            for erro in errors:
                flash(f"{field}: {erro}", "danger")

    return redirect(url_for('produto.produto'))


@produto_bp.route('/<int:id>/editar', methods=['GET', 'POST'])  
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    form = ProdutoForm(obj=produto)

    if form.validate_on_submit():
        produto.nome        = form.nome.data
        produto.preco_venda = form.preco_venda.data
        db.session.commit()
        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for('produto.produto'))

    return render_template('pages/produto_editar.html', produto=produto, form=form)


@produto_bp.route('/<int:id>/apagar', methods=['GET','POST'])  
def apagar_produto(id):
    produto = Produto.query.get_or_404(id)

    if produto.itens:
        flash("Não é possível excluir um produto que já foi utilizado em comandas.", "danger")
        return redirect(url_for('produto.produto'))

    db.session.delete(produto)
    db.session.commit()
    flash("Produto excluído com sucesso!", "success")
    return redirect(url_for('produto.produto'))