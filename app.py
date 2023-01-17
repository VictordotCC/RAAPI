from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from models import db
from usermodels import db as userdb

app = Flask(__name__)
cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGODB_SETTINGS'] = {
    'db': 'ProyectosInfo',
    'host': 'localhost',
    'port': 27017
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
userdb.init_app(app)