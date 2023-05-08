import unittest
from lib.ApiChourmOlympique import ApiChourmOlympique

class TestApiChourmOlympique(unittest.TestCase):

    def setUp(self):
        self.api = ApiChourmOlympique()

    def testAuth(self):
        self.assertIsNotNone(self.api.token)