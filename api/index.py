from datetime import timedelta
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
# from passlib.hash import pbkdf2_sha256

load_dotenv()
app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

app.config['JWT_SECRET_KEY'] = 'sua_chave_secreta'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)
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

@app.route('/beneficiarios')
# @jwt_required()
def listar_beneficiarios():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, name, cnpj, cpf, updated_at, created_at, cargo_id, empresa_id, owner_id FROM cadastros_beneficiario LIMIT %s OFFSET %s', (per_page, (page - 1) * per_page))
    beneficiarios_consultados = cursor.fetchall()
    beneficiarios = []
    for i in beneficiarios_consultados:
        beneficiarios.append({
            'id': i[0],
            'name': i[1],
            'cnpj': i[2],
            'cpf': i[3],
            'updated_at': i[4],
            'created_at': i[5],
            'cargo_id': i[6],
            'empresa_id': i[7],
            'owner_id': i[8]
        })
    total_items = cursor.execute("SELECT COUNT(id) FROM cadastros_beneficiario;")
    total_items = cursor.fetchone()[0]
    print(total_items)
    total_pages = (total_items // per_page) + (1 if total_items % per_page > 0 else 0)
    if page > total_pages:
        return jsonify({'message': 'Página não encontrada'}), 404
    return jsonify({
        'total_pages': total_pages,
        'total_items': total_items,
        'page': page,
        'clientes': beneficiarios
        
    })


@app.route('/test', methods=['GET'])
def test():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM auth_user where id = 1")
    user = cur.fetchone()
    username = "pablo.celestino"
    password = "Gmitsu2103Ssj"
    return jsonify(user[1]),200

if __name__ == '__main__':
    app.run()