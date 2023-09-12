import unittest
from lib.API.ApiClient import ApiClient
from lib.Classes.Joueur import Joueur

class TestApiChourmOlympique(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = ApiClient()

    def testAuth(self):
        self.assertIsNotNone(self.api.token)

    def testGetJoueurByIdTransferMarktWithCorrectId(self):
        joueur = self.api.getJoueurByIdTransferMarkt(idTransfermarkt=160)

        self.assertIsInstance(joueur, Joueur)

    def testGetJoueurByIdTransferMarktWithString(self):
        with self.assertRaises(Exception) as context:
            joueur = self.api.getJoueurByIdTransferMarkt(idTransfermarkt="aaa")

    def testGetJoueurByIdTransferMarktWithUnknownId(self):
        with self.assertRaises(Exception) as context:
            joueur = self.api.getJoueurByIdTransferMarkt(idTransfermarkt=177)
