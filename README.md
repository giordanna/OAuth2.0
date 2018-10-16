# Catálogo
Quarto projeto do curso nanodegree da Udacity de Desenvolvedor Full-stack.
Este projeto é um pequeno servidor em python, utilizando o framework Flask e SQLAlchemy, que hospeda um serviço de registro de catálogo, onde o usuário deve logar com uma conta Google+ para adicionar categorias e itens. Há também alguns endpoints de API.

### Importante
Este projeto utiliza ID de cliente OAuth 2.0 do Google, o qual está em um arquivo nomeado para o projeto `segredos_cliente.json`, porém não está à mostra neste repositório por questões de segurança. Para obter um ID de cliente acesse a aba Credenciais em https://console.developers.google.com/apis/.

Na hora de criar o ID, dentro de Restrições:
- Insira na seção de Origens JavaScript autorizadas o endereço http://localhost:5000;
- Insira na seção de URIs de redirecionamento autorizados os endereços http://localhost:5000 e http://localhost:5000/login.

## Definindo variáveis de ambiente
- Bash (Linux, Mac, etc): `export FLASK_APP=catalogo`
- Windows CMD: `set FLASK_APP=catalogo`
- Windows PowerShell: `$env:FLASK_APP = "catalogo"`


## Como instalar
- Baixe ou clone este repositório usando `git clone https://github.com/giordanna/projeto-catalogo.git`;
- Dentro do diretório, instale as dependências usando `pip install -r requirements.txt`;
- Agora instale a aplicação com `pip install -e .`;
- Caso deseje, popule o webserver executando `python popular_db.py` para gerar vários itens e categorias mockup. Você pode modificar o email do usuário neste arquivo para o seu equivalente, podendo assim editar excluir itens e categorias.

## Como executar o webserver
- Execute `flask run`. Depois, você poderá acessar localmente o site em http://localhost:5000

## TODOs
- Utilizar blueprints
- Utilizar errorhandler
- Utilizar o SQL-Alchemy

## Dúvidas
 - Caso há alguma dúvida em relação a este repositório, envie para gior.grs@gmail.com

## Licença
[MIT](LICENSE)