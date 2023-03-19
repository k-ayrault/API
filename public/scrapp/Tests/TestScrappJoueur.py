import unittest
from ScrappJoueur import ScrappJoueur
from scrapp_func_global import transfermarkt_url_replace
from bs4 import BeautifulSoup

class TestScrappJoueur(unittest.TestCase):
    
    def setUp(self):
        self.id_joueur_transfermarkt = "40433"
        self.lien_joueur_transfermarkt = f"https://www.transfermarkt.fr/alexis-sanchez/{transfermarkt_url_replace}/spieler/40433"

        self.scrapp_joueur = ScrappJoueur(id_joueur_transfermarkt=self.id_joueur_transfermarkt, lien_joueur_transfermarkt=self.lien_joueur_transfermarkt)

    def testGetHTMLSuccessfull(self):
        html = self.scrapp_joueur.getHTML()
        self.assertIsInstance(html, BeautifulSoup)
    
    

if __name__ == '__main__':
    unittest.main()