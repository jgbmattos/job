import requests
from flask import Flask, jsonify, request, make_response
from decorator import Decorators
import datetime

app = Flask(__name__)

dados = {
    'cpf': '111.111.111-11',
    'bureau_id' : 1,
    'mov_fin' : [
        {
            'data' : datetime.datetime.utcnow(),
            'cnpj_vendedor' : '11.111.111/0001-11',
            'valor': 100
        },
        {
            'data' : datetime.datetime.utcnow(),
            'cnpj_vendedor' : '11.111.111/0002-11',
            'valor': 1000
        }
    ],
    'dados_ultima_compra'   :   {
        'numero_cartao' : '1111 1111 1111 1111',
        'data' : datetime.datetime.utcnow(),
        'cnpj_vendedor': '111.111.111/0001-88'
    }
}

@app.route('/', methods=['GET']) 
def home():
    return jsonify('sistema rodando')

@app.route('/v1/system3', methods=['GET']) 
def system3():
    return jsonify(dados)

if __name__ == "__main__":
    app.run(debug=False, port=5003)