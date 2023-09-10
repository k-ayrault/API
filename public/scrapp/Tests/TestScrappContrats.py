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

    def testScrappDateFromLigne(self):
        self.scrappContrats.currentLigne = self.scrappContrats.lignesTransferts[0]
        date = self.scrappContrats.scrappDateFromLigne()

        self.assertEqual(date, '2005-03-01')

    def testScrappNomClubFromLigne(self):
        self.scrappContrats.currentLigne = self.scrappContrats.lignesTransferts[1]
        nomClub = self.scrappContrats.scrappNomClubLigne(depart=False)
        
        self.assertEqual(nomClub, 'Udinese')

    def testScrappMontantFromLigne(self):
        self.scrappContrats.currentLigne = self.scrappContrats.lignesTransferts[1]
        montant = self.scrappContrats.scrappMontantLigne()
        
        self.assertEqual(montant, '3,00 mio. €')

    def testScrappPret(self):        
        self.scrappContrats.indexCurrentLigne = 2
        self.scrappContrats.currentLigne = self.scrappContrats.lignesTransferts[self.scrappContrats.indexCurrentLigne]
        pret = self.scrappContrats.scrappContratPret()
        
        self.assertEqual(pret.debut, '2006-07-11')
        self.assertEqual(pret.fin, '2007-06-30')
        self.assertEqual(pret.club.nom, 'Colo Colo')
        

if __name__ == '__main__':
    unittest.main()
