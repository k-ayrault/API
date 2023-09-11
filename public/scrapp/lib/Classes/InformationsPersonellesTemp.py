from lib.Classes.InformationsPersonelles import InformationsPersonelles
from lib.Classes.Pays import Pays


class InformationsPersonellesTemp(InformationsPersonelles):

    def __new__(cls):
        return super(InformationsPersonellesTemp, cls).__new__(cls)

    def __init__(self, informationsPersonelles: InformationsPersonelles):
        super().__init__()
        self.informationsPersonelles = informationsPersonelles

    def toJson(self, schema: str = "") -> dict:
        if schema in ['persist.InformationsPersonellesTemp']:
            json = {
                "nom_complet": self.nomComplet,
                "nom": self.nom,
                "prenom": self.prenom,
                "date_naissance": self.dateNaissance,
                "meilleur_pied": self.meilleurPied,
                "taille": self.taille,
                "equipementier": self.equipementier,
                "nationnalites": [pays.toJson(schema=schema) for pays in self.nationalites],
                "retraite_joueur": self.retraiteJoueur,
                "informationsPersonelles" : self.informationsPersonelles.toJson(schema=schema)
            }
        else :
            json = {
                "id" : self.id,
                "nom_complet": self.nomComplet,
                "nom": self.nom,
                "prenom": self.prenom,
                "date_naissance": self.dateNaissance,
                "meilleur_pied": self.meilleurPied,
                "taille": self.taille,
                "equipementier": self.equipementier,
                "nationnalites": [pays.toJson(schema=schema) for pays in self.nationalites],
                "retraite_joueur": self.retraiteJoueur,
                "informationsPersonelles" : self.informationsPersonelles.toJson(schema=schema)
            }
            
        return json


    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.nomComplet = json['nom_complet'] if json.get('nom_complet') else self.nomComplet
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.prenom = json['prenom'] if json.get('prenom') else self.prenom
        self.dateNaissance = json['date_naissance'] if json.get('date_naissance') else self.dateNaissance
        self.meilleurPied = json['meilleur_pied'] if json.get('meilleur_pied') else self.meilleurPied
        self.taille = json['taille'] if json.get('taille') else self.taille
        self.equipementier = json['equipementier'] if json.get('equipementier') else self.equipementier
        self.nationalites = [Pays().fromJson(json=pays) for pays in json['nationnalites']] if json.get('nationnalites') else self.nationalites
        self.retraiteJoueur = json['retraite_joueur'] if json.get('retraite_joueur') else self.retraiteJoueur
        self.informationsPersonelles = InformationsPersonelles().fromJson(json=json['informationsPersonelles']) if json.get('informationsPersonelles') else self.informationsPersonelles

        return self
    