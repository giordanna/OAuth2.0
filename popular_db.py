# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from configuracao_db import Base, Usuario, Categoria, Item, engine
from sqlalchemy.orm import sessionmaker

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

session.add(
    Usuario(
        nome="Giordanna De Gregoriis",
        email="gior.grs@gmail.com",
        imagem=""))

session.flush()

session.add(
    Categoria(
        nome=u"Natação",
        usuario_id=1))

session.add(
    Categoria(
        nome="Futebol",
        usuario_id=1))

session.add(
    Categoria(
        nome="Ciclismo",
        usuario_id=1))

session.flush()

session.add(
    Item(
        nome="Lorem ipsum 1",
        descricao='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Phasellus tortor tortor, laoreet vel pharetra ac, pharetra sit amet
        urna. Aliquam maximus dolor nunc, at egestas nibh egestas a.
        Suspendisse potenti.''',
        imagem="item_sem_imagem.png",
        categoria_id=1,
        usuario_id=1))

session.add(
    Item(
        nome="Lorem ipsum 2",
        descricao='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Phasellus tortor tortor, laoreet vel pharetra ac, pharetra sit amet
        urna. Aliquam maximus dolor nunc, at egestas nibh egestas a.
        Suspendisse potenti.''',
        imagem="item_sem_imagem.png",
        categoria_id=1,
        usuario_id=1))

session.add(
    Item(
        nome="Lorem ipsum 3",
        descricao='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Phasellus tortor tortor, laoreet vel pharetra ac, pharetra sit amet
        urna. Aliquam maximus dolor nunc, at egestas nibh egestas a.
        Suspendisse potenti.''',
        imagem="item_sem_imagem.png",
        categoria_id=1,
        usuario_id=1))

session.add(
    Item(
        nome="Lorem ipsum 4",
        descricao='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Phasellus tortor tortor, laoreet vel pharetra ac, pharetra sit amet
        urna. Aliquam maximus dolor nunc, at egestas nibh egestas a.
        Suspendisse potenti.''',
        imagem="item_sem_imagem.png",
        categoria_id=1,
        usuario_id=1))

session.add(
    Item(
        nome="Lorem ipsum 5",
        descricao='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Phasellus tortor tortor, laoreet vel pharetra ac, pharetra sit amet
        urna. Aliquam maximus dolor nunc, at egestas nibh egestas a.
        Suspendisse potenti.''',
        imagem="item_sem_imagem.png",
        categoria_id=1,
        usuario_id=1))

session.add(
    Item(
        nome="Lorem ipsum 6",
        descricao='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Phasellus tortor tortor, laoreet vel pharetra ac, pharetra sit amet
        urna. Aliquam maximus dolor nunc, at egestas nibh egestas a.
        Suspendisse potenti.''',
        imagem="item_sem_imagem.png",
        categoria_id=2,
        usuario_id=1))

session.add(
    Item(
        nome="Lorem ipsum 7",
        descricao='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Phasellus tortor tortor, laoreet vel pharetra ac, pharetra sit amet
        urna. Aliquam maximus dolor nunc, at egestas nibh egestas a.
        Suspendisse potenti.''',
        imagem="item_sem_imagem.png",
        categoria_id=2,
        usuario_id=1))

session.add(
    Item(
        nome="Lorem ipsum 8",
        descricao='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Phasellus tortor tortor, laoreet vel pharetra ac, pharetra sit amet
        urna. Aliquam maximus dolor nunc, at egestas nibh egestas a.
        Suspendisse potenti.''',
        imagem="item_sem_imagem.png",
        categoria_id=3,
        usuario_id=1))

session.commit()
