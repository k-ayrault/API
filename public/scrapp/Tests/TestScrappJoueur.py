import unittest
from lib.ScrappJoueur import ScrappJoueur
from scrapp_func_global import transfermarkt_url_replace
from bs4 import BeautifulSoup


class TestScrappJoueur(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.idJoueurTransfermarkt = "40433"
        cls.lienJoueurTransfermarkt = f"https://www.transfermarkt.fr/alexis-sanchez/{transfermarkt_url_replace}/spieler/40433"

        cls.scrappJoueur = ScrappJoueur(
            idTransferMarkt=cls.idJoueurTransfermarkt, lienJoueurTransferMarkt=cls.lienJoueurTransfermarkt)

    def testGetHTMLSuccessfull(self):
        html = self.scrappJoueur.getHTML()
        self.assertIsInstance(html, BeautifulSoup)

    def testGetHeaderInfoJoueur(self):
        header = self.scrappJoueur.scrappInfoPerso.getHeaderInfoJoueur()
        self.assertIsNotNone(header)

    def testGetInfoTableJoueur(self):
        infoTable = self.scrappJoueur.scrappInfoPerso.getInfoTableJoueur()
        self.assertIsNotNone(infoTable)

    def testScrappNomEtPrenom(self):
        nom, prenom = self.scrappJoueur.scrappInfoPerso.scrappNomEtPrenom()
        self.assertEqual(nom, "Sánchez")
        self.assertEqual(prenom, "Alexis")

    def testScrappNomComplet(self):
        nomComplet = self.scrappJoueur.scrappInfoPerso.scrappNomComplet()
        self.assertEqual(nomComplet, "Alexis Alejandro Sánchez Sánchez")

    def testScrappDateDeNaissance(self):
        dateDeNaissance = self.scrappJoueur.scrappInfoPerso.scrappDateDeNaissance()
        self.assertEqual(dateDeNaissance, "1988-12-19")

    def testScrappNationalite(self):
        nationalites = self.scrappJoueur.scrappInfoPerso.scrappNationalites()
        self.assertEqual(len(nationalites), 1)
        pays = nationalites[0]
        self.assertEqual(pays.code, "CL")

    def testScrappPiedFort(self):
        piedFort = self.scrappJoueur.scrappInfoPerso.scrappPiedFort()
        self.assertEqual(piedFort, "droit")

    def testScrappTaille(self):
        taille = self.scrappJoueur.scrappInfoPerso.scrappTaile()
        self.assertEqual(taille, "169")

    def testScrappEquipementier(self):
        equipementier = self.scrappJoueur.scrappInfoPerso.scrappEquipementierActuel()
        self.assertEqual(equipementier, "Nike")

    def testScrappPositions(self):
        postes = self.scrappJoueur.scrappInfoPerso.scrappPostesJoueur()
        self.assertEqual(len(postes), 3)

    def testScrappDateFinContratActuel(self):
        dateFinContratActuel = self.scrappJoueur.scrappInfoPerso.scrappDateFinContratActuel()
        self.assertEqual(dateFinContratActuel, "2024-06-30")

if __name__ == '__main__':
    unittest.main()
