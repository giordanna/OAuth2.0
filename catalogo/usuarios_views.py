# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from catalogo import *


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


def getUsuarioId(email):
    session = DBSession()
    usuario = session.query(
        Usuario).filter_by(email=email).one_or_none()
    session.close()
    if usuario is None:
        return None
    else:
        return usuario.id