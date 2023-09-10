import unittest
from lib.ScrappJoueur import ScrappJoueur
from lib.ScrappContrats import ScrappContrats
from scrapp_func_global import transfermarkt_url_replace
from bs4 import BeautifulSoup


class TestScrappJoueur(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.idJoueurTransfermarkt = "40433"
        cls.lienJoueurTransfermarkt = f"https://www.transfermarkt.fr/alexis-sanchez/{transfermarkt_url_replace}/spieler/40433"

        cls.scrappJoueur = ScrappJoueur(
            idJoueurTransferMarkt=cls.idJoueurTransfermarkt, lienJoueurTransferMarkt=cls.lienJoueurTransfermarkt)
        
        html = cls.scrappJoueur.getHTML()
        cls.scrappContrats = ScrappContrats(idJoueurTransferMarkt=cls.idJoueurTransfermarkt, html=html, contrats=[])

    def testGetTableauTransfert(self):
        tableauTransfert = self.scrappContrats.getTableauTransfert()

        self.assertIsNotNone(tableauTransfert)

    def testGetLignesTransferts(self):
        lignes = self.scrappContrats.getLignesTransferts()
        
        self.assertEqual(len(lignes), 13)

if __name__ == '__main__':
    unittest.main()
