import requests
from flask import Flask, jsonify, request, make_response
from decorator import Decorators
import os

app = Flask(__name__)

dados = {
    'cpf': '111.111.111-11',
    'idade' : 22,
    'lista_bens' : ['Carro', 'casa', 'barco'],
    'endereco' : {
        'logradouro': '...',
        'bairo': '...'
    },
    'fontes_de_renda':['clt', 'acoes', 'titulos_tesouro']
}

@app.route('/', methods=['GET']) 
def home():
    return jsonify('sistema rodando')

@app.route('/v1/system2', methods=['GET']) 
@Decorators.token_required
def system2():
    return jsonify(dados)

if __name__ == "__main__":
    app.run(debug=False, port=5002)
