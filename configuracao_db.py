from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String, index=True)
    imagem = Column(String)


class Categoria(Base):
    __tablename__ = "categoria"

    id = Column(Integer, primary_key=True)
    nome = Column(String(250), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id"))
    usuario = relationship(Usuario)

    @property
    def serialize(self):
        '''Return object data in easily serializeable format'''
        return {
            "id": self.id,
            "nome": self.nome
        }


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    nome = Column(String(80), nullable=False)
    descricao = Column(String(250))
    imagem = Column(String)
    categoria_id = Column(Integer, ForeignKey("categoria.id"))
    categoria = relationship(Categoria)
    usuario_id = Column(Integer, ForeignKey("usuario.id"))
    usuario = relationship(Usuario)

    @property
    def serialize(self):
        '''Return object data in easily serializeable format'''
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "categoria": self.categoria_id
        }

engine = create_engine("sqlite:///catalogo.db")

Base.metadata.create_all(engine)
