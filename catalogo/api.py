# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from catalogo import *
from flask_restful import reqparse, abort, Resource


def abortarSeForNulo(objeto):
    if objeto is None:
        abort(404, erro=u"Categoria/item não existente")


parser = reqparse.RequestParser()
parser.add_argument('erro')


class ListaCategorias(Resource):
    def get(self):
        categorias = Categoria.query.all()
        categoriasSerializadas = []
        # serializa cada item das categorias, e depois cria uma lista
        # de itens serializados para juntar com a categoria serializada
        # correspondente
        for c in categorias:
            itens = Item.query.filter_by(categoria_id=c.id).all()
            itensSerializados = []
            for i in itens:
                itensSerializados.append(i.serialize)
            categoriaSerializada = c.serialize
            categoriaSerializada["itens"] = itensSerializados
            categoriasSerializadas.append(categoriaSerializada)
        return {
            "categorias": categoriasSerializadas
        }


class UmaCategoria(Resource):
    def get(self, categoria):
        categoria = Categoria.query.filter_by(id=categoria).one_or_none()
        abortarSeForNulo(categoria)
        itens = Item.query.filter_by(categoria_id=categoria.id).all()
        # serializa cada item das categoria, e depois cria uma lista
        # de itens serializados para juntar com a categoria serializada
        itensSerializados = []
        for i in itens:
            itensSerializados.append(i.serialize)
        categoriaSerializada = categoria.serialize
        categoriaSerializada["itens"] = itensSerializados
        return {
            "categoria": categoriaSerializada
        }


class UmItem(Resource):
    def get(self, categoria, item):
        item = Item.query.filter_by(
            id=item, categoria_id=categoria).one_or_none()
        abortarSeForNulo(item)
        return {
            "item": item.serialize
        }


api.add_resource(ListaCategorias, "/api/v1/categorias/")
api.add_resource(UmaCategoria, "/api/v1/categorias/<int:categoria>/")
api.add_resource(UmItem, "/api/v1/categorias/<int:categoria>/<int:item>/")
