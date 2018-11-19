# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from catalogo import *
from flask import Blueprint
import hashlib
import os

itens = Blueprint(
    "itens", __name__,
    url_prefix="/categorias/<int:categoria>",
    template_folder="templates/itens")


def arquivoPermitido(arquivo):
    return '.' in arquivo and \
           arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS


@itens.route("/<int:item>/")
def showItem(categoria, item):
    umItem = Item.query.filter_by(
        id=item, categoria_id=categoria).one_or_none()
    if umItem is None:
        flash(u"Erro: O item que você está tentando acessar não existe!")
        return redirect(
            url_for("categorias.showCategoria", categoria=categoria))
    else:
        if "usuario_id" not in login_session:
            return render_template(
                "itens/showItemPublica.html", item=umItem)
        return render_template(
            "itens/showItem.html", item=umItem,
            usuario_id=login_session["usuario_id"])


@itens.route("/new/", methods=["GET", "POST"])
def newItem(categoria):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono desta categoria
    if "usuario_id" not in login_session:
        flash(u"Você precisa estar logado para acessar esta página.")
        return redirect(url_for("usuarios.loginUsuario"))
    umaCategoria = Categoria.query.filter_by(id=categoria).one_or_none()
    if umaCategoria is None:
        flash(u"Erro: A categoria que você está tentando acessar não existe!")
        return redirect(url_for("categorias.showCategorias"))
    if login_session["usuario_id"] != umaCategoria.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return redirect(
            url_for("categorias.showCategoria", categoria=umaCategoria.id))

    if request.method == "POST":
        umUsuario = usuarios.getUsuario(login_session["usuario_id"])

        newItem = Item(
            nome=request.form["nome"], descricao=request.form["descricao"],
            imagem="item_sem_imagem.png", categoria=umaCategoria,
            usuario=umUsuario)
        db.session.add(newItem)
        db.session.flush()
        item_id = newItem.id
        db.session.commit()

        # se o usuário enviar uma imagem, envia para o servidor
        # com o nome equivalente ao seu id em hash
        if "imagem" in request.files and \
                request.files["imagem"].filename != "" and \
                request.files["imagem"]:
            arquivo = request.files["imagem"]
            tipo_imagem = arquivo.filename.rsplit(".", 1)[1].lower()
            imagem_nome = hashlib.sha1(
                str(item_id).encode("utf-8")).hexdigest() + "." + tipo_imagem
            imagemUpload.save(arquivo, name=imagem_nome)
            newItem.imagem = imagem_nome
            db.session.add(newItem)
            db.session.commit()
        flash("Novo item criado!")
        return redirect(url_for(
            "itens.showItem", categoria=categoria, item=newItem.id))
    else:
        return render_template("newItem.html", categoria=umaCategoria)


@itens.route("<int:item>/edit/", methods=["GET", "POST"])
def editItem(categoria, item):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono deste item
    if "usuario_id" not in login_session:
        flash(u"Você precisa estar logado para acessar esta página.")
        return redirect(url_for("usuarios.loginUsuario"))
    umItem = Item.query.filter_by(
        id=item, categoria_id=categoria).one_or_none()
    if umItem is None:
        flash(u"Erro: O item que você está tentando acessar não existe!")
        return redirect(
            url_for("categorias.showCategoria", categoria=categoria))
    if login_session["usuario_id"] != umItem.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return redirect(
            url_for("itens.showItem", categoria=categoria, item=item))

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
                    str(umItem.id).encode("utf-8")).hexdigest() + "." + tipo_imagem
                umItem.imagem = imagem_nome

            imagemUpload.save(arquivo, name=umItem.imagem)

        umItem.nome = request.form["nome"]
        umItem.descricao = request.form["descricao"]
        db.session.add(umItem)
        db.session.commit()
        flash("O item foi editado!")
        return redirect(
            url_for("itens.showItem", categoria=categoria, item=item))
    else:
        return render_template("editItem.html", item=umItem)


@itens.route("<int:item>/delete/", methods=["GET", "POST"])
def deleteItem(categoria, item):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono deste item
    if "usuario_id" not in login_session:
        flash(u"Você precisa estar logado para acessar esta página.")
        return redirect(url_for("usuarios.loginUsuario"))
    umItem = Item.query.filter_by(
        id=item, categoria_id=categoria).one_or_none()
    if umItem is None:
        flash(u"Erro: O item que você está tentando acessar não existe!")
        redirect(
            url_for("categorias.showCategoria", categoria=categoria))
    if login_session["usuario_id"] != umItem.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return redirect(
            url_for("itens.showItem", categoria=categoria, item=item))

    if request.method == "POST":
        if umItem.imagem != "item_sem_imagem.png":
            try:
                os.remove(os.path.join(
                    app.config["UPLOADED_IMAGEM_DEST"], umItem.imagem))
            except OSError:
                pass
        db.session.delete(umItem)
        db.session.commit()
        flash(u"O item foi excluído!")
        return redirect(
            url_for("categorias.showCategoria", categoria=categoria))
    else:
        return render_template("deleteItem.html", item=umItem)
