"""Flask App for the API"""
# pylint: disable=no-member
import math

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from models import db, Proyecto, AeroGenerador, Receptor, Medicion
from fastkml import kml

from helpers import get_weather_info
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

@cross_origin()
@app.route('/proyectos', methods=['GET'])
def get_proyectos():
    """Get all projects"""
    proyectos = Proyecto.objects().to_json()
    return jsonify(proyectos), 200

@cross_origin()
@app.route('/proyectos', methods=['POST'])
def add_proyecto():
    """Add a project"""
    body = request.get_json()
    proyecto = Proyecto(**body).save()
    id_proyecto = proyecto.id
    return {'id': str(id_proyecto)}, 200

@cross_origin()
@app.route('/proyectos/<id_proyecto>', methods=['GET'])
def get_proyecto(id_proyecto):
    """Get a project"""
    proyecto = Proyecto.objects.get(id=id_proyecto).to_json()
    return jsonify(proyecto), 200


#Info Methods

@cross_origin()
@app.route('/leer_kml', methods=['POST']) #Cambiar a POST
def leer_kml():
    print("reading kml")
    """Read a kml file and return the coordinates"""
    body = request.get_json()
    kml_file = body['kml_file']
    
    with open(kml_file, 'r') as f:
        doc = f.read()
        k = kml.KML()
        k.from_string(doc)
        k.from_string(doc)
   
        features = list(k.features())
        puntos = []
        for feature in features:
            for group in feature.features():
                for placemark in group.features():
                    print(placemark.geometry.x, placemark.geometry.y)
                    puntos.append([placemark.geometry.x, placemark.geometry.y])
    
    return jsonify(puntos), 200

@cross_origin()
@app.route('/info', methods=['POST'])
def get_info():
    """Get the info of the project, returning each point value"""
    body = request.get_json()
    #Obtener la fecha y el id del proyecto e info del clima
    #fecha_req = body['fecha']
    proyecto = Proyecto.objects.get(id=body['id_proyecto'])
    info = get_weather_info(proyecto) #Dict fecha["wind_speed", "wind_direction"]

    #Obtener los aero_generadores y sus caracteristicas
    aero_generadores = AeroGenerador.objects(proyecto=proyecto)
    #Obtener los receptores y sus caracteristicas
    receptores = Receptor.objects(proyecto=proyecto)

    #Obtener las mediciones de los receptores
    respuesta = {}
    valores_viento = []
    for date, valor in info.items():
        fecha = date
        vel_viento = valor["wind_speed"]
        ang_viento = valor["wind_direction"]
        respuesta.update({fecha: {"velocidad": vel_viento, "angulo": ang_viento, "receptores": []}})
        if [vel_viento, ang_viento] not in valores_viento:
            valores_viento.append([vel_viento, ang_viento])

    mediciones = {}
    for receptor in receptores:
        suma_medicion = 0
        for aerogenerador in aero_generadores:
            for vel_viento, ang_viento in valores_viento:
                medicion = Medicion(vel_viento=vel_viento,
                                    ang_viento=ang_viento,
                                    AG=aerogenerador,
                                    R=receptor)
                opmedicion = 10**(medicion.NPS/10)
                suma_medicion += opmedicion
        total_medicion = 10*math.log10(suma_medicion)
        mediciones.update({receptor.id: total_medicion})

    for fecha, valor in respuesta.items():
        for receptor in receptores:
            valor["receptores"].append(
                {"id_receptor": receptor.id,
                  "totalNPS": mediciones[receptor.id]})
    return jsonify(respuesta), 200

if __name__ == '__main__':
    app.run(debug=True)
