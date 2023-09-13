from lib.Classes.Pays import Pays
from lib.Classes.Stade import Stade
from lib.Classes.CouleurClub import CouleurClub
from lib.Classes.LogoClub import LogoClub


import json as oejson

class Club:

    def __new__(cls):
        return super(Club, cls).__new__(cls)

    def __init__(self):
        self.uri = None
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
        elif schema == 'persist.Club':
            json = {
                "nom": self.nom,
                "adresse": self.adresse,
                "pays": f"/api/pays/{self.pays.code}" if self.pays.code is not None else None,
                "dateCreation": self.dateCreation,
                "siteWeb": self.siteWeb,
                "couleurs": [couleur.toJson(schema=schema) for couleur in self.couleurs],
                "logos": [logo.toJson(schema=schema) for logo in self.logos],
                "idTransfermarkt": int(self.idTransferMarkt) if self.idTransferMarkt is not None else None,
                "stade": f"/api/stade/{self.stade.id}" if self.stade.id is not None else None
            }
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
        if isinstance(json, str) :
            self.uri = json

            return self
        
        self.uri = json['@id'] if json.get('@id') else self.uri
        self.id = json['id'] if json.get('id') else self.id
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.adresse = json['adresse'] if json.get('adresse') else self.adresse
        self.pays = Pays().fromJson(
            json=json['pays']) if json.get('pays') else self.pays
        self.dateCreation = json['dateCreation'] if json.get(
            'dateCreation') else self.dateCreation
        self.siteWeb = json['siteWeb'] if json.get(
            'siteWeb') else self.siteWeb
        self.couleurs = [CouleurClub().fromJson(json=couleur)
                         for couleur in json['couleurs']] if json.get('couleurs') else self.couleurs
        self.logos = [LogoClub().fromJson(json=logo)
                      for logo in json['logos']] if json.get('logos') else self.logos
        self.idTransferMarkt = json['idTransfermarkt'] if json.get(
            'idTransfermarkt') else self.idTransferMarkt
        self.stade = Stade().fromJson(
            json=json['stade']) if json.get('stade') else self.stade

        return self
