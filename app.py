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
@app.route("/categorias/")
def showCategorias():
    todasCategorias = session.query(Categoria).all()
    return render_template("showCategorias.html", categorias = todasCategorias)


@app.route('/login/', methods=["GET", "POST"])
def loginUsuario():
    if request.method == "POST":
        return "login usuario!"
    else:
        return "visualizando pagina de login!"


@app.route('/usuarios/', methods=['POST'])
def newUsuario():
    if request.method == "POST":
        return "novo usuario criado!";


@app.route("/categorias/new/", methods=["GET", "POST"])
def newCategoria():
    if request.method == 'POST':
        newCategoria = Categoria(nome=request.form['nome'])
        session.add(newCategoria)
        session.commit()
        flash("Nova categoria criada!")
        return redirect(url_for("showCategoria"))
    else: 
        return render_template("newCategoria.html")


@app.route("/categorias/<int:categoria>/")
def showCategoria(categoria):
    todasCategorias = session.query(Categoria).all()
    umaCategoria = session.query(Categoria).filter_by(id=categoria).one()
    if umaCategoria is None:
        return showCategorias()
    else:
        return render_template("showCategoria.html", categorias=todasCategorias, categoria=umaCategoria)


@app.route("/categorias/<int:categoria>/edit/", methods=["GET", "POST"])
def editCategoria(categoria):
    umaCategoria = session.query(Categoria).filter_by(id=categoria).one()
    if umaCategoria is None:
        return showCategorias()
    else:
        if request.method == 'POST':
            umaCategoria.nome = request.form['nome']
            session.add(umaCategoria)
            session.commit()
            flash("A categoria foi editada!")
            return redirect(url_for("showCategoria", categoria=umaCategoria.id))
        else: 
            return render_template("editCategoria.html", categoria=umaCategoria)


@app.route("/categorias/<int:categoria>/delete/", methods=["GET", "POST"])
def deleteCategoria(categoria):
    umaCategoria = session.query(Categoria).filter_by(id=categoria).one()
    if umaCategoria is None:
        return showCategorias()
    else:
        if request.method == 'POST':
            session.delete(umaCategoria)
            session.commit()
            flash("A categoria foi excluída!")
            return redirect(url_for("showCategorias"))
        else: 
            return render_template("deleteCategoria.html", categoria=umaCategoria)

@app.route("/categorias/<int:categoria>/<int:item>/")
def showItem(categoria, item):
    umItem = session.query(Item).filter_by(id=item, categoria_id=categoria).one()
    if umItem is None:
        return showCategoria(categoria=categoria)
    else:
        return render_template("showItem.html", item=umItem)

@app.route("/categorias/<int:categoria>/new/", methods=["GET", "POST"])
def newItem(categoria):
    umaCategoria = session.query(Categoria).filter_by(id=categoria).one()
    if umaCategoria is None:
        return showCategorias()
    else:
        if request.method == 'POST':
            newItem = Item(nome=request.form['nome'],
                            descricao=request.form['descricao'],
                            imagem=request.form['imagem'],
                            categoria=umaCategoria)
            session.add(newItem)
            session.commit()
            flash("Novo item criado!")
            return redirect(url_for("showItem", item=newItem.id))
        else: 
            return render_template("newItem.html", categoria=umaCategoria)


@app.route("/categorias/<int:categoria>/<int:item>/edit/", methods=["GET", "POST"])
def editItem(categoria, item):
    umItem = session.query(Item).filter_by(id=item, categoria_id=categoria).one()
    if umItem is None:
        return showCategoria(categoria=categoria)
    else:
        if request.method == 'POST':
            umItem = Item(nome=request.form['nome'],
                            descricao=request.form['descricao'],
                            imagem=request.form['imagem'],
                            categoria=umaCategoria)
            session.add(umItem)
            session.commit()
            flash("O item foi editado!")
            return redirect(url_for("showItem", item=newItem.id))
        else: 
            return render_template("editItem.html", item=umItem)


@app.route("/categorias/<int:categoria>/<int:item>/delete/", methods=["GET", "POST"])
def deleteItem(categoria, item):
    umItem = session.query(Item).filter_by(id=item, categoria_id=categoria).one()
    if umItem is None:
        return showCategoria(categoria=categoria)
    else:
        if request.method == 'POST':
            session.delete(umItem)
            session.commit()
            flash("O item foi excluído!")
            return redirect(url_for("showCategoria", categoria=categoria))
        else: 
            return render_template("editItem.html", item=umItem)


@app.route('/api/v1/categorias')
def jsonCategorias():
    categorias = session.query(Categoria).all()
    return jsonify(categorias = [c.serialize for c in categorias])


@app.route('/api/v1/categorias/<int:categoria>')
def jsonCategoria(categoria):
    categoria = session.query(Categoria).filter_by(id=categoria).one()
    return jsonify(categorias = categoria.serialize)


@app.route('/api/v1/categorias/<int:categoria>/<int:item>')
def jsonItem(categoria, item):
    item = session.query(Item).filter_by(id=item, categoria_id=categoria).one()
    return jsonify(item = item.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
