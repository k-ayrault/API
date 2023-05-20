class Pays:
    code = None
    nom = None
    drapeau = None
    nomFR = None
    
    def __init__(self):
        pass

    def toJson(self, schema:str) -> dict:
        if schema == 'persist.Joueur':
            json = {
                "code": self.code
            }
        else:
            json = {
                "code": self.code,
                "nom": self.nom,
                "drapeau": self.drapeau,
                "nom_fr": self.nomFR
            }
        return json

    def fromJson(self, json: dict):
        self.code = json['code'] if json.get('code') else self.code
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.drapeau = json['drapeau'] if json.get('drapeau') else self.drapeau
        self.nomFR = json['nom_fr'] if json.get('nom_fr') else self.nomFR
        