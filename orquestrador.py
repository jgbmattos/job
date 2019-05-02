import os
from subprocess import Popen
from flask import Flask, jsonify, request, make_response, render_template, url_for
import requests
import random
import time
import json
from celery import Celery

app = Flask(__name__)
os.environ['FORKED_BY_MULTIPROCESSING'] = "1"

def make_celery(app):
    celery = Celery('orquestrador',#app.import_name,
                broker='sqla+sqlite:///' + os.path.join(os.path.dirname(os.path.realpath(__file__)), 'celery.db'),
                backend='db+sqlite:///' + os.path.join(os.path.dirname(os.path.realpath(__file__)), 'celery_results.db'))
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    return celery

celery = make_celery(app)
app.app_context().push() 

def retorna_dados_base_a():
    r = requests.get('http://127.0.0.1:5001/v1/system1')
    if r.status_code == 403:
        print('token invalido, solicitando token e refazendo requisição')
        r_token = requests.post('http://127.0.0.1:5004/v1/login') 
        if r_token.status_code == 200:
            r = requests.get('http://127.0.0.1:5001/v1/system1', params='token={}'.format(r_token.json()["token"]))
            return jsonify(r.json())
        else:
            print('erro geral')
    return jsonify({})

def retorna_dados_base_b():
    r = requests.get('http://127.0.0.1:5002/v1/system2')
    if r.status_code == 403:
        print('token invalido, solicitando token e refazendo requisição')
        r_token = requests.post('http://127.0.0.1:5004/v1/login') 
        if r_token.status_code == 200:
            r = requests.get('http://127.0.0.1:5002/v1/system2', params='token={}'.format(r_token.json()["token"]))
            return jsonify(r.json())
        else:
            print('erro geral')
    return jsonify({})

def retorna_dados_base_c():
    r = requests.get('http://127.0.0.1:5003/v1/system3')
    if r.status_code == 200:
         return jsonify(r.json())

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/baseA')
def request_baseA():
    return retorna_dados_base_a()

@app.route('/baseB')
def request_baseB():
    return retorna_dados_base_b()

@app.route('/baseC')
def request_baseC():
    return retorna_dados_base_c()


@celery.task(bind=True)
def calcula_score(self):
    num_etapas = 3
    for i in range(num_etapas):
        cpf = '' 
        if i == 0:
            message = 'Consultando microserviço a'
            dados = retorna_dados_base_a()
        elif i == 1:
            message = 'Consultando microserviço b'
            dados = retorna_dados_base_b()
        elif i == 2:
            message = 'Consultando microserviço c'
            dados = retorna_dados_base_c()
        self.update_state(state='PROGRESS',
                          meta={'etapa': i,
                                'payload': json.dumps(dados.data.decode('UTF-8')),
                                'etapas': num_etapas,
                                'status': message})
        time.sleep(2)
    
    return {'etapa': num_etapas, 'etapas': num_etapas, 'status': 'Calculo finalizado!', 'payload' : '', 'result': 77}

@app.route('/consulta_score', methods=['POST'])
def consulta_score():
    task = calcula_score.apply_async()
    return jsonify({}), 202, {'Location': url_for('status_calculo_score',
                                                  task_id=task.id)}

@app.route('/status/<task_id>')
def status_calculo_score(task_id):
    task = calcula_score.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'etapa': 0,
            'etapas': 1,
            'payload': '',
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'etapa': task.info.get('etapa', 0),
            'etapas': task.info.get('etapas', 1),
            'payload': task.info.get('payload', ''),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'etapa': 1,
            'etapas': 1,
            'payload': '',
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

if __name__ == "__main__":
    p1 = Popen("python system1.py") 
    p2 = Popen("python system2.py") 
    p3 = Popen("python system3.py") 
    p4 = Popen("python auth.py")
    app.run(debug=False, port=5005)