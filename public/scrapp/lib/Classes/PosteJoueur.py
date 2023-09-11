from lib.Classes.Poste import Poste

class PosteJoueur:

    def __new__(cls):
        return super(PosteJoueur, cls).__new__(cls)
    
    def __init__(self):
        self.id = None
        self.principale = False
        self.poste = Poste()

    def toJson(self, schema: str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {
                "principal": self.principale,
                "poste": self.poste.toJson(schema=schema)
            }
        else :
            json = {
                "id": self.id,
                "principale": self.principale,
                "poste": self.poste.toJson(schema=schema)
            }

        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.principale = json['principal'] if json.get('principal') else self.principale
        self.poste = Poste().fromJson(json=json['poste']) if json.get('poste') else self.poste

        return self