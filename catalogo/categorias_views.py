# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from catalogo import *

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
