from flask import Flask
from app.config import Config
from app.extensions import db, migrate

from app.models.comanda import Comanda
from app.models.item_comanda import ItemComanda
from app.models.produto import Produto

from app.controllers.home_controller import home_bp
from app.controllers.comanda_controller import comanda_bp
from app.controllers.produto_controller import produto_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(comanda_bp, url_prefix="/comanda")
    app.register_blueprint(produto_bp, url_prefix="/produtos")

    return app