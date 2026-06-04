from app.extensions import db
from datetime import datetime

class Comanda(db.Model): #tabela de comanda
    __tablename__ = 'comandas'

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True) #ID - Inteiro - PK - Autoincrementável
    cliente           = db.Column(db.String(100), nullable=False) # cliente - texto - não nulo
    mesa              = db.Column(db.Integer, nullable=False) # mesa - nº - não nulo
    status            = db.Column(db.String(20), nullable=False, default='Aberta') #status - texto - não nulo - padrão como aberta
    horarioPedido     = db.Column(db.DateTime, nullable=False, default=datetime.now)
    horarioPagamento  = db.Column(db.DateTime, nullable=True)
    total             = db.Column(db.Float, nullable=False, default=0.0)
    observacao        = db.Column(db.String(300), nullable=True)

    # Relacionamento - Uma comanda tem vários itens
    itens = db.relationship(
        'ItemComanda',
        backref='comanda', #permite acessar item.comanda a partir de um item
        lazy=True, #os itens só são carregados do banco quando acessados
        cascade='all, delete-orphan'   # apagar comanda apaga seus itens
    )

    #função auxiliar
    def recalcular_total(self): #Soma o subtotal de todos os itens da comanda e atualiza o campo total.
        self.total = sum(item.subtotal for item in self.itens)

    def __repr__(self):
        return f'<Comanda {self.id} - {self.cliente} - Mesa {self.mesa}>'