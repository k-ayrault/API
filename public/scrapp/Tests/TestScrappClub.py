import unittest
from lib.ScrappClub import ScrappClub
from lib.configScrapp import *
from bs4 import BeautifulSoup


class TestScrappClub(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.idClubTransfermarkt = "244"
        cls.lienClubTransfermarkt = f"https://www.transfermarkt.fr/olympique-de-marseille/{TM_URL_REPLACE}/verein/244"

        cls.scrappClub = ScrappClub(
            idTransferMarkt=cls.idClubTransfermarkt, lienTransferMarkt=cls.lienClubTransfermarkt)

    def testGetHTMLSuccessfull(self):
        html = self.scrappClub.getHTML()
        self.assertIsInstance(html, BeautifulSoup)

    def testGetBoxInfo(self):
        boxInfo = self.scrappClub.getBoxInfo()
        self.assertIsNotNone(boxInfo)

    def testScrappNomClub(self):
        nomClub = self.scrappClub.scrappNomClub()

        self.assertEqual(nomClub, 'Olympique de Marseille')
        
    def testScrappPaysClub(self):
        paysClub = self.scrappClub.scrappPaysClub()

        self.assertEqual(paysClub, 'France')

    def testScrappAdresseClub(self):
        adresseClub = self.scrappClub.scrappAdresseClub()

        self.assertEqual(adresseClub, '33 traverse de la Martine, 13012 Marseille  (Résidents: 870.731), France')

    def testScrappSiteClub(self):
        siteClub = self.scrappClub.scrappSiteClub()

        self.assertEqual(siteClub, 'https://www.om.fr')

    def testScrappDateCreationClub(self):
        dateCreationClub = self.scrappClub.scrappDateCreationClub()

        self.assertEqual(dateCreationClub, '1899-08-31')
        
    def testScrappCouleursClub(self):
        couleurs = self.scrappClub.scrappCouleursClub()

        couleursHexa = []
        for couleur in couleurs:
            couleursHexa.append(couleur.hexa)

        self.assertTrue('#FFFFFF' in couleursHexa and '#099FFF' in couleursHexa)

    def testScrappLogoPrincipalClub(self):
        logo = self.scrappClub.scrappLogoPrincipalClub()

        self.assertEqual(logo.lien, 'https://tmssl.akamaized.net/images/wappen/big/244.png?lm=1485642163')
        self.assertTrue(logo.principal)

    def testScrappLogosClub(self):
        logos = self.scrappClub.scrappLogosClub()
        imgs = [
            'https://tmssl.akamaized.net/images/wappen/medium/244_1403785698.png?lm=1403785698',
            'https://tmssl.akamaized.net/images/wappen/medium/244_1403785721.png?lm=1403785721',
            'https://tmssl.akamaized.net/images/wappen/medium/244_1403785777.png?lm=1403785777',
            'https://tmssl.akamaized.net/images/wappen/medium/244_1403785807.png?lm=1403785807',
            'https://tmssl.akamaized.net/images/wappen/medium/244_1403785829.png?lm=1403785829',
            'https://tmssl.akamaized.net/images/wappen/medium/244_1403785851.png?lm=1403785851',
            'https://tmssl.akamaized.net/images/wappen/medium/244_1403786032.png?lm=1403786032',
            'https://tmssl.akamaized.net/images/wappen/medium/244_1403786064.png?lm=1403786064'
        ]

        self.assertEqual(len(logos), len(imgs))
        
        for logo in logos:
            self.assertTrue(logo.lien in imgs and not logo.principal)

if __name__ == '__main__':
    unittest.main()
