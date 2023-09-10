from lib.Classes.Pays import Pays


class InformationsPersonelles:
    id = None
    nomComplet = None
    nom = None
    prenom = None
    dateNaissance = None
    meilleurPied = None
    taille = None
    equipementier = None
    nationalites = []
    retraiteJoueur = None

    def __init__(self):
        pass

    def toJson(self, schema: str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {
                "nom_complet": self.nomComplet,
                "nom": self.nom,
                "prenom": self.prenom,
                "date_naissance": self.dateNaissance,
                "meilleur_pied": self.meilleurPied,
                "taille": self.taille,
                "equipementier": self.equipementier,
                "nationnalites": [pays.toJson(schema=schema) for pays in self.nationalites],
                "retraite_joueur": self.retraiteJoueur
            }
        elif schema == 'persist.InformationsPersonellesTemp':\
            json = {
                "id": self.id
            }
        else:
            json = {
                "id": self.id,
                "nom_complet": self.nomComplet,
                "nom": self.nom,
                "prenom": self.prenom,
                "date_naissance": self.dateNaissance,
                "meilleur_pied": self.meilleurPied,
                "taille": self.taille,
                "equipementier": self.equipementier,
                "nationnalites": [pays.toJson(schema=schema) for pays in self.nationalites],
                "retraite_joueur": self.retraiteJoueur
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

        return self