"""Flask App for the API"""
# pylint: disable=no-member
import math
import os
import utm

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import numpy as np
from models import db, Proyecto, AeroGenerador, Receptor, Medicion

from helpers import get_weather_info, leer_kml, get_time, search_in_xlsx
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
@app.route('/proyectos/<id_proyecto>', methods=['GET']) #TODO: Cambiar a PUT
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
@app.route('/ag', methods=['GET'])
def get_ag():
    """Get all aero generators"""
    aero_generadores = AeroGenerador.objects().to_json()
    return jsonify(aero_generadores), 200

@cross_origin()
@app.route('/ag/<id_proy>', methods=['GET'])
def get_ag_proy(id_proy):
    """Get all aero generators of a project"""
    aero_generadores = AeroGenerador.objects(proyecto=id_proy).to_json()
    return jsonify(aero_generadores), 200

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

@cross_origin()
@app.route('/rx', methods=['GET'])
def get_rx():
    """Get all receptors"""
    receptores = Receptor.objects().to_json()
    return jsonify(receptores), 200

@cross_origin()
@app.route('/rx/<id_proy>', methods=['GET'])
def get_rx_proy(id_proy):
    """Get all receptors of a project"""
    receptores = Receptor.objects(proyecto=id_proy).to_json()
    return jsonify(receptores), 200


#Info Methods

@cross_origin()
@app.route('/gm', methods=['POST'])
def generar_mediciones():
    """Genera los valores de las mediciones del proyecto para cada valor de angulo y velocidad del viento"""
    body = request.values
    #Obtener los aero generadores y sus caracteristicas
    aero_generadores = AeroGenerador.objects(proyecto=body['id_proyecto'])
    #Obtener los receptores y sus caracteristicas
    receptores = Receptor.objects(proyecto=body['id_proyecto'])

    for ag in aero_generadores:
        for rx in receptores:
            par_mediciones = search_in_xlsx(body['id_proyecto'], ag.nombre, rx.nombre)
            if par_mediciones is not None:
                for par in par_mediciones:
                    medicion = Medicion(velViento = par['vel_viento'],
                                        anguloViento = par['angulo'],
                                        AG = ag.id,
                                        R = rx.id,
                                        NPS = par['valor'])
                    medicion.save()
    return jsonify('finalizado'), 200

@cross_origin()
@app.route('/gjson', methods=['POST'])
def crear_geojson():
    """Crea un archivo geojson con los puntos de aero generadores y receptores incluyendo sus mediciones"""
    body = request.values
    receptores = body['receptores']
    #obtener 1 receptor
    r = Receptor.objects.get(id=receptores[0])
    mediciones = Medicion.objects(R=r.id)
    #FIXME: REPENSAR ESTO
    pares_vel_ang = []
    for medicion in mediciones:
        pares_vel_ang.append({'vel_viento': medicion.velViento, 'angulo': medicion.anguloViento})
    for par in pares_vel_ang:
        latitudes = []
        longitudes = []
        for receptor in receptores:
            lat, lon = utm.to_latlon(receptor.UtmEste, receptor.UtmNorte, receptor.UtmZone, receptor.UtmZoneLetter)
            longitudes.append(lon)
            latitudes.append(lat)
            #Obtener el valor de la medicion
            medicion = Medicion.objects.get(R=receptor.id, velViento=par['vel_viento'], anguloViento=par['angulo'])
            
            
            


        



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
