from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import event
from sqlalchemy.orm import Session


from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db,login




class User(UserMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    nome_usuario: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    nome_empresa: so.Mapped[str] = so.mapped_column(sa.String(200), index=True)
    
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    
    senha_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    
    configuracoes: so.Mapped[list["Configuracoes"]] = so.relationship(back_populates='usuario')

    def __repr__(self):
        return f'<User {self.nome_usuario}>'
    
    
    def set_senha(self, password):
        self.senha_hash = generate_password_hash(password)
    
    def check_senha(self, password):
        return check_password_hash(self.senha_hash, password)



class Configuracoes(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    chave_configuracao: so.Mapped[str] = so.mapped_column(sa.String(200))
    valor_configuracao: so.Mapped[str] = so.mapped_column(sa.String(200))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    usuario: so.Mapped[User] = so.relationship(back_populates='configuracoes')

    def __repr__(self):
        return f'<Configuração {self.chave_configuracao}={self.valor_configuracao}>'


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_produto = db.Column(db.String(45), nullable=False)
    valor_produto = db.Column(db.Numeric(10, 2), nullable=False)
    id_marca = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=False)
    id_origem = db.Column(db.Integer, db.ForeignKey('origem.id'), nullable=False)
    nota_produto_avg = db.Column(db.Numeric(3, 2), default=0.0)
    data_produto = db.Column(db.Date)
    produtocol = db.Column(db.String(45))

    marca = db.relationship('Marca', back_populates='produtos')
    origem = db.relationship('Origem', back_populates='produtos')
    avaliacoes = db.relationship('Avaliacao', back_populates='produto')



class Marca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_marca = db.Column(db.String(45), unique=True, nullable=False)
    nota_marca_avg = db.Column(db.Numeric(3, 2), default=0.0)
    marcacol = db.Column(db.String(45))

    produtos = db.relationship('Produto', back_populates='marca')


class Origem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_site = db.Column(db.String(45), nullable=False)
    url_site = db.Column(db.String(100))

    produtos = db.relationship('Produto', back_populates='origem')


class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(200))
    comentario = db.Column(db.Text)
    nota_avaliacao = db.Column(db.Numeric(3, 2))
    id_produto = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    data_avaliacao = db.Column(db.Date)

    produto = db.relationship('Produto', back_populates='avaliacoes')



@event.listens_for(User, 'after_insert')
def criar_configuracoes_padrao(mapper, connection, target):
    default_configs = [
        {'chave_configuracao': 'tempo_scraping', 'valor_configuracao': 'diario'},
        {'chave_configuracao': 'site_scraping', 'valor_configuracao': 'https://lista.mercadolivre.com.br/iphone'}
    ]

    for config in default_configs:
        connection.execute(
            Configuracoes.__table__.insert(),
            {
                'chave_configuracao': config['chave_configuracao'],
                'valor_configuracao': config['valor_configuracao'],
                'user_id': target.id
            }
        )