import requests
from flask import Flask, jsonify, request, make_response
import jwt
import time
import datetime
import json
import uuid
import decorator


app = Flask(__name__)
JWT_SECRET = 'D#|VX$zph=>mtT&hK&b.Nr0G-,TA=o&a%vDEg-|(NRho:UI@L)HTSc361R)eJUd'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

@app.route('/v1/login', methods=['POST']) 
def login():
    error = None
    
    #if not request.is_json:
    #    return(400)

    #content = request.get_json()

    #if 'user' not in content or 'password' not in content:
    #    return(400)

    #Nesse ponto seria feita a validação do usuário e passadas as permissões que se desejam propagar pelo micro serviço.

    payload = {
        'user_id': 1,#content['user'],
        'jti': str(uuid.uuid4()),
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        'permissoes': ['log_access', 'storage_manager']
    }
    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return jsonify({'token': jwt_token.decode('utf-8')})

if __name__ == "__main__":
    app.run(debug=False, port=5004)