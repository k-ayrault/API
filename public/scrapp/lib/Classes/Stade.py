from lib.Classes.Pays import Pays
from lib.Classes.ImageStade import ImageStade

class Stade:
    id = None
    nom = None
    pays = Pays()
    adresse = None
    capacite = None
    anneeConstruction = None
    images = []
    
    def __init__(self):
        pass

    def toJson(self, schema: dict) -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else:
            json = {
                "id": self.id,
                "nom": self.nom,
                "pays": self.pays.toJson(schema=schema),
                "adresse": self.adresse,
                "capacite": self.capacite,
                "annee_construction": self.anneeConstruction,
                "images": [image.toJson(schema=schema) for image in self.images]
            }

        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.pays = Pays().fromJson(json=json['pays']) if json.get('pays') else self.pays
        self.adresse = json['adresse'] if json.get('adresse') else self.adresse
        self.capacite = json['capacite'] if json.get('capacite') else self.capacite
        self.anneeConstruction = json['annee_construction'] if json.get('annee_construction') else self.anneeConstruction
        self.id = [ImageStade().fromJson(json=image) for image in json['images']] if json.get('images') else self.images

        return self