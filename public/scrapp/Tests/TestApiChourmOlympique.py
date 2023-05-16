import unittest
from lib.ApiChourmOlympique import ApiChourmOlympique

class TestApiChourmOlympique(unittest.TestCase):

    def setUp(self):
        self.api = ApiChourmOlympique()

    def testAuth(self):
        self.assertIsNotNone(self.api.token)

    def testGetJoueurByIdTransferMarktWithCorrectId(self):
        joueur = self.api.getJoueurByIdTransferMarkt(160)

        self.assertIsNotNone(joueur)

    def testGetJoueurByIdTransferMarktWithString(self):
        with self.assertRaises(Exception) as context:
            joueur = self.api.getJoueurByIdTransferMarkt("aaa")

    def testGetJoueurByIdTransferMarktWithUnknownId(self):
        with self.assertRaises(Exception) as context:
            joueur = self.api.getJoueurByIdTransferMarkt(177)