class Position:
    id = None
    nom = None
    
    def __init__(self):
        pass
    
    def toJson(self, schema: str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else :
            json = {
                "id": self.id,
                "nom": self.nom
            }
        
        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.nom = json['nom'] if json.get('nom') else self.nom

        return self