class LogoClub:
    id = None
    lien = None
    principal = False

    def __init__(self):
        pass

    def toJson(self, schema:str) -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else:
            json = {}
            
        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.lien = json['lien'] if json.get('lien') else self.lien
        self.principal = json['principal'] if json.get('principal') else self.principal
        
        return self