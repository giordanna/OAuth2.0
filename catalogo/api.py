from catalogo import *


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