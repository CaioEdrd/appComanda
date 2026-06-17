from flask import Blueprint, render_template, redirect, flash, url_for, request, abort #importação de módulos da biblioteca "flask"
from app.extensions import db #importação do banco
from app.models.comanda import Comanda #importação da tabela comanda
from app.models.item_comanda import ItemComanda #importação da tabela de itens
from app.models.produto import Produto #importação da tabela produto
from app.forms.item_editar_form import ItemComandaForm #importação do formulário de editar item da comanda
from app.forms.comanda_form import  AdicionarItensForm, EditarComandaForm #importação de formulários da comanda e de adicionar itens na comanda
from datetime import datetime #importação da biblioteca datetime
from flask_login import current_user,login_required
from functools import wraps

comanda_bp = Blueprint("comanda", __name__) #configuração da blueprint da comanda

def perfil_required(*perfil):

    def decorator(func):

        @wraps(func)
        def decorated_view(*args, **kwargs):

            if current_user.perfil not in perfil:
                flash("Você não tem permissão para acessar essa página.", "danger")
                return redirect(url_for('home.home'))

            return func(*args, **kwargs)

        return decorated_view

    return decorator

@comanda_bp.route('/<int:id>', methods=["GET", "POST"]) #rota de detalhar uma comanda específica
@login_required
@perfil_required("garçom", "admin")
def detalhe_comanda(id):
    comanda  = Comanda.query.get_or_404(id) #select na comadna
    produtos = Produto.query.all() #select nos produtos
    form     = AdicionarItensForm()  # form de adicionar itens sem cliente/mesa obrigatórios 

    if request.method == "GET": 
        for produto in produtos: #percorre todos os produtos
            form.itens.append_entry({ #Para cada produto, adiciona uma entrada no formulário com seus dados e quantidade inicial zero.

                "produto_id": produto.id,
                "nome":       produto.nome,
                "preco":      produto.preco_venda,
                "quantidade": 0,
            })

    if form.validate_on_submit(): #verifica se o formulário foi submetido
        adicionou_algum = False #variavel de controle de adição de produtos

        for item_data in form.itens.data: #Percorre os dados de cada item enviado pelo formulário.
            quantidade = item_data.get("quantidade") or 0 #Pega a quantidade do item. Se vier vazio ou None, assume zero.
            if quantidade <= 0:
                continue #Se a quantidade for zero ou negativa, pula esse item.

            item_existente = ItemComanda.query.filter_by(
                comanda_id=comanda.id,
                produto_id=item_data["produto_id"],
            ).first() #Verifica se esse produto já existe na comanda atual.

            if item_existente: #Se o item já existe, soma a nova quantidade e recalcula o subtotal.
                item_existente.quantidade += quantidade
                item_existente.subtotal    = item_existente.quantidade * item_existente.valor_unitario
            else: #Se o item não existe, cria um novo ItemComanda e adiciona na sessão do banco.
                db.session.add(ItemComanda(
                    comanda_id     = comanda.id,
                    produto_id     = item_data["produto_id"],
                    nome           = item_data["nome"],
                    valor_unitario = float(item_data["preco"]),
                    quantidade     = quantidade,
                    subtotal       = quantidade * float(item_data["preco"]),
                ))

            adicionou_algum = True
 
        if adicionou_algum: #Se algum item foi adicionado:
            db.session.flush() # sincroniza as mudanças na sessão sem commitar ainda
            comanda.recalcular_total() # atualiza o total da comanda
            db.session.commit() #salva tudo no banco
            flash("Itens adicionados com sucesso!", "success")
        else:
            flash("Nenhum item selecionado.", "warning")

        return redirect(url_for('comanda.detalhe_comanda', id=id))

    fim          = comanda.horarioPagamento if comanda.horarioPagamento else datetime.now() #Se a comanda já foi paga, usa o horário de pagamento. Se não, usa o horário atual.
    tempo_aberta = str(fim - comanda.horarioPedido).split(".")[0]

    return render_template(
        'pages/comanda_detalhe.html',
        comanda=comanda,
        tempo_aberta=tempo_aberta,
        produtos=produtos,
        form=form,
    )


@comanda_bp.route('/<int:id>/editar', methods=["GET", "POST"]) #rota de editar uma comanda específica
@login_required
@perfil_required("garçom")
def editar_comanda(id):
    comanda      = Comanda.query.get_or_404(id)
    form_comanda = EditarComandaForm(obj=comanda) #preenche o formulario da comanda com as informações da comanda que foi puxada da tabela pelo select anterior

    if form_comanda.validate_on_submit():
        comanda.cliente = form_comanda.cliente.data #preenche o cliente com os dados da comanda 
        comanda.mesa    = form_comanda.mesa.data #preenche a mesa com os dados da comanda 

        # Só permite mudar status se ainda estiver aberta
        if comanda.status == "Aberta":
            comanda.status = form_comanda.status.data  # adicione o campo no form se necessário

        if comanda.status in ("Paga", "Inadimplente"):
            if not comanda.horarioPagamento:
                comanda.horarioPagamento = datetime.now() #se estiver fechada/inadimplente, é adicionado o horário de pagamento
       
        mesa_ocupada = Comanda.query.filter_by(
            mesa=form_comanda.mesa.data,
            status="Aberta"
        ).filter(Comanda.id != id).first()  # ← exclui a própria comanda da busca

        if mesa_ocupada:
            flash("Mesa com comanda aberta!", "danger")
            return redirect(url_for("home.home"))
        
        db.session.commit()
        flash("Comanda editada com sucesso!", "success")
        return redirect(url_for('home.home'))

    return render_template('pages/comanda_editar.html', comanda=comanda, form_comanda=form_comanda)


@comanda_bp.route('/<int:id>/apagar', methods=["POST", "GET"])  # rota de apagar uma comanda
@login_required
@perfil_required("admin")
def apagar_comanda(id):
    comanda = Comanda.query.get_or_404(id) #select na comanda a ser apagada
    db.session.delete(comanda) #apaga da tabela
    db.session.commit() #salva
    flash("Comanda apagada com sucesso!", "success")
    return redirect(url_for('home.home'))


@comanda_bp.route('/<int:comanda_id>/item/<int:item_id>/editar', methods=["GET", "POST"]) #rota de edição de item na comanda
@login_required
@perfil_required("garçom")
def editar_item(comanda_id, item_id):
    comanda  = Comanda.query.get_or_404(comanda_id) #select na comanda
    item     = ItemComanda.query.get_or_404(item_id) #select nos itens daquela comanda
    form     = ItemComandaForm(obj=item)  # form já preenchido com o item

    if form.validate_on_submit():
        item.quantidade = form.quantidade.data 
        item.subtotal   = item.quantidade * item.valor_unitario
        comanda.recalcular_total() #atualiza o valor do total
        db.session.commit()
        flash("Item atualizado com sucesso!", "success")
        return redirect(url_for('comanda.detalhe_comanda', id=comanda_id))

    return render_template('pages/item_editar.html', comanda=comanda, item=item, form=form)


@comanda_bp.route('/<int:comanda_id>/item/<int:item_id>/apagar', methods=["POST", "GET"])  # rota de apagar item
@login_required
@perfil_required("garçom")
def apagar_item(comanda_id, item_id):
    comanda = Comanda.query.get_or_404(comanda_id)
    item    = ItemComanda.query.get_or_404(item_id)

    db.session.delete(item)
    db.session.flush() #sincronizar o estado da sessão antes de uma operação que depende dessas mudanças, garantindo que o recalcular_total() sempre trabalhe com os dados corretos.
    comanda.recalcular_total()
    db.session.commit() #salva
    flash("Item apagado com sucesso!", "success")
    return redirect(url_for('comanda.detalhe_comanda', id=comanda_id))