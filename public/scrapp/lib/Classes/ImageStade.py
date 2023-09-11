class ImageStade:

    def __new__(cls):
        return super(ImageStade, cls).__new__(cls)
    
    def __init__(self):
        self.id = None
        self.lien = None

    def toJson(self, schema:str) -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else:
            json = {
                "id": self.id,
                "lien": self.lien
            }

        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.lien = json['lien'] if json.get('lien') else self.lien

        return self