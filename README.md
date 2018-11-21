# Catálogo
Quarto projeto do curso nanodegree da Udacity de Desenvolvedor Full-stack.
Este projeto é um pequeno servidor em python, utilizando o framework Flask, que hospeda um serviço de registro de catálogo, onde o usuário deve logar com uma conta Google+ para adicionar categorias e itens. Há também alguns endpoints de API.

### Importante
Esta versão foi modificada para que seu deploy seja feito em um [servidor linux](https://github.com/giordanna/projeto-deploy-linux), ligado ao sexto projeto do curso.

## Como instalar
- Baixe ou clone este repositório usando `sudo git clone https://github.com/giordanna/projeto-catalogo.git`;
- Dentro do diretório, instale as dependências usando `sudo pip3 install -r requirements.txt`;
- Agora instale a aplicação com `sudo pip3 install -e .`;
- Caso deseje, popule o webserver executando `sudo python3 popular_db.py` para gerar vários itens e categorias mockup. Você pode modificar o email do usuário neste arquivo para o seu equivalente, podendo assim editar excluir itens e categorias.

## Definindo variáveis de ambiente
Para que o flask possa rodar com o comando `flask run` é necessário definir as variáveis de ambiente com o nome desta aplicação:
- Bash (Linux, Mac, etc): `export FLASK_APP=catalogo`

## Dúvidas
 - Caso há alguma dúvida em relação a este repositório, envie para gior.grs@gmail.com

## Licença
[MIT](LICENSE)
