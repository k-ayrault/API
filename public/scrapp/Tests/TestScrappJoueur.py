import unittest
from ScrappJoueur import ScrappJoueur
from scrapp_func_global import transfermarkt_url_replace
from bs4 import BeautifulSoup


class TestScrappJoueur(unittest.TestCase):

    def setUp(self):
        self.id_joueur_transfermarkt = "40433"
        self.lien_joueur_transfermarkt = f"https://www.transfermarkt.fr/alexis-sanchez/{transfermarkt_url_replace}/spieler/40433"

        self.scrapp_joueur = ScrappJoueur(
            id_joueur_transfermarkt=self.id_joueur_transfermarkt, lien_joueur_transfermarkt=self.lien_joueur_transfermarkt)

    def testGetHTMLSuccessfull(self):
        html = self.scrapp_joueur.getHTML()
        self.assertIsInstance(html, BeautifulSoup)

    def testGetHeaderInfoJoueur(self):
        html = self.scrapp_joueur.getHTML()
        header = self.scrapp_joueur.getHeaderInfoJoueur()
        self.assertIsNotNone(header)

    def testGetInfoTableJoueur(self):
        html = self.scrapp_joueur.getHTML()
        info_table = self.scrapp_joueur.getInfoTableJoueur()
        self.assertIsNotNone(info_table)

    def testScrappNomEtPrenom(self):
        html = self.scrapp_joueur.getHTML()
        header = self.scrapp_joueur.getHeaderInfoJoueur()
        nom, prenom = self.scrapp_joueur.scrappNomEtPrenom()
        self.assertEqual(nom, "Sánchez")
        self.assertEqual(prenom, "Alexis")

    def testScrappNomComplet(self):
        html = self.scrapp_joueur.getHTML()
        info_table = self.scrapp_joueur.getInfoTableJoueur()
        nom_complet = self.scrapp_joueur.scrappNomComplet()
        self.assertEqual(nom_complet, "Alexis Alejandro Sánchez Sánchez")

    def testScrappDateDeNaissance(self):
        html = self.scrapp_joueur.getHTML()
        info_table = self.scrapp_joueur.getInfoTableJoueur()
        nom_complet = self.scrapp_joueur.scrappDateDeNaissance()
        self.assertEqual(nom_complet, "1988-12-19")

    def testScrappNationalite(self):
        html = self.scrapp_joueur.getHTML()
        info_table = self.scrapp_joueur.getInfoTableJoueur()
        nom_complet = self.scrapp_joueur.scrappNationalites()
        self.assertEqual(nom_complet, ["Chili"])

    def testScrappPiedFort(self):
        html = self.scrapp_joueur.getHTML()
        info_table = self.scrapp_joueur.getInfoTableJoueur()
        pied_fort = self.scrapp_joueur.scrappPiedFort()
        self.assertEqual(pied_fort, "droit")

    def testScrappTaille(self):
        html = self.scrapp_joueur.getHTML()
        info_table = self.scrapp_joueur.getInfoTableJoueur()
        taille = self.scrapp_joueur.scrappTaile()
        self.assertEqual(taille, "169")

    def testScrappTaille(self):
        html = self.scrapp_joueur.getHTML()
        info_table = self.scrapp_joueur.getInfoTableJoueur()
        equipementier = self.scrapp_joueur.scrappEquipementierActuel()
        self.assertEqual(equipementier, "Nike")

    def testScrappPositions(self):
        html = self.scrapp_joueur.getHTML()
        positions_principales, positions_secondaires = self.scrapp_joueur.scrappPositions()
        self.assertEqual(positions_principales, ['14'])
        self.assertEqual(positions_secondaires, ['11', '12'])

if __name__ == '__main__':
    unittest.main()
