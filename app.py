# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from configuracao_db import Base, Usuario, Categoria, Item, engine
from flask import (
    Flask, jsonify, request, url_for, g,
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


DIRETORIO_UPLOAD = "static/img"

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
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
    session = DBSession()
    todasCategorias = session.query(Categoria).all()
    itensRecentes = session.query(Item).order_by(Item.id.desc()).limit(8).all()
    session.close()
    pagina = "showCategorias.html"
    if "usuario_id" not in login_session:
        pagina = "showCategoriasPublica.html"
    return render_template(
        pagina, categorias=todasCategorias, itens=itensRecentes)


@app.route("/login/", methods=["GET", "POST"])
def loginUsuario():
    # trecho de validação de login de usuário retirado de:
    # https://github.com/udacity/ud330/blob/master/Lesson2/step5/project.py
    if request.method == "POST":
        # valida state token
        if request.args.get("state") != login_session["state"]:
            response = make_response(json.dumps(
                u"Parâmetro de state inválido."), 401)
            response.headers["Content-Type"] = "application/json"
            return response
        # Obtain authorization code
        code = request.data

        try:
            # atualiza o código de autorização em um objeto de credenciais
            oauth_flow = flow_from_clientsecrets(
                "segredos_cliente.json", scope="")
            oauth_flow.redirect_uri = "postmessage"
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(
                json.dumps(
                    u"Falha ao tentar atualizar código de autenticação"), 401)
            response.headers["Content-Type"] = "application/json"
            return response

        # verifica se o token de acesso é valido
        access_token = credentials.access_token
        url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s"
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, "GET")[1])
        # se houver algum problema, retornar erro
        if result.get("error") is not None:
            response = make_response(json.dumps(result.get("error")), 500)
            response.headers["Content-Type"] = "application/json"
            return response

        # verifica se o token é do usuário correto
        gplus_id = credentials.id_token["sub"]
        if result["user_id"] != gplus_id:
            response = make_response(
                json.dumps(
                    u"ID de usuário do token não bate com o ID dado."), 401)
            response.headers["Content-Type"] = "application/json"
            return response

        # verifica se o token é válido para o site
        if result["issued_to"] != ID_CLIENTE:
            response = make_response(
                json.dumps(
                    u"ID de usuário do token não bate com o ID no site."), 401)
            response.headers["Content-Type"] = "application/json"
            return response

        stored_access_token = login_session.get("access_token")
        stored_gplus_id = login_session.get("gplus_id")
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            response = make_response(
                            json.dumps(u"Usuário já está conectado."),
                            200)
            response.headers["Content-Type"] = "application/json"
            return response

        # guarda o token de acesso para uso futuro
        login_session["access_token"] = credentials.access_token
        login_session["gplus_id"] = gplus_id

        # obtêm informações do usuário
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": credentials.access_token, "alt": "json"}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session["nome"] = data["name"]
        login_session["imagem"] = data["picture"]
        login_session["email"] = data["email"]

        output = ""

        # verifica se usuário já existe no banco de dados. se sim
        # só adiciona na sessão o seu id, senão, adicione ao
        # banco de dados e adiciona na sessão seu id
        if not getUsuarioId(login_session["email"]):
            login_session["usuario_id"] = newUsuario(login_session)
            output += "<h1>Bem vindo(a), "
        else:
            login_session["usuario_id"] = getUsuarioId(login_session["email"])
            output += "<h1>Bem vindo(a) de volta, <strong>"

        output += login_session["nome"]
        output += "</strong>!</h1>"
        output += "<img src='"
        output += login_session["imagem"]
        output += '''' style = 'width: 300px; height: 300px;
        border-radius: 150px;-webkit-border-radius: 150px;
        -moz-border-radius: 150px;'>'''
        flash(u"Você está logado como %s" % login_session["nome"])
        return output
    else:
        state = "".join(random.choice(
                string.ascii_uppercase + string.digits) for x in xrange(32))
        login_session["state"] = state
        return render_template(
            "loginUsuario.html", id_cliente=ID_CLIENTE, state=state)


@app.route("/logout/")
def logoutUsuario():
    access_token = login_session.get("access_token")
    if access_token is None:
        flash(u"Usuário não conectado.")
        return redirect(url_for("showCategorias"))

    # desloga o usuário tanto no aplicativo tanto na api do google
    url = ("https://accounts.google.com/o/oauth2/revoke?token=%s"
           % login_session["access_token"])

    h = httplib2.Http()
    result = h.request(url, "GET")[0]
    if result["status"] == "200":
        del login_session["access_token"]
        del login_session["gplus_id"]
        del login_session["nome"]
        del login_session["email"]
        del login_session["imagem"]
        del login_session["usuario_id"]
        flash(u"Usuário desconectado com sucesso.")
    else:
        flash(u"Falha ao tentar desconectar usuário.")
        return redirect(url_for("showCategorias"))

    return render_template("logoutUsuario.html", id_cliente=ID_CLIENTE)


def newUsuario(login_session):
    session = DBSession()
    newUsuario = Usuario(
        nome=login_session["nome"], email=login_session["email"],
        imagem=login_session["imagem"])
    session.add(newUsuario)
    session.commit()
    usuario = session.query(
        Usuario).filter_by(email=login_session["email"]).one_or_none()
    session.close()
    return usuario.id


def getUsuario(usuario_id):
    session = DBSession()
    usuario = session.query(
        Usuario).filter_by(id=usuario_id).one_or_none()
    session.close()
    return usuario


def getUsuarioId(email):
    session = DBSession()
    usuario = session.query(
        Usuario).filter_by(email=email).one_or_none()
    session.close()
    if usuario is None:
        return None
    else:
        return usuario.id


@app.route("/categorias/new/", methods=["GET", "POST"])
def newCategoria():
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    if request.method == "POST":
        session = DBSession()
        umUsuario = getUsuario(login_session["usuario_id"])
        newCategoria = Categoria(nome=request.form["nome"], usuario=umUsuario)
        session.add(newCategoria)
        session.commit()
        session.close()
        flash("Nova categoria criada!")
        return redirect(url_for("showCategorias"))

    return render_template("newCategoria.html")


@app.route("/categorias/<int:categoria>/")
def showCategoria(categoria):
    session = DBSession()
    todasCategorias = session.query(Categoria).all()
    umaCategoria = session.query(
        Categoria).filter_by(id=categoria).one_or_none()
    # verifica se a categoria existe no banco, senão, retorna
    # para a página de categorias
    if umaCategoria is None:
        return showCategorias()
    seusItens = session.query(Item).filter_by(categoria_id=categoria).all()
    session.close()
    # verifica se há algun usuário logado. se sim, renderiza a página
    # de usuário, senão, renderiza a página pública
    if "usuario_id" not in login_session:
        return render_template(
            "showCategoriaPublica.html", categorias=todasCategorias,
            categoria=umaCategoria, itens=seusItens)
    return render_template(
        "showCategoria.html",
        categorias=todasCategorias, categoria=umaCategoria, itens=seusItens,
        usuario_id=login_session["usuario_id"])


@app.route("/categorias/<int:categoria>/edit/", methods=["GET", "POST"])
def editCategoria(categoria):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono desta categoria
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    session = DBSession()
    umaCategoria = session.query(
        Categoria).filter_by(id=categoria).one_or_none()
    if umaCategoria is None:
        return showCategorias()
    if login_session["usuario_id"] != umaCategoria.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=umaCategoria.id)

    if request.method == "POST":
        umaCategoria.nome = request.form["nome"]
        session.add(umaCategoria)
        session.commit()
        session.close()
        flash("A categoria foi editada!")
        return redirect(url_for("showCategoria", categoria=umaCategoria.id))
    else:
        return render_template("editCategoria.html", categoria=umaCategoria)


@app.route("/categorias/<int:categoria>/delete/", methods=["GET", "POST"])
def deleteCategoria(categoria):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono desta categoria
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    session = DBSession()
    umaCategoria = session.query(
        Categoria).filter_by(id=categoria).one_or_none()
    if umaCategoria is None:
        return showCategorias()
    if login_session["usuario_id"] != umaCategoria.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=umaCategoria.id)

    if request.method == "POST":
        itens = session.query(Item).filter_by(categoria_id=categoria).all()
        # verifica se cada item a se deletado possui uma imagem
        # customizada. se sim, ela deve ser excluída do servidor
        for i in itens:
            if i.imagem != "item_sem_imagem.png":
                try:
                    os.remove(
                        os.path.join(
                            app.config["UPLOADED_IMAGEM_DEST"], i.imagem))
                except OSError:
                    pass

        session.query(Item).filter_by(categoria_id=categoria).delete()
        session.delete(umaCategoria)
        session.commit()
        session.close()
        flash(u"A categoria foi excluída! Seus itens também foram excluídos!")
        return redirect(url_for("showCategorias"))
    else:
        return render_template("deleteCategoria.html", categoria=umaCategoria)


@app.route("/categorias/<int:categoria>/<int:item>/")
def showItem(categoria, item):
    session = DBSession()
    umItem = session.query(Item).filter_by(
        id=item, categoria_id=categoria).one_or_none()
    session.close()
    if umItem is None:
        return showCategoria(categoria=categoria)
    else:
        if "usuario_id" not in login_session:
            return render_template("showItemPublica.html", item=umItem)
        return render_template(
            "showItem.html", item=umItem,
            usuario_id=login_session["usuario_id"])


@app.route("/categorias/<int:categoria>/new/", methods=["GET", "POST"])
def newItem(categoria):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono desta categoria
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    session = DBSession()
    umaCategoria = session.query(
        Categoria).filter_by(id=categoria).one_or_none()
    if umaCategoria is None:
        return showCategorias()
    if login_session["usuario_id"] != umaCategoria.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=umaCategoria.id)

    if request.method == "POST":
        umUsuario = getUsuario(login_session["usuario_id"])

        newItem = Item(
            nome=request.form["nome"], descricao=request.form["descricao"],
            imagem="item_sem_imagem.png", categoria=umaCategoria,
            usuario=umUsuario)
        session.add(newItem)
        session.flush()
        item_id = newItem.id
        session.commit()

        # se o usuário enviar uma imagem, envia para o servidor
        # com o nome equivalente ao seu id em hash
        if "imagem" in request.files and \
                request.files["imagem"].filename != "" and \
                request.files["imagem"]:
            arquivo = request.files["imagem"]
            tipo_imagem = arquivo.filename.rsplit(".", 1)[1].lower()
            imagem_nome = hashlib.sha1(
                str(item_id)).hexdigest() + "." + tipo_imagem
            imagemUpload.save(arquivo, name=imagem_nome)
            newItem.imagem = imagem_nome
            session.add(newItem)
            session.commit()
        session.close()
        flash("Novo item criado!")
        return redirect(url_for("showCategoria", categoria=categoria))
    else:
        return render_template("newItem.html", categoria=umaCategoria)


@app.route(
    "/categorias/<int:categoria>/<int:item>/edit/", methods=["GET", "POST"])
def editItem(categoria, item):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono deste item
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    session = DBSession()
    umItem = session.query(Item).filter_by(
        id=item, categoria_id=categoria).one_or_none()
    if umItem is None:
        return showCategoria(categoria=categoria)
    if login_session["usuario_id"] != umItem.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=categoria)

    if request.method == "POST":

        # se o usuário enviar uma imagem, verifica se existe alguma imagem
        # antes, se sim, apaga a imagem anterior, envia a nova para o
        # servidor com o nome equivalente ao seu id em hash
        if "imagem" in request.files and \
                request.files["imagem"].filename != "" and \
                request.files["imagem"]:
            arquivo = request.files["imagem"]
            if umItem.imagem != "item_sem_imagem.png":
                try:
                    os.remove(os.path.join(
                        app.config["UPLOADED_IMAGEM_DEST"], umItem.imagem))
                except OSError:
                    pass
            else:
                tipo_imagem = arquivo.filename.rsplit(".", 1)[1].lower()
                imagem_nome = hashlib.sha1(
                    str(umItem.id)).hexdigest() + "." + tipo_imagem
                umItem.imagem = imagem_nome

            imagemUpload.save(arquivo, name=umItem.imagem)

        umItem.nome = request.form["nome"]
        umItem.descricao = request.form["descricao"]
        session.add(umItem)
        session.commit()
        session.close()
        flash("O item foi editado!")
        return redirect(url_for("showCategoria", categoria=categoria))
    else:
        return render_template("editItem.html", item=umItem)


@app.route(
    "/categorias/<int:categoria>/<int:item>/delete/", methods=["GET", "POST"])
def deleteItem(categoria, item):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono deste item
    if "usuario_id" not in login_session:
        return redirect(url_for("loginUsuario"))
    session = DBSession()
    umItem = session.query(Item).filter_by(
        id=item, categoria_id=categoria).one_or_none()
    if umItem is None:
        return showCategoria(categoria=categoria)
    if login_session["usuario_id"] != umItem.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return showCategoria(categoria=categoria)

    if request.method == "POST":
        if umItem.imagem != "item_sem_imagem.png":
            try:
                os.remove(os.path.join(
                    app.config["UPLOADED_IMAGEM_DEST"], umItem.imagem))
            except OSError:
                pass
        session.delete(umItem)
        session.commit()
        session.close()
        flash(u"O item foi excluído!")
        return redirect(url_for("showCategoria", categoria=categoria))
    else:
        return render_template("deleteItem.html", item=umItem)


@app.route("/api/v1/categorias")
def jsonCategorias():
    session = DBSession()
    categorias = session.query(Categoria).all()
    categoriasSerializadas = []
    # serializa cada item das categorias, e depois cria uma lista
    # de itens serializados para juntar com a categoria serializada
    # correspondente
    for c in categorias:
        itens = session.query(Item).filter_by(categoria_id=c.id).all()
        itensSerializados = []
        for i in itens:
            itensSerializados.append(i.serialize)
        categoriaSerializada = c.serialize
        categoriaSerializada["itens"] = itensSerializados
        categoriasSerializadas.append(categoriaSerializada)
    session.close()
    return jsonify(categorias=categoriasSerializadas)


@app.route("/api/v1/categorias/<int:categoria>")
def jsonCategoria(categoria):
    session = DBSession()
    categoria = session.query(Categoria).filter_by(id=categoria).one_or_none()
    itens = session.query(Item).filter_by(categoria_id=categoria.id).all()
    # serializa cada item das categoria, e depois cria uma lista
    # de itens serializados para juntar com a categoria serializada
    itensSerializados = []
    for i in itens:
        itensSerializados.append(i.serialize)
    categoriaSerializada = categoria.serialize
    categoriaSerializada["itens"] = itensSerializados
    session.close()
    return jsonify(categoria=categoriaSerializada)


@app.route("/api/v1/categorias/<int:categoria>/<int:item>")
def jsonItem(categoria, item):
    session = DBSession()
    item = session.query(
        Item).filter_by(id=item, categoria_id=categoria).one_or_none()
    session.close()
    return jsonify(item=item.serialize)


if __name__ == "__main__":
    app.secret_key = "super_chave_secreta"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
