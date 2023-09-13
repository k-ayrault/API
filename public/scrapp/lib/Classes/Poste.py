from lib.Classes.Position import Position

class Poste:

    def __new__(cls):
        return super(Poste, cls).__new__(cls)
    
    def __init__(self):
        self.uri = None
        self.id = None
        self.abreviation = None
        self.nom = None
        self.idTransferMarkt = None
        self.position = Position()

    def toJson(self, schema:str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {
                "id": self.id,
            }
        else :
            json = {
                "id": self.id,
                "abreviation": self.abreviation,
                "nom": self.nom,
                "idTransfermarkt": self.idTransferMarkt,
                "position": self.position.toJson(schema=schema)
            }
        
        return json

    def fromJson(self, json: dict):
        if isinstance(json, str) :
            self.uri = json

            return self
        
        self.uri = json['@id'] if json.get('@id') else self.uri
        self.id = json['id'] if json.get('id') else self.id
        self.abreviation = json['abreviation'] if json.get('abreviation') else self.abreviation
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.idTransferMarkt = json['idTransfermarkt'] if json.get('idTransfermarkt') else self.idTransferMarkt
        self.position = Position().fromJson(json=json['position']) if json.get('position') else self.position

        return self