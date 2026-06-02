from app.extensions import db
from datetime import datetime

class Comanda(db.Model):
    __tablename__ = 'comandas'

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente           = db.Column(db.String(100), nullable=False)
    mesa              = db.Column(db.Integer, nullable=False)
    status            = db.Column(db.String(20), nullable=False, default='Aberta')
    horarioPedido     = db.Column(db.DateTime, nullable=False, default=datetime.now)
    horarioPagamento  = db.Column(db.DateTime, nullable=True)
    total             = db.Column(db.Float, nullable=False, default=0.0)
    observacao        = db.Column(db.String(300), nullable=True)

    # Uma comanda tem vários itens
    itens = db.relationship(
        'ItemComanda',
        backref='comanda',
        lazy=True,
        cascade='all, delete-orphan'   # apagar comanda apaga seus itens
    )

    def recalcular_total(self):
        """Recalcula e persiste o total com base nos itens atuais."""
        self.total = sum(item.subtotal for item in self.itens)

    def __repr__(self):
        return f'<Comanda {self.id} - {self.cliente} - Mesa {self.mesa}>'