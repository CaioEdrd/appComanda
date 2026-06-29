from flask import Flask #importação do flask 
from app.config import Config #importação das configurações
from app.extensions import db, migrate,login_manager #importação das extensões

#importação das rotas 
from app.controllers.home_controller import home_bp
from app.controllers.comanda_controller import comanda_bp
from app.controllers.produto_controller import produto_bp
from app.controllers.login_controller import login_bp
from app.controllers.cadastro_controller import cadastro_bp
from app.controllers.suap_controller     import auth_suap_bp

def create_app():
    app = Flask(__name__) #criação da aplicação

    app.config.from_object(Config) #configuração da aplicação
  
    db.init_app(app) #inicialização do banco com a aplicação
    migrate.init_app(app, db) #Inicializa o Flask-Migrate passando o app e o banco
    login_manager.init_app(app)

    login_manager.login_view = "login.login"
    #registro das blueprints/rotas
    app.register_blueprint(login_bp, url_prefix="/login")
    app.register_blueprint(cadastro_bp, url_prefix="/cadastro")
    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(comanda_bp, url_prefix="/comanda")
    app.register_blueprint(produto_bp, url_prefix="/produtos")
    app.register_blueprint(auth_suap_bp, url_prefix="/auth/suap")

    return app