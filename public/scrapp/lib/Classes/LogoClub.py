class LogoClub:

    def __new__(cls):
        return super(LogoClub, cls).__new__(cls)

    def __init__(self):
        self.uri = None
        self.id = None
        self.lien = None
        self.principal = False

    def toJson(self, schema:str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {}
        elif schema == 'persist.Club':
            json = {
                "lien": self.lien,
                "principal": self.principal
            }
        else:
            json = {
                "id": self.id,
                "lien": self.lien,
                "principal": self.principal
            }
            
        return json

    def fromJson(self, json: dict):
        if isinstance(json, str) :
            self.uri = json

            return self
        
        self.uri = json['@id'] if json.get('@id') else self.uri
        self.id = json['id'] if json.get('id') else self.id
        self.lien = json['lien'] if json.get('lien') else self.lien
        self.principal = json['principal'] if json.get('principal') else self.principal
        
        return self