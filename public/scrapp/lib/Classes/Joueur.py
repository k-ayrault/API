from lib.Classes.InformationsPersonelles import InformationsPersonelles
from lib.Classes.PosteJoueur import PosteJoueur
from lib.Classes.Contrat import Contrat


class Joueur:

    def __new__(cls):
        return super(Joueur, cls).__new__(cls)

    def __init__(self):
        self.uri = None
        self.id = None
        self.idTransfermarkt = None
        self.informationsPersonelles = InformationsPersonelles()
        self.postes = []
        self.contrats = []

    def toJson(self, schema: str = ""):
        if schema == 'persist.Joueur':
            json = {
                "id_transfermarkt": self.idTransfermarkt,
                "informations_personnelles": self.informationsPersonelles.toJson(schema=schema),
                "postes": [poste.toJson(schema=schema) for poste in self.postes],
                "contrats": [contrat.toJson(schema=schema) for contrat in self.contrats]
            }
        else:
            json = {
                "id": self.id,
                "id_transfermarkt": self.idTransfermarkt,
                "informations_personnelles": self.informationsPersonelles.toJson(schema=schema),
                "postes": [poste.toJson(schema=schema) for poste in self.postes],
                "contrats": [contrat.toJson(schema=schema) for contrat in self.contrats]
            }
            
        return json

    def fromJson(self, json: dict):
        if isinstance(json, str) :
            self.uri = json

            return self
        
        self.uri = json['@id'] if json.get('@id') else self.uri
        self.id = json['id'] if json.get('id') else self.id
        self.idTransfermarkt = json['id_transfermarkt'] if json.get('id_transfermarkt') else self.idTransfermarkt
        self.informationsPersonelles.fromJson(json=json['informations_personnelles']) if json.get('informations_personnelles') else self.informationsPersonelles
        self.postes = [PosteJoueur().fromJson(json=poste) for poste in json['postes']] if json.get('postes') else self.postes
        self.contrats = [Contrat().fromJson(json=contrat) for contrat in json['contrats']] if json.get('contrats') else self.contrats
        
        return self
