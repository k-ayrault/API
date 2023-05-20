import unittest
from lib.ApiChourmOlympique import ApiChourmOlympique
from lib.Classes.Joueur import Joueur

class TestApiChourmOlympique(unittest.TestCase):

    def setUp(self):
        self.api = ApiChourmOlympique()

    def testAuth(self):
        self.assertIsNotNone(self.api.token)

    def testGetJoueurByIdTransferMarktWithCorrectId(self):
        joueur = self.api.getJoueurByIdTransferMarkt(160)

        self.assertIsInstance(joueur, Joueur)

    def testGetJoueurByIdTransferMarktWithString(self):
        with self.assertRaises(Exception) as context:
            joueur = self.api.getJoueurByIdTransferMarkt("aaa")

    def testGetJoueurByIdTransferMarktWithUnknownId(self):
        with self.assertRaises(Exception) as context:
            joueur = self.api.getJoueurByIdTransferMarkt(177)