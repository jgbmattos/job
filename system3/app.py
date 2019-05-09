# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, make_response, abort
from flask_restplus import Resource, Api
import datetime


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app = Flask(__name__)
api = Api(app)
ns_pessoa_fisica = api.namespace('api/pessoa_fisica', description='API de pessoa física')
ns_bureau        = api.namespace('api/bureau', description="API de bureau de crédito")

dados = {'pessoas':[{
        'id':1,
        'cpf': '111.111.111-11',
        'nome': 'Wladimir',
        'data_nascimento' : '01/01/1970',
        'data_cadastro' : '15/12/2018',
        'bureau_id' : 1,
        'endereco' : {
                'logradouro': '...',
                'bairro': '...'
            },
        'lista_mov_fin' : [
            {   'id': 1,
                'data' : datetime.datetime.utcnow(),
                'cnpj_vendedor' : '11.111.111/0001-11',
                'valor': 100
            },
            {   'id': 2,
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
]}

dados_bureau = {"bureau":[{'id':1, 'decricao': 'bureau 1', 'cnpj':'111.111.111/0001-11'}]}

@ns_bureau.route('/')
class IndividualCollection(Resource):
    def get(self):
        """Retorna a lista de pessoas."""
        return jsonify(dados)

@ns_pessoa_fisica.route('/')
class IndividualCollection(Resource):
    @ns_pessoa_fisica.param('cpf', 'Filtra registro pelo CPF')
    @ns_pessoa_fisica.param('data_cadastro', 'Filtra registros pela data de cadastro')
    @ns_pessoa_fisica.param('data_nascimento', 'Filtra registros pela data de nascimento')
    def get(self):
        """Retorna a lista de pessoas."""
        if "cpf" in request.args:
            for pessoa in dados['pessoas']:
                if pessoa['cpf'] == request.args.get('cpf'):
                    return jsonify(pessoa)
            return None, 404

        if 'data_cadastro' in request.args:
            dados_filtrados =  {'pessoas': []}
         
            for pessoa in dados['pessoas']:
                if pessoa['data_cadastro'] == request.args.get('data_cadastro'):
                    dados_filtrados['pessoas'].append(pessoa)
         
            if dados_filtrados['pessoas'].count == 0:
                    dados_filtrados['pessoas'].append({})
         
            return jsonify(dados_filtrados)

        if 'data_nascimento' in request.args:
            dados_filtrados =  {'pessoas': []}
            for pessoa in dados['pessoas']:
            
                if pessoa['data_nascimento'] == request.args.get('data_nascimento'):
                    dados_filtrados['pessoas'].append(pessoa)
            
            if dados_filtrados['pessoas'].count == 0:
                    dados_filtrados['pessoas'].append({})
            
            return jsonify(dados_filtrados)

        return jsonify(dados)

    @api.response(201, 'Pessoa física cadastrada com sucesso.')
    def post(self):
        """Cadastra uma nova pessoa fisica."""
        json_data = request.get_json(force=True)
        print(json_data)
        if ('cpf' not in json_data) or ('nome' not in json_data) or ('data_nascimento' not in json_data) or ('lista_bens' not in json_data) or ('endereco' not in json_data) or ('lista_mov_fin' not in json_data):
            abort(400, 'Informe todos os dados para incluir um cliente')
        max_id = 0

        for pessoa in dados['pessoas']:
            if pessoa['cpf'] == json_data['cpf']:
                abort(409, 'cpf já cadastrado utilize put para atualizar os dados')

            if pessoa['id'] > max_id:
                max_id = pessoa['id']

        json_data['id'] = max_id+1

        dados['pessoas'].append(json_data)

        return None, 201

@ns_pessoa_fisica.route('/<int:id>')
@api.response(404, 'Pessoa não encontrada.')
class Individual(Resource):

    def get(self, id):
        for pessoa in dados['pessoas']:
            if int(pessoa['id']) == id:
                return jsonify(pessoa)

        return None, 404

    @api.response(204, 'Pessoa física atualizada com sucesso.')
    def put(self, id):
        """Atualiza pessoa física."""
        json_data = request.get_json(force=True)

        if ('cpf' not in json_data) or ('nome' not in json_data) or ('data_nascimento' not in json_data) or ('lista_bens' not in json_data) or ('endereco' not in json_data) or ('lista_mov_fin' not in json_data):
            abort(400, 'Informe todos os dados para incluir um cliente')

        for i, pessoa in enumerate(dados['pessoas']):
            if int(pessoa['id']) == id:
                dados['pessoas'][i].update(json_data)
                return jsonify('{} atualizado com sucesso'.format(pessoa['nome']))

        return None, 404

    @api.response(204, 'Pessoa física deletada com sucesso.')
    def delete(self, id):
        """Deleta pessoa física."""
        for i, pessoa in enumerate(dados['pessoas']):
            if int(pessoa['id']) == id:
                del dados['pessoas'][i]
                return jsonify('id {} deletado com sucesso'.format(id))

        return None, 204

@ns_pessoa_fisica.route('/<int:id_pessoa>/endereco')
@api.response(404, 'Pessoa não encontrada.')
class Individual(Resource):

    def get(self, id_pessoa):
        for pessoa in dados['pessoas']:
            if int(pessoa['id']) == id_pessoa:
                return jsonify(pessoa['endereco'])

        return None, 404

    @api.response(204, 'Endereço atualizado com sucesso.')
    def put(self, id_pessoa):
        """Atualiza endereço."""
        json_data = request.get_json(force=True)

        if ('bairro' not in json_data) or ('logradouro' not in json_data):
            abort(400, 'Informe todos os dados para atualizar um cliente')

        for i, pessoa in enumerate(dados['pessoas']):
            if int(pessoa['id']) == id_pessoa:
                dados['pessoas'][i]['endereco'].update(json_data)
                return jsonify('{} atualizado com sucesso'.format(pessoa['nome']))

        return None, 404

@ns_pessoa_fisica.route('/<int:id_pessoa>/movimentacoes')
@api.response(404, 'Pessoa não encontrada.')
class Individual(Resource):

    def get(self, id_pessoa):
        for pessoa in dados['pessoas']:
            if int(pessoa['id']) == id_pessoa:
                return jsonify(pessoa['lista_mov_fin'])

        return None, 404

    @api.response(204, 'fonte de rende adicionada com sucesso.')
    def post(self, id_pessoa):
        """Cadastra uma nova fonte de renda."""
        json_data = request.get_json(force=True)

        if ('descricao' not in json_data):
            abort(400, 'Informe a descrição desse bem')
        max_id = 0
        idx = 0
        for i, pessoa in enumerate(dados['pessoas']):
            if pessoa['id'] == id_pessoa:
                idx = i
                for bem in pessoa['lista_mov_fin']:
                    if bem['id'] > max_id:
                        max_id = bem['id']

        json_data['id'] = max_id+1
        dados['pessoas'][idx]['lista_mov_fin'].append(json_data)


        return None, 201

@ns_pessoa_fisica.route('/<int:id_pessoa>/movimentacoes/<int:id>')
@api.response(404, 'Bem não encontrad.')
class Individual(Resource):

    def get(self, id_pessoa, id):
        for pessoa in dados['pessoas']:
            if int(pessoa['id']) == id_pessoa:
                for bem in pessoa['lista_mov_fin']:
                    if bem['id'] == id:
                        return jsonify(bem)
        return None, 404

    def delete(self, id_pessoa, id):
        for i, pessoa in enumerate(dados['pessoas']):
            if int(pessoa['id']) == id_pessoa:
                for j, bem in enumerate(pessoa['lista_mov_fin']):
                    if bem['id'] == id:
                        del dados['pessoas'][i]['lista_mov_fin'][j]
                        return 200
        return None, 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)