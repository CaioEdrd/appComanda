from app.extensions import db

class ItemComanda(db.Model):
    __tablename__ = 'itens_comanda'

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comanda_id     = db.Column(db.Integer, db.ForeignKey('comandas.id'), nullable=False)
    produto_id     = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    nome           = db.Column(db.String(100), nullable=False)   # snapshot do nome
    valor_unitario = db.Column(db.Float, nullable=False)          # snapshot do preço
    quantidade     = db.Column(db.Integer, nullable=False)
    subtotal       = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<ItemComanda comanda={self.comanda_id} produto={self.produto_id} qtd={self.quantidade}>'