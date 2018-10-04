from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random
import string
from itsdangerous import(
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired
)

Base = declarative_base()
chave_secreta = "".join(random.choice(
    string.ascii_uppercase + string.digits) for x in xrange(32))


class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    senha_hash = Column(String(64))
    imagem = Column(String)

    def hash_senha(self, senha):
        self.senha_hash = pwd_context.encrypt(senha)

    def verificar_senha(self, senha):
        return pwd_context.verify(senha, self.senha_hash)

    def gerar_token_auth(self, expiration=600):
        s = Serializer(chave_secreta, expires_in=expiration)
        return s.dumps({"id": self.id})

    @staticmethod
    def verificar_token_auth(token):
        s = Serializer(chave_secreta)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        usuario_id = data["id"]
        return usuario_id


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
