from lib.Classes.Club import Club

class Contrat:

    def __new__(cls):
        return super(Contrat, cls).__new__(cls)
    
    def __init__(self):
        self.uri = None
        self.id = None
        self.debut = None
        self.fin = None
        self.club = Club()

    def toJson(self, schema: str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else :
            json = {}
    
        return json
    
    def fromJson(self, json: dict):
        if isinstance(json, str) :
            self.uri = json

            return self
        
        self.uri = json['@id'] if json.get('@id') else self.uri
        self.id = json['id'] if json.get('id') else self.id
        self.debut = json['debut'] if json.get('debut') else self.debut
        self.fin = json['fin'] if json.get('fin') else self.fin
        self.club = Club().fromJson(json=json['club']) if json.get('club') else self.club

        return self