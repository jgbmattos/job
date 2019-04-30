from flask import Flask, jsonify, request, make_response
import jwt
import time
import datetime
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asd09123ads'

def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is invalid'}), 403            

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid'}), 403
        
        return f(*args, **kwargs)
    return decorated

@app.route('/unprotected')
def unprotected():
    return ''

@app.route('/protected')
@token_required
def protected():
    return ''

@app.route('/login')
def login():
    auth = request.authorization
    if auth and auth.password == 'password':
        token = jwt.encode({'user': auth.username, 'exp' : time.mktime((datetime.datetime.utcnow() + datetime.timedelta(minutes=30)).timetuple())},app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Could verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})


if __name__ == "__main__":
    app.run(debug=True)