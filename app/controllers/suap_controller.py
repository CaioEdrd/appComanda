import secrets #segurança, gera valores aleatórios criptograficamente seguros
from urllib.parse import urlencode # urlencode → transforma um dicionário em query string de URL
from flask import (
    Blueprint,       
    redirect,        
    url_for,         
    session,         
    request,         
    flash,          
    current_app,)
import requests
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db          
from app.models.user import User       

auth_suap_bp = Blueprint("auth_suap", __name__)

# Função auxiliar
def _suap_cfg(key: str) -> str:
    value = current_app.config.get(key)
    if not value:
        raise RuntimeError(f"Configuração ausente: {key}. Verifique seu .env e config.py.")

    return value

@auth_suap_bp.route("/login")
def suap_login():
    state = secrets.token_urlsafe(32)     # gera uma string aleatória de 32 bytes serve como "senha temporária" para validar que o callback veio do fluxo que você iniciou

    session["suap_oauth_state"] = state     # guarda o state na sessão Flask para comparar depois no callback


    params = {
        "response_type": "code", # diz ao SUAP que você quer receber um código de autorização 

        "client_id": _suap_cfg("SUAP_CLIENT_ID"),
        # identifica a aplicação para o SUAP

        "redirect_uri": _suap_cfg("SUAP_REDIRECT_URI"),
        # URL para onde o SUAP vai redirecionar o usuário após o login

        "scope": "identificacao email",
        # quais dados  acessar
        # "identificacao" → nome, matrícula, tipo de vínculo
        # "email"         → endereço de email

        "state": state,
        # é assim que você vai confirmar o callback
    }

    authorize_url = _suap_cfg("SUAP_AUTHORIZE_URL")


    return redirect(f"{authorize_url}?{urlencode(params)}")
    

@auth_suap_bp.route("/callback")
def suap_callback():

    returned_state = request.args.get("state", "")
    # lê o state que o SUAP devolveu na URL do callback

    expected_state = session.pop("suap_oauth_state", None)
    # recupera e REMOVE o state guardada na sessão lá no suap_login()

    if not expected_state or returned_state != expected_state:
        # tratamento de erro
        flash("Requisição inválida (state mismatch). Tente novamente.", "danger")
        return redirect(url_for("login.login"))
        # redireciona para seu login local em caso de erro

    error = request.args.get("error")
    # se o usuário clicou em "Negar" no SUAP, ele retorn error=access_denied
    if error:
        flash(f"Autenticação recusada pelo SUAP: {error}", "danger")
        return redirect(url_for("login.login"))

    code = request.args.get("code")
    
    if not code:
        flash("Código de autorização ausente. Tente novamente.", "danger")
        return redirect(url_for("login.login"))

   # Troca o código pelo access token 

    token_response = requests.post(
        _suap_cfg("SUAP_TOKEN_URL"),

        data={
            "grant_type": "authorization_code",
            # informa que está trocando um código por token
            "code": code,
            "redirect_uri": _suap_cfg("SUAP_REDIRECT_URI"),
            "client_id": _suap_cfg("SUAP_CLIENT_ID"),
            "client_secret": _suap_cfg("SUAP_CLIENT_SECRET"),
        },
        timeout=10,
        # aguarda no máximo 10 segundos pela resposta
    )

    if not token_response.ok:
        # .ok → False para qualquer erro
        flash("Erro ao obter token de acesso do SUAP.", "danger")
        current_app.logger.error(
            "SUAP token error: %s – %s",
            token_response.status_code,  
            token_response.text,         
        )
        return redirect(url_for("login.login"))
    
    #verificação do erro
    access_token = token_response.json().get("access_token")
    # .json()           → converte a resposta  em dicionário Python
    # .get("access_token") → extrai o token do dicionário
    # o token é uma string longa que prova que o usuário autorizou sua aplicação

    if not access_token:
        flash("Token de acesso não encontrado na resposta do SUAP.", "danger")
        return redirect(url_for("login.login"))

    #Busca os dados do usuário 
    
    userinfo_response = requests.get(
        _suap_cfg("SUAP_USERINFO_URL"),

        headers={"Authorization": f"Bearer {access_token}"},
        # envia o token no header para o SUAP identificar de qual usuário buscar os dados
        timeout=10,
    )

    if not userinfo_response.ok:
        flash("Erro ao recuperar dados do usuário no SUAP.", "danger")
        current_app.logger.error(
            "SUAP userinfo error: %s – %s",
            userinfo_response.status_code,
            userinfo_response.text,
        )
        return redirect(url_for("login.login"))

    suap_data = userinfo_response.json()
    # converte a resposta em dicionário Python


    #Cria ou atualiza o usuário no banco 
    usuario = _get_or_create_user(suap_data)



    login_user(usuario)

    flash(f"Bem-vindo(a), {usuario.nome}! Login realizado via SUAP.", "success")
    return redirect(url_for("home.home"))


# FUNÇÃO AUXILIAR

def _get_or_create_user(suap_data: dict) -> User:
    email        = suap_data.get("email_preferencial", "").strip().lower()
    nome         = suap_data.get("nome_usual") or suap_data.get("nome", "Usuário SUAP")
    tipo_usuario = suap_data.get("tipo_usuario", "Aluno").lower()

    # "aluno" → garçom, qualquer outro (servidor, etc) → admin
    perfil = "garçom" if tipo_usuario == "aluno" else "admin"

    usuario = User.query.filter_by(email=email).first()

    if usuario is None:
        usuario = User(
            nome=nome,
            email=email,
            senha=generate_password_hash(secrets.token_hex(32)),
            perfil=perfil,
        )
        db.session.add(usuario)
    else:
        usuario.nome   = nome
        usuario.perfil = perfil

    db.session.commit()
    return usuario
