import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") #criação da chave secreta
 
    SQLALCHEMY_DATABASE_URI = "sqlite:///banco.db" #URL do banco
    SQLALCHEMY_TRACK_MODIFICATIONS = False