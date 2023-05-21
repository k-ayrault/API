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
        elif schema == 'patch.Pays.drapeau':
            json = {
                "code": self.code,
                "drapeau": self.drapeau
            }
        else:
            json = {
                "code": self.code,
                "nom": self.nom,
                "drapeau": self.drapeau,
                "nomFr": self.nomFR
            }
        return json

    def fromJson(self, json: dict):
        self.code = json['code'] if json.get('code') else self.code
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.drapeau = json['drapeau'] if json.get('drapeau') else self.drapeau
        self.nomFR = json['nom_fr'] if json.get('nom_fr') else self.nomFR
        
        return self