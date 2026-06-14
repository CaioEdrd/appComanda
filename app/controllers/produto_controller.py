from flask import Blueprint, render_template, redirect, flash, url_for,abort
from app.extensions import db
from app.models.produto import Produto
from app.forms.produto_form import ProdutoForm
from flask_login import current_user,login_required
from functools import wraps



produto_bp = Blueprint("produto", __name__) #bp produto

def perfil_required(perfil):

    def decorator(func):

        @wraps(func)
        def decorated_view(*args, **kwargs):

            if current_user.perfil != perfil:
                abort(403)

            return func(*args, **kwargs)

        return decorated_view

    return decorator

@produto_bp.route('/') #rota principal de produtos
@login_required
@perfil_required("admin")
def produto():
    produtos = Produto.query.all()
    form = ProdutoForm() #criação do formulário de produtos
    return render_template('pages/produtos.html', produtos=produtos, form=form)


@produto_bp.route('/cadastrar', methods=['POST']) #rota de cadastrar produtos
def cadastrar_produto():
    form = ProdutoForm()  # instância, não a classe
    if form.validate_on_submit():
        produto = Produto(
            nome        = form.nome.data,         # dados via form
            preco_venda = form.preco_venda.data,
        )
        db.session.add(produto)
        db.session.commit()
        flash("Produto cadastrado com sucesso!", "success")
    else:
        for field, errors in form.errors.items(): #erros no formulários
            for erro in errors:
                flash(f"{field}: {erro}", "danger")

    return redirect(url_for('produto.produto'))


@produto_bp.route('/<int:id>/editar', methods=['GET', 'POST'])  #rota de editar produto
@login_required
@perfil_required("admin")
def editar_produto(id):
    produto = Produto.query.get_or_404(id) #select no produto específico
    form = ProdutoForm(obj=produto) #preenche o formulário com os dados do item

    if form.validate_on_submit():
        produto.nome        = form.nome.data
        produto.preco_venda = form.preco_venda.data
        db.session.commit()
        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for('produto.produto'))

    return render_template('pages/produto_editar.html', produto=produto, form=form)


@produto_bp.route('/<int:id>/apagar', methods=['GET','POST'])  #rota de apagar produto
@login_required
@perfil_required("admin")
def apagar_produto(id):
    produto = Produto.query.get_or_404(id)

    if produto.itens: #verifica se o produto já é um item de uma comanda
        flash("Não é possível excluir um produto que já foi utilizado em comandas.", "danger")
        return redirect(url_for('produto.produto')) #se for item, não apaga

    db.session.delete(produto)
    db.session.commit()
    flash("Produto excluído com sucesso!", "success")
    return redirect(url_for('produto.produto'))