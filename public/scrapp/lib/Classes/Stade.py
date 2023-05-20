from lib.Classes.Pays import Pays


class Stade:
    id = None
    nom = None
    pays = Pays()
    adresse = None
    capacite = None
    annee_construction = None
    images = []
    
    def __init__(self):
        pass

    def toJson(self) -> dict:
        pass

    def fromJson(self, json: dict):
        pass