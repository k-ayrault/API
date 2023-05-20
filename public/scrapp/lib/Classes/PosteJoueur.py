from lib.Classes.Poste import Poste

class PosteJoueur:
    id = None
    principale = False
    poste = Poste()
    
    def __init__(self):
        pass

    def toJson(self, schema: str) -> dict:
        if schema == 'persist.Joueur':
            json = {
                "principale": self.principale,
                "poste": self.poste.toJson(schema=schema)
            }
        else :
            json = {
                "id": self.id,
                "principale": self.principale,
                "poste": self.poste.toJson(schema=schema)
            }

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.principale = json['principale'] if json.get('principale') else self.principale
        self.poste = Poste().fromJson(json=json['poste']) if json.get('poste') else self.poste