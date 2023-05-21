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
            idJoueurTransferMarkt=cls.idJoueurTransfermarkt, lienJoueurTransferMarkt=cls.lienJoueurTransfermarkt)

    def testGetHTMLSuccessfull(self):
        html = self.scrappJoueur.getHTML()
        self.assertIsInstance(html, BeautifulSoup)

    def testGetHeaderInfoJoueur(self):
        html = self.scrappJoueur.getHTML()
        header = self.scrappJoueur.getHeaderInfoJoueur()
        self.assertIsNotNone(header)

    def testGetInfoTableJoueur(self):
        html = self.scrappJoueur.getHTML()
        infoTable = self.scrappJoueur.getInfoTableJoueur()
        self.assertIsNotNone(infoTable)

    def testScrappNomEtPrenom(self):
        html = self.scrappJoueur.getHTML()
        header = self.scrappJoueur.getHeaderInfoJoueur()
        nom, prenom = self.scrappJoueur.scrappNomEtPrenom()
        self.assertEqual(nom, "Sánchez")
        self.assertEqual(prenom, "Alexis")

    def testScrappNomComplet(self):
        html = self.scrappJoueur.getHTML()
        infoTable = self.scrappJoueur.getInfoTableJoueur()
        nomComplet = self.scrappJoueur.scrappNomComplet()
        self.assertEqual(nomComplet, "Alexis Alejandro Sánchez Sánchez")

    def testScrappDateDeNaissance(self):
        html = self.scrappJoueur.getHTML()
        infoTable = self.scrappJoueur.getInfoTableJoueur()
        dateDeNaissance = self.scrappJoueur.scrappDateDeNaissance()
        self.assertEqual(dateDeNaissance, "1988-12-19")

    def testScrappNationalite(self):
        html = self.scrappJoueur.getHTML()
        infoTable = self.scrappJoueur.getInfoTableJoueur()
        nationalites = self.scrappJoueur.scrappNationalites()
        self.assertEqual(len(nationalites), 1)
        pays = nationalites[0]
        self.assertEqual(pays.code, "CL")

    def testScrappPiedFort(self):
        html = self.scrappJoueur.getHTML()
        infoTable = self.scrappJoueur.getInfoTableJoueur()
        piedFort = self.scrappJoueur.scrappPiedFort()
        self.assertEqual(piedFort, "droit")

    def testScrappTaille(self):
        html = self.scrappJoueur.getHTML()
        infoTable = self.scrappJoueur.getInfoTableJoueur()
        taille = self.scrappJoueur.scrappTaile()
        self.assertEqual(taille, "169")

    def testScrappEquipementier(self):
        html = self.scrappJoueur.getHTML()
        infoTable = self.scrappJoueur.getInfoTableJoueur()
        equipementier = self.scrappJoueur.scrappEquipementierActuel()
        self.assertEqual(equipementier, "Nike")

    def testScrappPositions(self):
        html = self.scrappJoueur.getHTML()
        postes = self.scrappJoueur.scrappPositions()
        self.assertEqual(len(postes), 3)
        # TODO : peut-être rajouter des tests

    def testScrappDateFinContratActuel(self):
        html = self.scrappJoueur.getHTML()
        infoTable = self.scrappJoueur.getInfoTableJoueur()
        dateFinContratActuel = self.scrappJoueur.scrappDateFinContratActuel()
        self.assertEqual(dateFinContratActuel, "2023-06-30")

if __name__ == '__main__':
    unittest.main()
