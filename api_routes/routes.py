import requests

base_url = "https://api.thecatapi.com/v1"
api_url = "http://10.135.232.38:5001"



def get_funcionario():
    url = f"{api_url}/funcionarios"

    resposta = requests.get(url)

    return resposta.json()[0]


def post_cadastro():
    url = f"{api_url}/cadastro_funcionario"
    dados = {
        "email": "gabriel@email.com",
        "senha": "batata"
    }
    resposta = requests.post(url, json=dados)
    return resposta.json()[0]