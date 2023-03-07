from datetime import timedelta
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=0.5)
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username != 'usuario' or password != 'senha':
        return jsonify({'message': 'Usuário ou senha inválidos'}), 401

    access_token = create_access_token(identity=username, additional_claims={'key': 'value'}, expires_delta=app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    refresh_token = create_refresh_token(identity=username)

    return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    refresh_token = create_refresh_token(identity=current_user)
    return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Olá, {current_user}!'}), 200

@app.route('/test', methods=['GET'])
def test():
    
    return jsonify({'message': f'Olá, você acessou'}), 200

if __name__ == '__main__':
    app.run()