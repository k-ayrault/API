class Position:

    def __new__(cls):
        return super(Position, cls).__new__(cls)
    
    def __init__(self):
        self.id = None
        self.nom = None
    
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