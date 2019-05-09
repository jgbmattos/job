# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, make_response, abort
from flask_restplus import Resource, Api

app = Flask(__name__)
api = Api(app)

ns_pessoa_fisica = api.namespace('api/pessoa_fisica', description='API de pessoa física')

dados = {'pessoas':
            [{
            'id': 1,
            'cpf': '111.111.111-11',
            'nome': 'Wladimir',
            'data_nascimento' : '01/01/1970',
            'data_cadastro' : '15/12/2018',
            'lista_bens' : [
                            {'id':1, 'descricao':'carro'},
                            {'id':2, 'descricao':'casa'},
                            {'id':3, 'descricao':'barco'}
                           ],
            'endereco' : {
                'logradouro': '...',
                'bairro': '...'
            },
            'lista_fontes_de_renda':[
                            {'id':1, 'descricao':'CLT'},
                            {'id':2, 'descricao':'Tesouro direto'},
                            {'id':3, 'descricao':'Sistema'}
            ]
        },
        {
            'id': 2,
            'cpf': '222.222.222-22',
            'nome': 'Jason',
            'data_nascimento' : '01/01/2000',
            'data_cadastro' : '15/12/2018',
            'lista_bens' : [{'id':1, 'descricao':'moto'}],
            'endereco' : {
                'logradouro': '...',
                'bairro': '...'
            },
            'lista_fontes_de_renda':[{'id':1, 'descricao':'CLT'}]
        }
    ]
}

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
        if ('cpf' not in json_data) or ('nome' not in json_data) or ('data_nascimento' not in json_data) or ('lista_bens' not in json_data) or ('endereco' not in json_data) or ('lista_fontes_de_renda' not in json_data):
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

        if ('cpf' not in json_data) or ('nome' not in json_data) or ('data_nascimento' not in json_data) or ('lista_bens' not in json_data) or ('endereco' not in json_data) or ('lista_fontes_de_renda' not in json_data):
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


@ns_pessoa_fisica.route('/<int:id_pessoa>/fontes_de_renda')
@api.response(404, 'Pessoa não encontrada.')
class Individual(Resource):

    def get(self, id_pessoa):
        for pessoa in dados['pessoas']:
            if int(pessoa['id']) == id_pessoa:
                return jsonify(pessoa['lista_fontes_de_renda'])

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
                for bem in pessoa['lista_fontes_de_renda']:
                    if bem['id'] > max_id:
                        max_id = bem['id']

        json_data['id'] = max_id+1
        dados['pessoas'][idx]['lista_fontes_de_renda'].append(json_data)


        return None, 201

@ns_pessoa_fisica.route('/<int:id_pessoa>/fontes_de_renda/<int:id>')
@api.response(404, 'Bem não encontrad.')
class Individual(Resource):

    def get(self, id_pessoa, id):
        for pessoa in dados['pessoas']:
            if int(pessoa['id']) == id_pessoa:
                for bem in pessoa['lista_fontes_de_renda']:
                    if bem['id'] == id:
                        return jsonify(bem)
        return None, 404

    def delete(self, id_pessoa, id):
        for i, pessoa in enumerate(dados['pessoas']):
            if int(pessoa['id']) == id_pessoa:
                for j, bem in enumerate(pessoa['lista_fontes_de_renda']):
                    if bem['id'] == id:
                        del dados['pessoas'][i]['lista_fontes_de_renda'][j]
                        return 200
        return None, 404

@ns_pessoa_fisica.route('/<int:id_pessoa>/bens')
@api.response(404, 'Pessoa não encontrada.')
class Individual(Resource):

    def get(self, id_pessoa):
        for pessoa in dados['pessoas']:
            if int(pessoa['id']) == id_pessoa:
                return jsonify(pessoa['lista_bens'])

        return None, 404
    
    def post(self, id_pessoa):
        """Cadastra um novo bem."""
        json_data = request.get_json(force=True)

        if ('descricao' not in json_data):
            abort(400, 'Informe a descrição desse bem')
        max_id = 0
        idx = 0
        for i, pessoa in enumerate(dados['pessoas']):
            if pessoa['id'] == id_pessoa:
                idx = i
                for bem in pessoa['lista_bens']:
                    if bem['id'] > max_id:
                        max_id = bem['id']

        json_data['id'] = max_id+1
        dados['pessoas'][idx]['lista_bens'].append(json_data)

        return None, 201

@ns_pessoa_fisica.route('/<int:id_pessoa>/bens/<int:id>')
@api.response(404, 'Bem não encontrad.')
class Individual(Resource):

    def get(self, id_pessoa, id):
        for pessoa in dados['pessoas']:
            if int(pessoa['id']) == id_pessoa:
                for bem in pessoa['lista_bens']:
                    if bem['id'] == id:
                        return jsonify(bem)
        return None, 404

    def delete(self, id_pessoa, id):
        for i, pessoa in enumerate(dados['pessoas']):
            if int(pessoa['id']) == id_pessoa:
                for j, bem in enumerate(pessoa['lista_bens']):
                    if bem['id'] == id:
                        del dados['pessoas'][i]['lista_bens'][j]
                        return 200
        return None, 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
