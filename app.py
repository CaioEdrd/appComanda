from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime


app = Flask(__name__)
app.secret_key = ("123456")

produtos = []
listaComandas = []
contador_id_comanda = 1   
contador_id_produto = 1   


@app.route('/', methods=["GET", "POST"])
def comandas():
    global contador_id_comanda

    comandas_abertas = []
    comandas_pagas = []
    comandas_inadimplentes = []
    faturamento = 0
    dataHoje = datetime.now()

    if request.method == "POST":

        # Verifica mesa com comanda aberta
        for c in listaComandas:
            if (
                str(c["mesa"]) == request.form.get("mesa")
                and c["status"] == "Aberta"
            ):
                flash("Mesa com comanda aberta!", "danger")
                return redirect(url_for("comandas"))

        pedido = []
        total = 0

        for produto in produtos:
            quantidade = request.form.get(f'quantidade_{produto["id"]}')
            quantidade = int(quantidade) if quantidade else 0

            if quantidade > 0:
                subtotal = quantidade * float(produto["preco_venda"])
                item = {
                    "produto_id": produto["id"],
                    "nome": produto["nome"],
                    "valor_unitario": produto["preco_venda"],
                    "quantidade": quantidade,
                    "subtotal": float(subtotal),
                }
                pedido.append(item)
                total += subtotal

        comanda = {
            "id": contador_id_comanda,          
            "cliente": request.form.get("cliente"),
            "mesa": request.form.get("mesa"),
            "horarioPedido": datetime.now(),
            "horarioPagamento": "-",
            "status": "Aberta",
            "pedido": pedido,
            "total": float(total),
            "observacao": request.form.get("observacao"),
        }

        if not comanda["cliente"]:
            flash("É necessário colocar o nome do cliente", "danger")
            return redirect(url_for("comandas"))

        if not comanda["mesa"]:
            flash("É necessário colocar a mesa do cliente", "danger")
            return redirect(url_for("comandas"))

        if total > 0:
            listaComandas.append(comanda)
            contador_id_comanda += 1            # Incrementa só após inserir
            flash("Comanda aberta com sucesso!", "success")
        else:
            flash("Não há itens na comanda", "danger")

        return redirect(url_for("comandas"))

    # ── KPIs ──────────────────────────────────
    for c in listaComandas:
        if c["status"] == "Aberta":
            comandas_abertas.append(c)
        elif c["status"] == "Paga":
            comandas_pagas.append(c)
        elif c["status"] == "Inadimplente":
            comandas_inadimplentes.append(c)

    for c in listaComandas:
        faturamento += c["total"]

    ultimosCinco = listaComandas[-5:][::-1]

    return render_template(
        'comandas.html',
        listaComandas=listaComandas,
        ultimosCinco=ultimosCinco,
        total_abertas=len(comandas_abertas),
        total_pagas=len(comandas_pagas),
        total_inadimplentes=len(comandas_inadimplentes),
        total_comandas=len(listaComandas),
        dataHoje=dataHoje,
        produtos=produtos,
        faturamento=faturamento,
    )


@app.route('/comanda/<int:id>', methods=["GET", "POST"])
def detalhe_comanda(id):
    comanda = next((i for i in listaComandas if i["id"] == id), None)

    if comanda is None:
        flash("Comanda não encontrada", "danger")
        return redirect(url_for("comandas"))

    # Calcula tempo da comanda
    if comanda["horarioPagamento"] == "-":
        diferenca = datetime.now() - comanda["horarioPedido"]
    else:
        diferenca = comanda["horarioPagamento"] - comanda["horarioPedido"]
    tempo_aberta = str(diferenca).split(".")[0]

    if request.method == "POST":
        adicionou_algum = False

        for produto in produtos:
            quantidade = request.form.get(f'quantidade_{produto["id"]}')
            quantidade = int(quantidade) if quantidade else 0

            if quantidade > 0:
                item = {
                    "produto_id": produto["id"],
                    "nome": produto["nome"],
                    "valor_unitario": float(produto["preco_venda"]),
                    "quantidade": quantidade,
                    "subtotal": quantidade * float(produto["preco_venda"]),
                }

                produto_existe = False
                for i in comanda["pedido"]:
                    if i["produto_id"] == item["produto_id"]:
                        i["quantidade"] += item["quantidade"]
                        i["subtotal"] = i["quantidade"] * float(i["valor_unitario"])
                        produto_existe = True
                        break

                if not produto_existe:
                    comanda["pedido"].append(item)

                adicionou_algum = True

        if adicionou_algum:
            comanda["total"] = sum(float(i["subtotal"]) for i in comanda["pedido"])
            flash("Itens adicionados com sucesso!", "success")
        else:
            flash("Nenhum item selecionado", "warning")

        return redirect(url_for('detalhe_comanda', id=id))

    return render_template(
        'comanda_detalhe.html',
        comanda=comanda,
        tempo_aberta=tempo_aberta,
        produtos=produtos,
    )


@app.route('/comanda/<int:id>/editar', methods=["GET", "POST"])
def editar_comanda(id):
    comanda = next((i for i in listaComandas if i['id'] == id), None)

    if comanda is None:
        flash("Comanda não encontrada", "danger")
        return redirect(url_for("comandas"))

    if request.method == "POST":
        comanda['cliente'] = request.form.get('cliente')
        comanda['mesa'] = request.form.get('mesa')

        if comanda['status'] != "Paga":
            novo_status = request.form.get('status')
            comanda['status'] = novo_status
        # Comanda já encerrada não pode ser reaberta

        if comanda['status'] in ("Paga"):
            if comanda['horarioPagamento'] == "-":
                comanda['horarioPagamento'] = datetime.now()

        flash("Comanda editada com sucesso!", "success")
        return redirect(url_for('comandas'))

    return render_template(
        'comanda_editar.html',
        listaComandas=listaComandas,
        comanda=comanda,
    )


@app.route('/comanda/<int:id>/apagar')
def apagar_comanda(id):
    global listaComandas
    listaComandas = [c for c in listaComandas if c['id'] != id]
    flash("Comanda apagada com sucesso!", "success")
    return redirect(url_for('comandas'))


# ─────────────────────────────────────────────
#  ITENS DA COMANDA
# ─────────────────────────────────────────────

@app.route('/comanda/<int:comanda_id>/item/<int:produto_id>/editar', methods=['GET', 'POST'])
def editar_item(comanda_id, produto_id):
    comanda = next((c for c in listaComandas if c["id"] == comanda_id), None)

    if comanda is None:
        flash("Comanda não encontrada", "danger")
        return redirect(url_for("comandas"))

    item = next((i for i in comanda["pedido"] if i["produto_id"] == produto_id), None)

    if item is None:
        flash("Item não encontrado", "danger")
        return redirect(url_for("detalhe_comanda", id=comanda_id))

    if request.method == "POST":
        quantidade = int(request.form.get("quantidade"))
        item["quantidade"] = quantidade
        item["subtotal"] = quantidade * float(item["valor_unitario"])
        comanda["total"] = sum(i["subtotal"] for i in comanda["pedido"])
        flash("Item atualizado com sucesso!", "success")
        return redirect(url_for('detalhe_comanda', id=comanda_id))

    return render_template('item_editar.html', comanda=comanda, item=item)


@app.route('/comanda/<int:comanda_id>/item/<int:produto_id>/apagar')
def apagar_item(comanda_id, produto_id):
    comanda = next((c for c in listaComandas if c["id"] == comanda_id), None)

    if comanda is None:
        flash("Comanda não encontrada", "danger")
        return redirect(url_for("comandas"))

    comanda["pedido"] = [i for i in comanda["pedido"] if i["produto_id"] != produto_id]
    comanda["total"] = sum(i["subtotal"] for i in comanda["pedido"])
    flash("Item apagado com sucesso!", "success")
    return redirect(url_for('detalhe_comanda', id=comanda_id))


@app.route('/produtos')                         
def produto():
    return render_template('produtos.html', produtos=produtos)


@app.route('/produtos/cadastrar', methods=['GET','POST'])   
def cadastrar_produto():
    global contador_id_produto

    nome = request.form['nome']
    preco = request.form['preco_venda']

    produto = {
        'id': contador_id_produto,
        'nome': nome,
        'preco_venda': preco,
    }
    produtos.append(produto)
    contador_id_produto += 1

    return redirect(url_for('produto'))


@app.route('/produtos/<int:id>/editar', methods=['GET','POST'])   
def editar_produto(id):
    produto = next((i for i in produtos if i['id'] == id), None)

    if produto is None:
        flash("Produto não encontrado", "danger")
        return redirect(url_for('produto'))

    return render_template('produto_editar.html', produto=produto)


@app.route('/produtos/<int:id>/atualizar', methods=['GET','POST'])  
def atualizar_produto(id):
    produto = next((i for i in produtos if i['id'] == id), None)

    if produto is not None:
        produto['nome'] = request.form['nome']
        produto['preco_venda'] = request.form['preco_venda']
        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for('produto'))
    return redirect(url_for('produto'))


@app.route('/produtos/<int:id>/apagar')          
def apagar_produto(id):
    global produtos
    produtos = [p for p in produtos if p['id'] != id]
    flash("Produto apagado com sucesso!", "success")
    return redirect(url_for('produto'))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)