from flask_mongoengine import MongoEngine
db = MongoEngine()

class Proyecto(db.Document):
    nombre = db.StringField(required=True, max_length=200)
    descripcion = db.StringField(required=False, max_length=200)
    fechaCreacion = db.StringField(required=True, max_length=200)
    estado = db.BooleanField(required=True)
    Latitud = db.FloatField(required=False)
    Longitud = db.FloatField(required=False)

    def to_json(self):
        return {"nombre": self.nombre,
                "descripcion": self.descripcion,
                "fechaCreacion": self.fechaCreacion,
                "estado": self.estado,
                "Latitud": self.Latitud,
                "Longitud": self.Longitud}

class AeroGenerador(db.Document):
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

    def to_json(self):
        return {"nombre": self.nombre,
                "descripcion": self.descripcion,
                "fechaCreacion": self.fechaCreacion,
                "estado": self.estado,
                "Latitud": self.Latitud,
                "Longitud": self.Longitud,
                "proyecto": self.proyecto.to_json()}

class Receptor(db.Document):
    nombre = db.StringField(required=True, max_length=200)
    fechaCreacion = db.StringField(required=True, max_length=200)
    estado = db.BooleanField(required=True, default=True)
    UtmEste = db.FloatField(required=True)
    UtmNorte = db.FloatField(required=True)
    Descripcion = db.StringField(required=True, max_length=200)
    Tipo = db.StringField(required=True, max_length=200)
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
    velViento = db.IntField(required=True)
    anguloViento = db.IntField(required=True)
    AG = db.ReferenceField(AeroGenerador, required=True, reverse_delete_rule=db.CASCADE)
    R = db.ReferenceField(Receptor, required=True, reverse_delete_rule=db.CASCADE)
    NPS = db.FloatField(required=False) #Nivel de Potencia Sonora

    def to_json(self):
        return {"VelViento": self.VelViento,
                "AnguloViento": self.AnguloViento,
                "AG": self.AG.to_json(), #AeroGenerador
                "R": self.R.to_json(), #Receptor
                "valor": self.valor}


#Modelos de Usuario

class User(db.Document):
    username = db.StringField(required=True, max_length=200)
    password = db.StringField(required=True, max_length=200)
    email = db.StringField(required=True, max_length=200)
    rol = db.StringField(required=True, max_length=200)

    def to_json(self):
        return {"username": self.username,
                "email": self.email,
                "rol": self.rol}

class User_Proyecto(db.Document):
    user = db.ReferenceField(User, required=True, reverse_delete_rule=db.CASCADE)
    proyecto = db.ReferenceField(Proyecto, required=True, reverse_delete_rule=db.CASCADE)

    def to_json(self):
        return {"user": self.user.to_json(),
                "proyecto": self.proyecto.to_json()}



    