"""Models and database functions for Project."""
# pylint: disable=no-member
from flask_mongoengine import MongoEngine
from datetime import date

db = MongoEngine()

class Proyecto(db.Document):
    """Proyecto model"""
    nombreProyecto = db.StringField(required=True, max_length=200)
    descripcionProyecto = db.StringField(required=False, max_length=200)
    fechaCreacion = db.StringField(required=True, max_length=200, default=date.today().strftime("%d/%m/%Y"))
    estado = db.BooleanField(required=True, default=True)
    Latitud = db.FloatField(required=False)
    Longitud = db.FloatField(required=False)

class AeroGenerador(db.Document):
    """AeroGenerador model"""
    nombre = db.StringField(required=True, max_length=200)
    fechaCreacion = db.StringField(required=True, max_length=200)
    estado = db.BooleanField(required=True, default=True)
    UtmEste = db.FloatField(required=True)
    UtmNorte = db.FloatField(required=True)
    LWS1 = db.FloatField(required=True) #LWS = Nivel de Potencia Sonora segun modo de operacion
    LWS2 = db.FloatField(required=True)
    LWS3 = db.FloatField(required=True)
    Hb = db.FloatField(required=True) #Altura de Buje
    ModoOperacion = db.StringField(required=True, max_length=200)
    Marca = db.StringField(required=True, max_length=200)
    Modelo = db.StringField(required=True, max_length=200)
    proyecto = db.ReferenceField(Proyecto, required=True, reverse_delete_rule=db.CASCADE)

class Receptor(db.Document):
    """Receptor model"""
    nombre = db.StringField(required=True, max_length=200)
    fechaCreacion = db.StringField(required=True, max_length=200)
    estado = db.BooleanField(required=True, default=True)
    UtmEste = db.FloatField(required=True)
    UtmNorte = db.FloatField(required=True)
    Descripcion = db.StringField(required=True, max_length=200)
    Tipo = db.StringField(required=True, max_length=200)
    proyecto = db.ReferenceField(Proyecto, required=True, reverse_delete_rule=db.CASCADE)

class Medicion(db.Document):
    """Medicion model"""
    velViento = db.IntField(required=True)
    anguloViento = db.IntField(required=True)
    AG = db.ReferenceField(AeroGenerador, required=True, reverse_delete_rule=db.CASCADE)
    R = db.ReferenceField(Receptor, required=True, reverse_delete_rule=db.CASCADE)
    NPS = db.FloatField(required=False) #Nivel de Potencia Sonora


#Modelos de Usuario

class User(db.Document):
    """User model"""
    username = db.StringField(required=True, max_length=200)
    password = db.StringField(required=True, max_length=200)
    email = db.StringField(required=True, max_length=200)
    rol = db.StringField(required=True, max_length=200)


class UserProyecto(db.Document):
    """User_Proyecto model"""
    user = db.ReferenceField(User, required=True, reverse_delete_rule=db.CASCADE)
    proyecto = db.ReferenceField(Proyecto, required=True, reverse_delete_rule=db.CASCADE)
    