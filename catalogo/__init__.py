# -*- coding: utf-8 -*-
# !/usr/bin/env python3


from flask import (
    Flask, request, url_for, g,
    render_template, flash, redirect
)

from sqlalchemy.orm import sessionmaker
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
from flask import session as login_session
import requests
import random
import string
import hashlib
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "super_chave_secreta"
app.debug = True

api = Api(app)

DIRETORIO_UPLOAD = "catalogo/static/img"
imagemUpload = UploadSet("imagem", IMAGES)
app.config["UPLOADED_IMAGEM_DEST"] = DIRETORIO_UPLOAD
configure_uploads(app, imagemUpload)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///catalogo.db"
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

ID_CLIENTE = json.loads(
    open("segredos_cliente.json", "r").read())["web"]["client_id"]


def getUsuario(usuario_id):
    usuario = Usuario.query.filter_by(id=usuario_id).one_or_none()
    return usuario


# justificativa de utilizar o nopep8:
# seguindo instruções na documentação do flask
# http://flask.pocoo.org/docs/1.0/patterns/packages/
# "Import the view module after the application object is created"
import catalogo.usuarios_views  # nopep8
import catalogo.categorias_views  # nopep8
import catalogo.itens_views  # nopep8
import catalogo.erros_views  # nopep8
import catalogo.api  # nopep8
