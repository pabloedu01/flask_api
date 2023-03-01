from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import ftplib
import os
from datetime import datetime
import time
from io import BytesIO
from flask_paginate import Pagination, get_page_args
# ler variaveis de ambiente
from dotenv import load_dotenv

load_dotenv()

mongo_username = os.getenv('MONGO_USERNAME')
mongo_password = os.getenv('MONGO_PASSWORD')
mongo_cluster = os.getenv('MONGO_CLUSTER')
mongo_db = os.getenv('MONGO_DB')

app = Flask(__name__)
app.config['MONGO_URI'] = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_CLUSTER')}/{os.getenv('MONGO_DB')}?retryWrites=true&w=majority"
mongo = PyMongo(app)
ftp = ftplib.FTP(os.getenv('FTP_URL'))
ftp.login(user=os.getenv('FTP_USERNAME'), passwd=os.getenv('FTP_PASSWORD'))


def check_out_dir(date):
    dir = '/public_html'
    filename = date.strftime('%Y/%m/%d')
    dir_ano = dir + '/' + filename.split('/')[0]
    dir_mes = dir_ano + '/' + filename.split('/')[1]
    dir_dia = dir_mes + '/' + filename.split('/')[2]
    try:
        ftp.cwd(dir_ano)
    except ftplib.error_perm:
        ftp.mkd(dir_ano)
        ftp.cwd(dir_ano)
    try:
        ftp.cwd(dir_mes)
    except ftplib.error_perm:
        ftp.mkd(dir_mes)
        ftp.cwd(dir_mes)
    try:
        ftp.cwd(dir_dia)
    except ftplib.error_perm:
        ftp.mkd(dir_dia)
        ftp.cwd(dir_dia)
    return (dir_dia)

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('file')
    tags = request.form['tags']
    file_paths = []
    today = datetime.now()
    directory = check_out_dir(today)
    print(directory)
    for file in files:
        filename = file.filename
        file_path = f"{directory}/{filename}"
        file = file.read()
        with BytesIO(file) as f:
            ftp.storbinary(f'STOR {directory}/{filename}', f)
        mongo.db.files.insert_one({'file_path': file_path, 'tags': tags})
        file_paths.append(file_path)
    return jsonify({'file_paths': file_paths})


@app.route('/list_files', methods=['GET'])
def list_files():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    files = []
    cursor = mongo.db.files.find()
    total = mongo.db.files.estimated_document_count()
    pagination = cursor.skip((page - 1) * per_page).limit(per_page)

    for file in pagination:
        files.append({'file_path': file['file_path'], 'tags': file['tags']})

    return jsonify({'files': files, 'total': total, 'current_page': page, 'per_page': per_page})


@app.route('/', methods=['GET'])
def home():
    return jsonify({'Message': 'Olá mundo'})
# if __name__ == '__main__':
#     app.run()
