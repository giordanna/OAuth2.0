# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from catalogo import *


@app.errorhandler(404)
def viewErroNotFound(error):
    titulo = "404 Not Found"
    corpo = u"Poxa, acho que ce errou esse URL, né. :/"
    return render_template("showErro.html", titulo=titulo, corpo=corpo), 404


@app.errorhandler(403)
def viewErroForbidden(error):
    titulo = "403 Forbidden"
    corpo = u'''Seu navegador está tentando acessar algum
    recurso que não lhe é permitido.'''
    return render_template("showErro.html", titulo=titulo, corpo=corpo), 403


@app.errorhandler(410)
def viewErroGone(error):
    titulo = "410 Gone"
    corpo = u"O recurso que você está tentando acessar não existe. sry :/"
    return render_template("showErro.html", titulo=titulo, corpo=corpo), 410


@app.errorhandler(500)
def viewErroInternalServerError(error):
    titulo = "500 Internal Server Error"
    corpo = u'''O servidor está falhando... de novo...
    deve ser algum erro de programação ou está sobrecarregado. rip'''
    return render_template("showErro.html", titulo=titulo, corpo=corpo), 500
