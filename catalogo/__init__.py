# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from flask import (
    Flask, request, url_for, session as login_session,
    render_template, flash, redirect
)
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
import json
import os

app = Flask(__name__)
app.secret_key = "super_chave_secreta"

api = Api(app)

DIRETORIO_UPLOAD = "catalogo/static/img"
imagemUpload = UploadSet("imagem", IMAGES)
app.config["UPLOADED_IMAGEM_DEST"] = DIRETORIO_UPLOAD
configure_uploads(app, imagemUpload)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://student:123qwe@localhost/catalogo"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# início do banco de dados


class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    imagem = db.Column(db.String)


class Categoria(db.Model):
    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    usuario = db.relationship(Usuario)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "nome": self.nome
        }


class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    descricao = db.Column(db.String)
    imagem = db.Column(db.String)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"))
    categoria = db.relationship(Categoria)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    usuario = db.relationship(Usuario)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "categoria": self.categoria_id
        }


# fim do banco de dados

db.create_all()

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(PROJECT_ROOT, 'segredos_cliente.json')

ID_CLIENTE = json.load(
    open(json_url))["web"]["client_id"]

# justificativa de utilizar o nopep8:
# seguindo instruções na documentação do flask
# http://flask.pocoo.org/docs/1.0/patterns/packages/
# "Import the view module after the application object is created"
from catalogo import (  # nopep8
    usuarios, categorias, itens, api_endpoints, erros
)

app.register_blueprint(usuarios.usuarios)
app.register_blueprint(categorias.categorias)
app.register_blueprint(itens.itens)


@app.route("/")
def index():
    return redirect(url_for("categorias.showCategorias"))
