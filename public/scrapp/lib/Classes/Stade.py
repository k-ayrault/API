from lib.Classes.Pays import Pays
from lib.Classes.ImageStade import ImageStade

class Stade:

    def __new__(cls):
        return super(Stade, cls).__new__(cls)
    
    def __init__(self):
        self.uri = None
        self.id = None
        self.nom = None
        self.pays = Pays()
        self.adresse = None
        self.capacite = None
        self.anneeConstruction = None
        self.images = []

    def toJson(self, schema: str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {}
        elif schema == 'persist.Club':
            json = self.uri
        elif schema == 'persist.Stade':
            json = {
                "nom": self.nom,
                "pays": self.pays.toJson(schema=schema),
                "adresse": self.adresse,
                "capacite": self.capacite,
                "anneeConstruction": self.anneeConstruction,
                "images": [image.toJson(schema=schema) for image in self.images]
            }
        else:
            json = {
                "id": self.id,
                "nom": self.nom,
                "pays": self.pays.toJson(schema=schema),
                "adresse": self.adresse,
                "capacite": self.capacite,
                "anneeConstruction": self.anneeConstruction,
                "images": [image.toJson(schema=schema) for image in self.images]
            }

        return json

    def fromJson(self, json: dict):
        if isinstance(json, str) :
            self.uri = json

            return self
        
        self.uri = json['@id'] if json.get('@id') else self.uri
        self.id = json['id'] if json.get('id') else self.id
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.pays = Pays().fromJson(json=json['pays']) if json.get('pays') else self.pays
        self.adresse = json['adresse'] if json.get('adresse') else self.adresse
        self.capacite = json['capacite'] if json.get('capacite') else self.capacite
        self.anneeConstruction = json['anneeConstruction'] if json.get('anneeConstruction') else self.anneeConstruction
        self.images = [ImageStade().fromJson(json=image) for image in json['images']] if json.get('images') else self.images

        return self