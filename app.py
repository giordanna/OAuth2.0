# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from configuracao_db import Base, Usuario, Categoria, Item, engine
from flask import (
    Flask, jsonify, request, url_for,
    abort, g, render_template, flash, redirect
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask.ext.httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
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
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES

DIRETORIO_UPLOAD = "static/img"

auth = HTTPBasicAuth()

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
app = Flask(__name__)

imagemUpload = UploadSet("imagem", IMAGES)
app.config["UPLOADED_IMAGEM_DEST"] = DIRETORIO_UPLOAD
configure_uploads(app, imagemUpload)


ID_CLIENTE = json.loads(
    open("segredos_cliente.json", "r").read())["web"]["client_id"]

def arquivoPermitido(arquivo):
    return '.' in arquivo and \
           arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

@app.route("/")
@app.route("/categorias/")
def showCategorias():
    todasCategorias = session.query(Categoria).all()
    itensRecentes = session.query(Item).order_by(Item.id.desc()).limit(8)

    pagina = "showCategorias.html"
    if "usuario_id" not in login_session:
        pagina = "showCategoriasPublica.html"
    return render_template(pagina, categorias=todasCategorias, itens=itensRecentes)


@app.route("/login/", methods=["GET", "POST"])
def loginUsuario():
    if request.method == "POST":
        # Validate state token
        if request.args.get("state") != login_session["state"]:
            response = make_response(json.dumps("Invalid state parameter."), 401)
            response.headers["Content-Type"] = "application/json"
            return response
        # Obtain authorization code
        code = request.data

        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets("segredos_cliente.json", scope="")
            oauth_flow.redirect_uri = "postmessage"
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(
                json.dumps("Failed to upgrade the authorization code."), 401)
            response.headers["Content-Type"] = "application/json"
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s"
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, "GET")[1])
        # If there was an error in the access token info, abort.
        if result.get("error") is not None:
            response = make_response(json.dumps(result.get("error")), 500)
            response.headers["Content-Type"] = "application/json"
            return response

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token["sub"]
        if result["user_id"] != gplus_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers["Content-Type"] = "application/json"
            return response

        # Verify that the access token is valid for this app.
        if result["issued_to"] != ID_CLIENTE:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            print "Token's client ID does not match app's."
            response.headers["Content-Type"] = "application/json"
            return response

        stored_access_token = login_session.get("access_token")
        stored_gplus_id = login_session.get("gplus_id")
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps("Current user is already connected."),
                                     200)
            response.headers["Content-Type"] = "application/json"
            return response

        # Store the access token in the session for later use.
        login_session["access_token"] = credentials.access_token
        login_session["gplus_id"] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": credentials.access_token, "alt": "json"}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session["nome"] = data["name"]
        login_session["imagem"] = data["picture"]
        login_session["email"] = data["email"]

        output = ""

        if not getUsuarioId(login_session["email"]):
            login_session["usuario_id"] = newUsuario(login_session)
            output += "<h1>Welcome, "
        else:
            login_session["usuario_id"] = getUsuarioId(login_session["email"])
            output += "<h1>Welcome back, "
 
        output += login_session["nome"]
        output += "!</h1>"
        output += "<img src='"
        output += login_session["imagem"]
        output += "' style = 'width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;'> "
        flash("you are now logged in as %s" % login_session["nome"])
        print "done!"
        return output
    else:
        state = "".join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
        login_session["state"] = state
        return render_template("loginUsuario.html", id_cliente=ID_CLIENTE, state=state)

@app.route("/logout/")
def logoutUsuario():
    access_token = login_session.get("access_token")
    if access_token is None:
        print "Access Token is None"
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    print "In gdisconnect access token is %s", access_token
    print "User name is: "
    print login_session["nome"]
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % login_session["access_token"]
    h = httplib2.Http()
    result = h.request(url, "GET")[0]
    print "result is "
    print result
    if result["status"] == "200":
        del login_session["access_token"]
        del login_session["gplus_id"]
        del login_session["nome"]
        del login_session["email"]
        del login_session["imagem"]
        del login_session["usuario_id"]
        response = make_response(json.dumps("Successfully disconnected."), 200)
        response.headers["Content-Type"] = "application/json"
    else:
        response = make_response(json.dumps("Failed to revoke token for given user.", 400))
        response.headers["Content-Type"] = "application/json"
    return response

def newUsuario(login_session):
    newUsuario = Usuario(nome=login_session["nome"],
                        email=login_session["email"],
                        imagem=login_session["imagem"])
    session.add(newUsuario)
    session.commit()
    usuario = session.query(Usuario).filter_by(email=login_session["email"]).one()
    return usuario.id


def getUsuario(usuario_id):
    usuario = session.query(Usuario).filter_by(id=usuario_id).one()
    return usuario


def getUsuarioId(email):
    try:
        usuario = session.query(Usuario).filter_by(email=email).one()
        return usuario.id
    except:
        return None

@app.route("/categorias/new/", methods=["GET", "POST"])
def newCategoria():
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    if request.method == "POST":
        umUsuario = getUsuario(login_session["usuario_id"])
        newCategoria = Categoria(nome=request.form["nome"], usuario=umUsuario)
        session.add(newCategoria)
        session.commit()
        flash("Nova categoria criada!")
        return redirect(url_for("showCategorias"))

    return render_template("newCategoria.html")


@app.route("/categorias/<int:categoria>/")
def showCategoria(categoria):
    todasCategorias = session.query(Categoria).all()
    umaCategoria = session.query(Categoria).filter_by(id=categoria).one()
    if umaCategoria is None:
        return showCategorias()
    seusItens = session.query(Item).filter_by(categoria_id=categoria).all()

    if "usuario_id" not in login_session:
        return render_template("showCategoriaPublica.html", categorias=todasCategorias, categoria=umaCategoria, itens=seusItens)
    return render_template("showCategoria.html", categorias=todasCategorias, categoria=umaCategoria, itens=seusItens, usuario_id=login_session["usuario_id"])


@app.route("/categorias/<int:categoria>/edit/", methods=["GET", "POST"])
def editCategoria(categoria):
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    umaCategoria = session.query(Categoria).filter_by(id=categoria).one()
    if umaCategoria is None:
        return showCategorias()
    if login_session["usuario_id"] != umaCategoria.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=umaCategoria.id)

    if request.method == "POST":
        umaCategoria.nome = request.form["nome"]
        session.add(umaCategoria)
        session.commit()
        flash("A categoria foi editada!")
        return redirect(url_for("showCategoria", categoria=umaCategoria.id))
    else: 
        return render_template("editCategoria.html", categoria=umaCategoria)


@app.route("/categorias/<int:categoria>/delete/", methods=["GET", "POST"])
def deleteCategoria(categoria):
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    umaCategoria = session.query(Categoria).filter_by(id=categoria).one()
    if umaCategoria is None:
        return showCategorias()
    if login_session["usuario_id"] != umaCategoria.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=umaCategoria.id)

    if request.method == "POST":
        itens = session.query(Item).filter_by(categoria_id=categoria).all()
        for i in itens:
            if i.imagem != "item_sem_imagem.png":
                try:
                    os.remove(os.path.join(app.config["UPLOADED_IMAGEM_DEST"], i.imagem))
                except OSError:
                    pass

        session.query(Item).filter_by(categoria_id=categoria).delete()
        session.delete(umaCategoria)
        session.commit()
        flash(u"A categoria foi excluída! Seus itens também foram excluídos!")
        return redirect(url_for("showCategorias"))
    else: 
        return render_template("deleteCategoria.html", categoria=umaCategoria)

@app.route("/categorias/<int:categoria>/<int:item>/")
def showItem(categoria, item):
    umItem = session.query(Item).filter_by(id=item, categoria_id=categoria).one()
    if umItem is None:
        return showCategoria(categoria=categoria)
    else:
        if "usuario_id" not in login_session:
            return render_template("showItemPublica.html", item=umItem)
        return render_template("showItem.html", item=umItem, usuario_id=login_session["usuario_id"])

@app.route("/categorias/<int:categoria>/new/", methods=["GET", "POST"])
def newItem(categoria):
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    umaCategoria = session.query(Categoria).filter_by(id=categoria).one()
    if umaCategoria is None:
        return showCategorias()
    if login_session["usuario_id"] != umaCategoria.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=umaCategoria.id)

    if request.method == "POST":
        umUsuario = getUsuario(login_session["usuario_id"])

        newItem = Item(nome=request.form["nome"],
                        descricao=request.form["descricao"],
                        imagem="item_sem_imagem.png",
                        categoria=umaCategoria,
                        usuario=umUsuario)
        session.add(newItem)
        session.flush()
        item_id = newItem.id
        session.commit()

        # se o usuário enviar uma imagem
        if "imagem" in request.files:
            arquivo = request.files["imagem"]
            tipo_imagem = arquivo.filename.rsplit(".", 1)[1].lower()
            imagem_nome = hashlib.sha1(str(item_id)).hexdigest() + "." + tipo_imagem
            imagemUpload.save(arquivo, name=imagem_nome)
            newItem.imagem = imagem_nome
            session.add(newItem)
            session.commit()

        flash("Novo item criado!")
        return redirect(url_for("showCategoria", categoria=categoria))
    else: 
        return render_template("newItem.html", categoria=umaCategoria)


@app.route("/categorias/<int:categoria>/<int:item>/edit/", methods=["GET", "POST"])
def editItem(categoria, item):
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    umItem = session.query(Item).filter_by(id=item, categoria_id=categoria).one()
    if umItem is None:
        return showCategoria(categoria=categoria)
    if login_session["usuario_id"] != umItem.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=categoria)

    if request.method == "POST":

        # se o usuário enviar uma imagem
        if "imagem" in request.files:
            arquivo = request.files["imagem"]
            if umItem.imagem != "item_sem_imagem.png":
                try:
                    os.remove(os.path.join(app.config["UPLOADED_IMAGEM_DEST"], umItem.imagem))
                except OSError:
                    pass
            else:
                tipo_imagem = arquivo.filename.rsplit(".", 1)[1].lower()
                imagem_nome = hashlib.sha1(str(item_id)).hexdigest() + "." + tipo_imagem
                umItem.imagem = imagem_nome

            imagemUpload.save(arquivo, name=umItem.imagem)

        umItem.nome = request.form["nome"]
        umItem.descricao = request.form["descricao"]
        session.add(umItem)
        session.commit()
        flash("O item foi editado!")
        return redirect(url_for("showCategoria", categoria=categoria))
    else: 
        return render_template("editItem.html", item=umItem)


@app.route("/categorias/<int:categoria>/<int:item>/delete/", methods=["GET", "POST"])
def deleteItem(categoria, item):
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    umItem = session.query(Item).filter_by(id=item, categoria_id=categoria).one()
    if umItem is None:
        return showCategoria(categoria=categoria)
    if login_session["usuario_id"] != umItem.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=categoria)

    if request.method == "POST":
        if umItem.imagem != "item_sem_imagem.png":
            try:
                os.remove(os.path.join(app.config["UPLOADED_IMAGEM_DEST"], umItem.imagem))
            except OSError:
                pass
        session.delete(umItem)
        session.commit()
        flash(u"O item foi excluído!")
        return redirect(url_for("showCategoria", categoria=categoria))
    else: 
        return render_template("deleteItem.html", item=umItem)


@app.route("/api/v1/categorias")
def jsonCategorias():
    categorias = session.query(Categoria).all()
    categoriasSerializadas = []
    for c in categorias:
        itens = session.query(Item).filter_by(categoria_id=c.id).all()
        itensSerializados = []
        for i in itens:
            itensSerializados.append(i.serialize)
        categoriaSerializada = c.serialize
        categoriaSerializada["itens"] = itensSerializados
        categoriasSerializadas.append(categoriaSerializada)
    
    return jsonify(categorias = categoriasSerializadas)


@app.route("/api/v1/categorias/<int:categoria>")
def jsonCategoria(categoria):
    categoria = session.query(Categoria).filter_by(id=categoria).one()
    itens = session.query(Item).filter_by(categoria_id=categoria.id).all()
    itensSerializados = []
    for i in itens:
        itensSerializados.append(i.serialize)
    categoriaSerializada = categoria.serialize
    categoriaSerializada["itens"] = itensSerializados

    return jsonify(categoria = categoriaSerializada)


@app.route("/api/v1/categorias/<int:categoria>/<int:item>")
def jsonItem(categoria, item):
    item = session.query(Item).filter_by(id=item, categoria_id=categoria).one()
    
    return jsonify(item = item.serialize)


if __name__ == "__main__":
    app.secret_key = "super_chave_secreta"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
