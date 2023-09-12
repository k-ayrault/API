from lib.Classes.Pays import Pays
from lib.Classes.Stade import Stade
from lib.Classes.CouleurClub import CouleurClub
from lib.Classes.LogoClub import LogoClub


class Club:

    def __new__(cls):
        return super(Club, cls).__new__(cls)

    def __init__(self):
        self.id = None
        self.nom = None
        self.adresse = None
        self.pays = Pays()
        self.dateCreation = None
        self.siteWeb = None
        self.couleurs = []
        self.logos = []
        self.idTransferMarkt = None
        self.stade = Stade()

    def toJson(self, schema: str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else:
            json = {
                "id": self.id,
                "nom": self.nom,
                "adresse": self.adresse,
                "pays": self.pays.toJson(schema=schema),
                "dateCreation": self.dateCreation,
                "siteWeb": self.siteWeb,
                "couleurs": [couleur.toJson(schema=schema) for couleur in self.couleurs],
                "logos": [logo.toJson(schema=schema) for logo in self.logos],
                "idTransfermarkt": self.idTransferMarkt,
                "stade": self.stade.toJson(schema=schema)
            }

        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.adresse = json['adresse'] if json.get('adresse') else self.adresse
        self.pays = Pays().fromJson(
            json=json['pays']) if json.get('pays') else self.pays
        self.dateCreation = json['date_creation'] if json.get(
            'date_creation') else self.dateCreation
        self.siteWeb = json['site_web'] if json.get(
            'site_web') else self.siteWeb
        self.couleurs = [CouleurClub().fromJson(json=couleur)
                         for couleur in json['couleurs']] if json.get('couleurs') else self.couleurs
        self.logos = [LogoClub().fromJson(json=logo)
                      for logo in json['logos']] if json.get('logos') else self.logos
        self.idTransferMarkt = json['id_transfermarkt'] if json.get(
            'id_transfermarkt') else self.idTransferMarkt
        self.stade = Stade().fromJson(
            json=json['stade']) if json.get('stade') else self.stade

        return self
