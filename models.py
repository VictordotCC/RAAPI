from flask_mongoengine import MongoEngine
db = MongoEngine()

class Proyecto(db.Document):
    nombre = db.StringField(required=True, max_length=200)
    descripcion = db.StringField(required=True, max_length=200)
    fechaCreacion = db.StringField(required=True, max_length=200)
    estado = db.BooleanField(required=True)
    Latitud = db.StringField(required=True, max_length=200)
    Longitud = db.StringField(required=True, max_length=200)

    def to_json(self):
        return {"nombre": self.nombre,
                "descripcion": self.descripcion,
                "fechaCreacion": self.fechaCreacion,
                "estado": self.estado,
                "Latitud": self.Latitud,
                "Longitud": self.Longitud}

class FuentedeRuido(db.Document):
    nombre = db.StringField(required=True, max_length=200)
    descripcion = db.StringField(required=True, max_length=200)
    fechaCreacion = db.StringField(required=True, max_length=200)
    estado = db.BooleanField(required=True)
    Latitud = db.StringField(required=True, max_length=200)
    Longitud = db.StringField(required=True, max_length=200)
    proyecto = db.ReferenceField(Proyecto, required=True, reverse_delete_rule=db.CASCADE)

    def to_json(self):
        return {"nombre": self.nombre,
                "descripcion": self.descripcion,
                "fechaCreacion": self.fechaCreacion,
                "estado": self.estado,
                "Latitud": self.Latitud,
                "Longitud": self.Longitud,
                "proyecto": self.proyecto.to_json()}

class Medicion(db.Document):
    velocidad_viento = db.FloatField(required=True)
    direccion_viento = db.FloatField(required=True)
    valor_ruido = db.FloatField(required=True)
    fuente_ruido = db.ReferenceField(FuentedeRuido, required=True, reverse_delete_rule=db.CASCADE)

    def to_json(self):
        return {"velocidad_viento": self.velocidad_viento,
                "direccion_viento": self.direccion_viento,
                "valor_ruido": self.valor_ruido,
                "fuente_ruido": self.fuente_ruido.to_json()}





    