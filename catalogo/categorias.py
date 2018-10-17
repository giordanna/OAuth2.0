# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from catalogo import *
from flask import Blueprint
import os

categorias = Blueprint(
    "categorias", __name__,
    url_prefix="/categorias",
    template_folder="templates/categorias")


@categorias.route("/")
def showCategorias():
    todasCategorias = Categoria.query.all()
    itensRecentes = Item.query.order_by(Item.id.desc()).limit(8).all()
    pagina = "showCategorias.html"
    if "usuario_id" not in login_session:
        pagina = "showCategoriasPublica.html"
    return render_template(
        pagina, categorias=todasCategorias, itens=itensRecentes)


@categorias.route("/new/", methods=["GET", "POST"])
def newCategoria():
    if "usuario_id" not in login_session:
        flash(u"Você precisa estar logado para acessar esta página.")
        return redirect(url_for("usuarios.loginUsuario"))
    if request.method == "POST":
        umUsuario = usuarios.getUsuario(login_session["usuario_id"])
        newCategoria = Categoria(nome=request.form["nome"], usuario=umUsuario)
        db.session.add(newCategoria)
        db.session.commit()
        flash("Nova categoria criada!")
        return redirect(url_for("categorias.showCategorias"))

    return render_template("newCategoria.html")


@categorias.route("/<int:categoria>/")
def showCategoria(categoria):
    todasCategorias = Categoria.query.all()
    umaCategoria = Categoria.query.filter_by(id=categoria).one_or_none()
    # verifica se a categoria existe no banco, senão, retorna
    # para a página de categorias
    if umaCategoria is None:
        flash(u"Erro: A categoria você está tentando acessar não existe!")
        return redirect(url_for("categorias.showCategorias"))
    seusItens = Item.query.filter_by(categoria_id=categoria).all()
    # verifica se há algun usuário logado. se sim, renderiza a página
    # de usuário, senão, renderiza a página pública
    if "usuario_id" not in login_session:
        return render_template(
            "showCategoriaPublica.html", categorias=todasCategorias,
            categoria=umaCategoria, itens=seusItens)
    return render_template(
        "showCategoria.html", categorias=todasCategorias,
        categoria=umaCategoria, itens=seusItens,
        usuario_id=login_session["usuario_id"])


@categorias.route("/<int:categoria>/edit/", methods=["GET", "POST"])
def editCategoria(categoria):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono desta categoria
    if "usuario_id" not in login_session:
        flash(u"Você precisa estar logado para acessar esta página.")
        return redirect(url_for("usuarios.loginUsuario"))
    umaCategoria = Categoria.query.filter_by(id=categoria).one_or_none()
    if umaCategoria is None:
        flash(u"Erro: A categoria você está tentando acessar não existe!")
        return redirect(url_for("categorias.showCategorias"))
    if login_session["usuario_id"] != umaCategoria.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return redirect(url_for(
            "categorias.showCategoria", categoria=umaCategoria.id))

    if request.method == "POST":
        umaCategoria.nome = request.form["nome"]
        db.session.add(umaCategoria)
        db.session.commit()
        flash("A categoria foi editada!")
        return redirect(url_for(
            "categorias.showCategoria", categoria=umaCategoria.id))
    else:
        return render_template("editCategoria.html", categoria=umaCategoria)


@categorias.route("/<int:categoria>/delete/", methods=["GET", "POST"])
def deleteCategoria(categoria):
    # verifica se há algum usuário logado, e depois se tal usuário
    # é dono desta categoria
    if "usuario_id" not in login_session:
        flash(u"Você precisa estar logado para acessar esta página.")
        return redirect(url_for("usuarios.loginUsuario"))
    umaCategoria = Categoria.query.filter_by(id=categoria).one_or_none()
    if umaCategoria is None:
        flash(u"Erro: A categoria você está tentando acessar não existe!")
        return redirect(url_for("categorias.showCategorias"))
    if login_session["usuario_id"] != umaCategoria.usuario_id:
        flash(u"Você não é o dono desta categoria.")
        return redirect(url_for(
            "categorias.showCategoria", categoria=umaCategoria.id))

    if request.method == "POST":
        itens = Item.query.filter_by(categoria_id=categoria).all()
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

        Item.query.filter_by(categoria_id=categoria).delete()
        db.session.delete(umaCategoria)
        db.session.commit()
        flash(u"A categoria foi excluída! Seus itens também foram excluídos!")
        return redirect(url_for("categorias.showCategorias"))
    else:
        return render_template("deleteCategoria.html", categoria=umaCategoria)
