from configuracao_db import Base, Usuario, Categoria, Item, engine
from flask import (
    Flask, jsonify, request, url_for,
    abort, g, render_template
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from flask.ext.httpauth import HTTPBasicAuth
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

auth = HTTPBasicAuth()

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
app = Flask(__name__)


ID_CLIENTE = json.loads(
    open("segredos_cliente.json", "r").read())["web"]["client_id"]


@auth.verify_password
def verificar_senha(usuario_ou_token, senha):
    #Try to see if it's a token first
    usuario_id = Usuario.verificar_token_auth(usuario_ou_token)
    if usuario_id:
        usuario = session.query(Usuario).filter_by(id=usuario_id).one()
    else:
        usuario = session.query(Usuario).filter_by(email=usuario_ou_token).first()
        if not usuario or not usuario.verificar_senha(senha):
            return False
    g.usuario = usuario
    return True


@app.route("/")
@app.route("/categorias")
def showCategorias():
    return "mostrando o catalogo!"


@app.route('/login', methods=["GET", "POST"])
def loginUsuario():
    if request.method == "POST":
        return "login usuario!"
    else:
        return "visualizando pagina de login!"


@app.route('/usuarios', methods=['POST'])
def newUsuario():
    if request.method == "POST":
        return "novo usuario criado!";


@app.route("/categorias/new/", methods=["GET", "POST"])
def newCategoria():
    if request.method == "POST":
        return "adicionando categoria no catalogo!"
    else:
        return "mostrar formulario para adicionar categoria!"


@app.route("/categorias/<int:categoria>/")
def showCategoria(categoria):
    return "mostrando a CATEGORIA!"


@app.route("/categorias/<int:categoria>/edit/", methods=["GET", "POST"])
def editCategoria(categoria):
    if request.method == "POST":
        return "editando categoria!"
    else:
        return "mostrar formulario para editar categoria!"


@app.route("/categorias/<int:categoria>/delete/", methods=["GET", "POST"])
def deleteCategoria(categoria):
    if request.method == "POST":
        return "deletando categoria!"
    else:
        return "mostrar formulario para deletar categoria!"


@app.route("/categorias/<int:categoria>/new/", methods=["GET", "POST"])
def newItem(categoria):
    if request.method == "POST":
        return "adicionando item na categoria!"
    else:
        return "mostrar formulario para adicionar item!"


@app.route("/categorias/<int:categoria>/<int:item>/edit/", methods=["GET", "POST"])
def editItem(categoria, item):
    if request.method == "POST":
        return "editando item!"
    else:
        return "mostrar formulario para editar item!"


@app.route("/categorias/<int:categoria>/<int:item>/delete/", methods=["GET", "POST"])
def deleteItem(categoria, item):
    if request.method == "POST":
        return "deletando item!"
    else:
        return "mostrar formulario para deletar item!"


@app.route('/api/v1/categorias')
def jsonCategorias():
    return "mostra as categorias";


@app.route('/api/v1/categorias/<int:categoria>')
def jsonCategoria(categoria):
    return "mostra uma categoria e seus itens";


@app.route('/api/v1/categorias/<int:categoria>/<int:item>')
def jsonItem(categoria, item):
    return "mostra um item de uma categoria";


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
