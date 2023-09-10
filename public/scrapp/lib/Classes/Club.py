from lib.Classes.Pays import Pays
from lib.Classes.Stade import Stade
from lib.Classes.LogoClub import LogoClub

class Club:
    id = None
    nom = None
    pays = Pays()
    dateCreation = None
    siteWeb = None
    logos = []
    idTransferMarkt = None
    stade = Stade()
    
    def __init__(self):
        pass

    def toJson(self, schema:str) -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else :
            json = {
                "id": self.id,
                "nom": self.nom
            }
        
        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.id = Pays().fromJson(json=json['pays']) if json.get('pays') else self.pays
        self.dateCreation = json['date_creation'] if json.get('date_creation') else self.dateCreation
        self.siteWeb = json['site_web'] if json.get('site_web') else self.siteWeb
        self.logos = [LogoClub().fromJson(json=logo) for logo in json['logos']] if json.get('logos') else self.logos
        self.idTransferMarkt = json['id_transfermarkt'] if json.get('id_transfermarkt') else self.idTransferMarkt
        self.stade = Stade().fromJson(json=json['stade']) if json.get('stade') else self.stade

        return self