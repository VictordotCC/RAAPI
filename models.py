from flask_mongoengine import MongoEngine
db = MongoEngine()

class Proyecto(db.Document):
    nombre = db.StringField(required=True, max_length=200)
    descripcion = db.StringField(required=True, max_length=200)
    fechaCreacion = db.StringField(required=True, max_length=200)
    estado = db.StringField(required=True, max_length=200)
    Latitud = db.StringField(required=True, max_length=200)
    Longitud = db.StringField(required=True, max_length=200)

    def to_json(self):
        return {"nombre": self.nombre,
                "descripcion": self.descripcion,
                "fechaCreacion": self.fechaCreacion,
                "estado": self.estado,
                "Latitud": self.Latitud,
                "Longitud": self.Longitud}
    