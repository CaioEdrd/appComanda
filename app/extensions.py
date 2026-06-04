from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy() #instância do banco
migrate = Migrate() #instância do migrate