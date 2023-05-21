from lib.Classes.Position import Position

class Poste:
    id = None
    abreviation = None
    nom = None
    idTransferMarkt = None
    position = Position()
    
    def __init__(self):
        pass

    def toJson(self, schema:str) -> dict:
        if schema == 'persist.Joueur':
            json = {
                "id": self.id,
            }
        else :
            json = {
                "id": self.id,
                "abreviation": self.abreviation,
                "nom": self.nom,
                "id_transfermarkt": self.idTransferMarkt,
                "position": self.position.toJson(schema=schema)
            }
        
        return json

    def fromJson(self, json: dict):
        self.id = json['id'] if json.get('id') else self.id
        self.abreviation = json['abreviation'] if json.get('abreviation') else self.abreviation
        self.nom = json['nom'] if json.get('nom') else self.nom
        self.idTransferMarkt = json['id_transfermarkt'] if json.get('id_transfermarkt') else self.idTransferMarkt
        self.position = Position().fromJson(json=json['position']) if json.get('position') else self.position

        return self