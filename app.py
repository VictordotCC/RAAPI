"""Flask App for the API"""
# pylint: disable=no-member
import os
import utm

import numpy as np
import pandas as pd
import geopandas as gpd
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from scipy.interpolate import griddata
import matplotlib.colors as clrs
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
    aerogeneradores = body['aerogeneradores']
    #obtener 1 receptor
    r = Receptor.objects.get(id=receptores[0])
    mediciones = Medicion.objects(R=r.id)
    pares_vel_ang = []
    for medicion in mediciones:
        if {'vel_viento': medicion.velViento, 'angulo': medicion.anguloViento} not in pares_vel_ang:
            pares_vel_ang.append({'vel_viento': medicion.velViento, 'angulo': medicion.anguloViento})
    for par in pares_vel_ang:
        latitudes = []
        longitudes = []
        mediciones = []
        for receptor in receptores:
            suma_medicion = 0
            for aerogenerador in aerogeneradores:
                medicion = Medicion.objects.get(R=receptor, AG=aerogenerador, velViento=par['vel_viento'], anguloViento=par['angulo'])
                opmedicion = 10**(medicion.NPS/10)
                suma_medicion += opmedicion
            total_medicion = 10*np.log10(suma_medicion)
            mediciones.append(total_medicion)
            lat, lon = utm.to_latlon(receptor.UtmEste, receptor.UtmNorte, receptor.UtmZone, receptor.UtmZoneLetter)
            longitudes.append(lon)
            latitudes.append(lat)
        #Crear el geojson
        xlist = np.linspace(np.min(longitudes), np.max(longitudes), 100)
        ylist = np.linspace(np.min(latitudes), np.max(latitudes), 100)
        x, y = np.meshgrid(xlist, ylist)
        z = griddata((longitudes, latitudes), mediciones, (x, y), method='linear')

        colors = ['#B0E57C', '#F4D06F', '#F7A83E', '#E7604A', '#9F1C20']
        vmin = 0
        vmax = 140
        levels = len(colors) - 1
        step = (vmax - vmin) / levels

        cmap = clrs.ListedColormap(colors)
        norm = clrs.BoundaryNorm(np.arange(vmin, vmax + step, step), cmap.N)

        hexcolors = [cmap(norm(v)) for v in mediciones]
        hexcolors = [colors.to_hex(color) for color in hexcolors]

        pointsdf = pd.DataFrame({'Longitud': longitudes, 'Latitud': latitudes, 'marker-color': hexcolors, 'NPS': mediciones})

        geo_df = gpd.GeoDataFrame(pointsdf, geometry = gpd.points_from_xy(pointsdf.Longitud, pointsdf.Latitud))

        filename = 'geojsons/' + body['id_proyecto'] + '_' + str(par['vel_viento']) + '_' + str(par['angulo']) + '.geojson'
        geo_df.to_file(filename, driver='GeoJSON')

    return jsonify('GeoJSON creados'), 200


if __name__ == '__main__':
    app.run(debug=True)
