from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from models import db, Proyecto, AeroGenerador, Receptor, Medicion
from helpers import getWeatherInfo
import math
import config

app = Flask(__name__)
cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGODB_SETTINGS'] = {
    'host': config.DBURL,
    'alias': 'default'
}

db.init_app(app)


#Database Methods

#get schema from mongo
@cross_origin()
@app.route('/schema', methods=['GET'])
def get_schema():
    schema = db.get_db().list_collection_names()
    return jsonify(schema), 200

@cross_origin()
@app.route('/proyectos', methods=['GET'])
def get_proyectos():
    proyectos = Proyecto.objects().to_json()
    return jsonify(proyectos), 200

@cross_origin()
@app.route('/proyectos', methods=['POST'])
def add_proyecto():
    body = request.get_json()
    proyecto = Proyecto(**body).save()
    id = proyecto.id
    return {'id': str(id)}, 200

@cross_origin()
@app.route('/proyectos/<id>', methods=['GET'])
def get_proyecto(id):
    proyecto = Proyecto.objects.get(id=id).to_json()
    return jsonify(proyecto), 200


#Info Methods

@cross_origin()
@app.route('/info', methods=['POST'])
def get_info():
    body = request.get_json()
    #Obtener la fecha y el id del proyecto e info del clima
    fechaReq = body['fecha']
    proyecto = Proyecto.objects.get(id=body['id_proyecto'])
    info = getWeatherInfo(fechaReq, proyecto) #Dict fecha["wind_speed", "wind_direction"]

    #Obtener los aeroGeneradores y sus caracteristicas
    aeroGeneradores = AeroGenerador.objects(proyecto=proyecto)
    #Obtener los receptores y sus caracteristicas
    receptores = Receptor.objects(proyecto=proyecto)

    #Obtener las mediciones de los receptores
    respuesta = {}
    valoresViento = []
    for fecha in info:
        velViento = info[fecha]["wind_speed"]
        angViento = info[fecha]["wind_direction"]
        respuesta.update({fecha: {"velocidad": velViento, "angulo": angViento, "receptores": []}})
        if [velViento, angViento] not in valoresViento:
            valoresViento.append([velViento, angViento])

    mediciones = {}
    for receptor in receptores:
        sumaMedicion = 0
        for aeroGenerador in aeroGeneradores:
            for velViento, angViento in valoresViento:
                medicion = Medicion(velViento=velViento, angViento=angViento, AG=aeroGenerador, R=receptor)
                opmedicion = 10**(medicion.NPS/10)
                sumaMedicion += opmedicion
        totalMedicion = 10*math.log10(sumaMedicion)
        mediciones.update({receptor.id: totalMedicion})

    for fecha in respuesta:
        for receptor in receptores:
            respuesta[fecha]["receptores"].append({"id_receptor": receptor.id, "totalNPS": mediciones[receptor.id]})
    return jsonify(respuesta), 200
    

if __name__ == '__main__':
    app.run(debug=True)
