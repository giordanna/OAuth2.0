# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from configuracao_db import Base, Usuario, Categoria, Item, engine
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


DIRETORIO_UPLOAD = "static/img"

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
app = Flask(__name__)
app.secret_key = "super_chave_secreta"
app.debug = True
api = Api(app)

imagemUpload = UploadSet("imagem", IMAGES)
app.config["UPLOADED_IMAGEM_DEST"] = DIRETORIO_UPLOAD
configure_uploads(app, imagemUpload)

ID_CLIENTE = json.loads(
    open("segredos_cliente.json", "r").read())["web"]["client_id"]


def getUsuario(usuario_id):
    session = DBSession()
    usuario = session.query(
        Usuario).filter_by(id=usuario_id).one_or_none()
    session.close()
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
