import requests
from flask import Flask, jsonify, request, make_response
from decorator import Decorators

app = Flask(__name__)

dados = {
    'cpf': '111.111.111-11',
    'nome' : 'Joao',
    'endereco' : {
        'logradouro': '...',
        'bairo': '...'
    },
    'lista_de_dividas' : ['ITAU', 'BTG', 'CARROS CAROS S/A']
}

@app.route('/', methods=['GET']) 
def home():
    return jsonify('sistema rodando')


@app.route('/v1/system1', methods=['GET']) 
@Decorators.token_required
def system1():
    return jsonify(dados)

if __name__ == "__main__":
    app.run(debug=True, port=5001)