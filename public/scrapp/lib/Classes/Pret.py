from lib.Classes.Contrat import Contrat


class Pret(Contrat):

    def __new__(cls):
        return super(Pret, cls).__new__(cls)

    def __init__(self):
        super().__init__()
        self.option_achat = False
        self.montant_option = 0

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
