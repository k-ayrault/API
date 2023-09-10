class CouleurClub:
    id = None
    hexa = None

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
        self.hexa = json['hexa'] if json.get('hexa') else self.hexa

        return self