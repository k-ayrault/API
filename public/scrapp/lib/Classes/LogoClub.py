class LogoClub:

    def __new__(cls):
        return super(LogoClub, cls).__new__(cls)

    def __init__(self):
        self.id = None
        self.lien = None
        self.principal = False

    def toJson(self, schema:str) -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else:
            json = {
                "id": self.id,
                "lien": self.lien,
                "principal": self.principal
            }
            
        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.lien = json['lien'] if json.get('lien') else self.lien
        self.principal = json['principal'] if json.get('principal') else self.principal
        
        return self