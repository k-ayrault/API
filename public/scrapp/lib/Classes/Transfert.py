from lib.Classes.Club import Club
from lib.Classes.Contrat import Contrat

class Transfert(Contrat):

    club_formateur = False

    libre = False

    montant = 0
    
    def __init__(self):
        pass

    def toJson(self, schema: str = "") -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else :
            json = {
                "id": self.id,
                "debut": self.debut,
                "fin": self.fin,
                "club": self.club.toJson(schema=schema),
                "club_formateur": self.club_formateur,
                "libre": self.libre,
                "montant": self.montant
            }
    
        return json
    
    def fromJson(self, json: dict):
        super().fromJson(json=json)
        self.club_formateur = json['club_formateur'] if json.get('club_formateur') else self.club_formateur
        self.libre = json['libre'] if json.get('libre') else self.libre
        self.montant = json['montant'] if json.get('montant') else self.montant

        return self