class ImageStade:

    def __new__(cls):
        return super(ImageStade, cls).__new__(cls)
    
    def __init__(self):
        self.id = None
        self.lien = None

    def toJson(self, schema:str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {}
        elif schema == 'persist.Stade':
            json = {
                "lien": self.lien
            }
        else:
            json = {
                "id": self.id,
                "lien": self.lien
            }

        return json

    def fromJson(self, json: dict):
        if isinstance(json, str) :
            self.uri = json

            return self
        
        if isinstance(json, list) :
            return self
        
        self.uri = json['@id'] if json.get('@id') else self.uri
        self.id = json['id'] if json.get('id') else self.id
        self.lien = json['lien'] if json.get('lien') else self.lien

        return self