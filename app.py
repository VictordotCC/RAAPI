"""Flask App for the API"""
# pylint: disable=no-member
import math
import os
import utm

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from models import db, Proyecto, AeroGenerador, Receptor, Medicion

from helpers import get_weather_info, leer_kml, get_time
import config

app = Flask(__name__)
cors = CORS(app)
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
    body = request.values

    files = request.files.to_dict()

    proyecto = Proyecto(**body)
    #proyecto.nombre = body['nombreProyecto']
    #proyecto.descripcion = body['descripcionProyecto'] 
    proyecto.save()

    if len(files) == 0:
        return jsonify({'proyecto': proyecto , 'AGlist': [], 'RXlist': []}), 200
    
    AGfile = files['AGkml']
    AGfile.save('temps/' + AGfile.filename)
    RXfile = files['RXkml']
    RXfile.save('temps/' + RXfile.filename)

    AGlist = leer_kml('temps/' + AGfile.filename)
    RXlist = leer_kml('temps/' + RXfile.filename)

    #remove files

    os.remove('temps/' + AGfile.filename)
    os.remove('temps/' + RXfile.filename)

    return jsonify({'proyecto': proyecto, 'AGlist': AGlist, 'RXlist': RXlist}), 200

@cross_origin()
@app.route('/proyectos/<id_proyecto>', methods=['GET']) #Cambiar a PUT
def delete_proyecto(id_proyecto):
    """Delete a project by object id"""
    proyecto = Proyecto.objects.get(id=id_proyecto).delete()
    return 'deleted', 200

@cross_origin()
@app.route('/proyectos/<id_proyecto>', methods=['GET'])
def get_proyecto(id_proyecto):
    """Get a project"""
    proyecto = Proyecto.objects.get(id=id_proyecto).to_json()
    return jsonify(proyecto), 200

@cross_origin()
@app.route('/ag', methods=['POST'])
def add_ag():
    """Add an aero generator"""
    body = request.values
    utm_coord = utm.from_latlon(float(body['latitud']), float(body['longitud'])) #(easting, northing, zone_number, zone_letter)
    aero_gen = AeroGenerador(nombre=body['nombreAG'], fechaCreacion=get_time(),
                                estado=True,
                                UtmEste=utm_coord[0],
                                UtmNorte=utm_coord[1],
                                UtmZone=utm_coord[2],
                                UtmZoneLetter=utm_coord[3],
                                proyecto=body['oidProyecto']
                                )
    aero_gen.save()

       
    return jsonify(''), 200

@cross_origin()
@app.route('/rx', methods=['POST'])
def add_rx():
    """Add a receptor"""
    body = request.values
    utm_coord = utm.from_latlon(float(body['latitud']), float(body['longitud']))
    receptor = Receptor(nombre=body['nombreRX'], fechaCreacion=get_time(),
                                estado=True,
                                UtmEste=utm_coord[0],
                                UtmNorte=utm_coord[1],
                                UtmZone=utm_coord[2],
                                UtmZoneLetter=utm_coord[3],
                                proyecto=body['oidProyecto']
                                )
    receptor.save()

    return jsonify(''), 200


#Info Methods

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
