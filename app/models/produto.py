from app.extensions import db

class Produto(db.Model):
    __tablename__ = 'produtos'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome        = db.Column(db.String(100), nullable=False)
    preco_venda = db.Column(db.Float, nullable=False)

    # Um produto pode aparecer em vários itens de comanda
    itens = db.relationship('ItemComanda', backref='produto', lazy=True)

    def __repr__(self):
        return f'<Produto {self.id} - {self.nome}>'
