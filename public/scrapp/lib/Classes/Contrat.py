from lib.Classes.Club import Club

class Contrat:
    id = None
    debut = None
    fin = None
    club = Club()
    
    def __init__(self):
        pass

    def toJson(self, schema: str) -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else :
            json = {}
    
        return json
    
    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.debut = json['debut'] if json.get('debut') else self.debut
        self.fin = json['fin'] if json.get('fin') else self.fin
        self.club = Club().fromJson(json=json['club']) if json.get('club') else self.club