import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") #criação da chave secreta
 
    SQLALCHEMY_DATABASE_URI = "sqlite:///banco.db" #URL do banco
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SUAP_CLIENT_ID = os.environ.get("SUAP_CLIENT_ID", "")

    SUAP_CLIENT_SECRET = os.environ.get("SUAP_CLIENT_SECRET", "")

    SUAP_REDIRECT_URI = os.environ.get(
        "SUAP_REDIRECT_URI", "http://localhost:5000/auth/suap/callback")
    
    SUAP_AUTHORIZE_URL = os.environ.get(
        "SUAP_AUTHORIZE_URL", "https://suap.ifrn.edu.br/o/authorize/"
    )

    SUAP_TOKEN_URL = os.environ.get(
        "SUAP_TOKEN_URL", "https://suap.ifrn.edu.br/o/token/"
    )
    
    SUAP_USERINFO_URL = os.environ.get(
        "SUAP_USERINFO_URL",
        "https://suap.ifrn.edu.br/api/rh/eu/",
    )