from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from models import db, Proyecto, AeroGenerador, Receptor, User, User_Proyecto

app = Flask(__name__)
cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGODB_SETTINGS'] = {
    'db': 'ProyectosInfo',
    'host': 'localhost',
    'port': 27017
}

db.init_app(app)

@cross_origin()
@app.route('/proyectos', methods=['GET'])
def get_proyectos():
    proyectos = Proyecto.objects().to_json()
    return proyectos

@cross_origin()
@app.route('/proyectos', methods=['POST'])
def add_proyecto():
    body = request.get_json()
    proyecto = Proyecto(**body).save()
    id = proyecto.id
    return {'id': str(id)}, 200
