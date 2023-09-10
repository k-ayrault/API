from lib.Classes.Club import Club
from lib.Classes.Contrat import Contrat


class Pret(Contrat):
    option_achat = False

    montant_option = 0

    def __init__(self):
        pass

    def toJson(self, schema: str = '') -> dict:
        if schema == 'persist.Joueur':
            json = {}
        else:
            json = {
                "id": self.id,
                "debut": self.debut,
                "fin": self.fin,
                "club": self.club.toJson(schema=schema),
                "option_achat": self.option_achat,
                "montant_option": self.montant_option
            }

        return json

    def fromJson(self, json: dict):
        super().fromJson(json=json)
        self.option_achat = json['option_achat'] if json.get(
            'option_achat') else self.option_achat
        self.montant_option = json['montant_option'] if json.get(
            'montant_option') else self.montant_option

        return self
