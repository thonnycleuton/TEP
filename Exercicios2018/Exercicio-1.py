"""
Algumas operacoess com a API do The Movie DB
"""

import requests

key = 'b32b779c125895827fa2c043dc223686'
session_id = 'dff18b30f18c789e8c964f5b75feade151159dfe'

user_id = '6429486'

# dominio da api
domain = 'https://api.themoviedb.org'


def list_movies():
    """ Mostra a lista de filmes criada por um usuario. """
    # url a ser montada para acessar o servico a ser requisitado
    url = domain + "/3/account/" + user_id + "/lists?page=1&session_id=" + session_id + "&language=en-US&api_key=" + key
    response = requests.get(url).json()

    return response


def add_movie_to_list(list_id, movie_id):
    """ Adiciona um titulo a uma lista de filmes de um usuario"""
    # url a ser montada para acessar o servico a ser requisitado
    url = domain + "/3/list/" + list_id + "/add_item?session_id=" + session_id + "&api_key=" + key
    # item a ser adicionado ao metodo post
    payload = "{\"media_id\":%s}" % movie_id

    headers = {'content-type': 'application/json;charset=utf-8'}
    response = requests.post(url, data=payload, headers=headers)

    return response


# mostra o resustado da funcao na Tela
print(add_movie_to_list('64614', '671'))

# chama o resultado da funcao List_movies na tela
print(list_movies())
