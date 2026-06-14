from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy() #instância do banco
migrate = Migrate() #instância do migrate
login_manager = LoginManager() #login
