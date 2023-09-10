import unittest
from lib.ScrappStade import ScrappStade
from lib.configScrapp import *
from bs4 import BeautifulSoup


class TestScrappClub(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.idClubTransfermarkt = "244"
        cls.lienClubTransfermarkt = f"https://www.transfermarkt.fr/olympique-de-marseille/{TM_URL_REPLACE}/verein/244"

        cls.scrappStade = ScrappStade(
            lienTransferMarkt=cls.lienClubTransfermarkt)

    def testGetHTMLSuccessfull(self):
        html = self.scrappStade.getHTML()
        self.assertIsInstance(html, BeautifulSoup)

    def testGetBoxInfo(self):
        boxInfo = self.scrappStade.getBoxInfo()
        self.assertIsNotNone(boxInfo)

    def testScrappNomClub(self):
        nomStade = self.scrappStade.scrappNomStade()

        self.assertEqual(nomStade, 'Orange Vélodrome')

    def testScrappCapaciteClub(self):
        capaciteStade = self.scrappStade.scrappCapaciteStade()

        self.assertEqual(capaciteStade, 67394)

    def testScrappDateConstructionStade(self):
        dateConstruction = self.scrappStade.scrappDateConstructionStade()

        self.assertEqual(dateConstruction, 1937)

    def testScrappImagesStade(self):
        images = self.scrappStade.scrappImagesStade()
        imgs = [
            'https://tmssl.akamaized.net/images/foto/stadionmedium/olympique-marseille-choreo-1585320589-35026.jpg?lm=1585320610',
            'https://tmssl.akamaized.net/images/foto/stadionmedium/stade-velodrome-1464625458-9357.jpg?lm=1491209195',
            'https://tmssl.akamaized.net/images/foto/stadionmedium/stade-velodrome-1464625436-9356.jpg?lm=1491209195'
        ]
        self.assertEqual(len(images), len(imgs))

        for image in images:
            self.assertTrue(image.lien in imgs)

    def testScrappAdresseStade(self):
        adresseStade = self.scrappStade.scrappAdresseStade()

        self.assertEqual(adresseStade, 'Orange Vélodrome, 3 Boulevard Michelet, 13008 Marseille, France')


if __name__ == '__main__':
    unittest.main()
