class Pays:

    def __new__(cls):
        return super(Pays, cls).__new__(cls)
    
    def __init__(self):
        self.uri = None
        self.code = None
        self.nom = None
        self.drapeau = None
        self.nomFR = None

    def toJson(self, schema:str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {
                "code": self.code
            }
        elif schema == 'patch.Pays.drapeau':
            json = {
                "code": self.code,
                "drapeau": self.drapeau
            }
        elif schema == 'persist.Club':
            json = self.uri
        else:
            json = {
                "code": self.code,
                "nom": self.nom,
                "drapeau": self.drapeau,
                "nomFr": self.nomFR
            }
        return json

    def fromJson(self, json: dict):
        if isinstance(json, str) :
            self.uri = json

            return self
        
        self.uri = json['@id'] if json.get('@id') else self.uri
        self.code = json['code'] if json.get('code') else self.code
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.drapeau = json['drapeau'] if json.get('drapeau') else self.drapeau
        self.nomFR = json['nom_fr'] if json.get('nom_fr') else self.nomFR
        
        return self