from functools import wraps
from flask import request, jsonify
import jwt
JWT_SECRET = 'D#|VX$zph=>mtT&hK&b.Nr0G-,TA=o&a%vDEg-|(NRho:UI@L)HTSc361R)eJUd'
class Decorators(object):
    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.args.get('token')
            if not token:
                return jsonify({'message' : 'Token is invalid 1'}), 403            
            try:
                data = jwt.decode(token, JWT_SECRET)
            except:
                return jsonify({'message' : 'Token is invalid 2'}), 403
            
            return f(*args, **kwargs)
        return decorated