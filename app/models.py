from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so

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