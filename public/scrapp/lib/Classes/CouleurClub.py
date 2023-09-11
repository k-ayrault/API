class CouleurClub:
    
    def __new__(cls):
        return super(CouleurClub, cls).__new__(cls)

    def __init__(self):
        self.id = None
        self.hexa = None

    def toJson(self, schema:str) -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else:
            json = {
                "id": self.id,
                "hexa": self.hexa
            }
            
        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.hexa = json['hexa'] if json.get('hexa') else self.hexa

        return self