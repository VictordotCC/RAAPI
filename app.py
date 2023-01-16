from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from models import db

app = Flask(__name__)
cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGODB_SETTINGS'] = {
    'db': 'ProyectosInfo',
    'host': 'localhost',
    'port': 27017
}

db.init_app(app)