from lib.configApi import *
from lib.API.ApiClient import ApiClient

from lib.Classes.Stade import Stade
from lib.Exception.StadeNotFoundException import StadeNotFoundException

import sys
import requests
import json

#   TODO : add tests

class StadeClient(ApiClient):

    def __init__(self):
        super().__init__()

    """
        Fonction permettant récupérer de les informations d'un stade via son nom et sa date de construction
        Entrée :
            - nom : nom du stade du stade
            - construction : date de construction du stade
        Sortie : 
            - Stade : Stade contenant les infos récupérées
        Raise :
            - StadeNotFoundException : Si la liste des stade récupérés est vide, donc qu'aucun stade n'a été trouvé pour les infos données
    """

    def getStadeByNomAndConstruction(self, nom: str, construction:int):
        params = {
            "nom": nom,
            "construction": construction
        }

        try:
            responseJson = self.exec(
                method=METHOD_GET, url=API_URL_GET_STADE, params=params)

            if responseJson['hydra:totalItems'] == 1:
                stade = Stade().fromJson(json=responseJson['hydra:member'][0])

                return stade
            else:
                raise StadeNotFoundException(
                    f"Aucun stade n'a été trouvé pour {nom} {construction} !")

        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    """
        Fonction permettant de savoir si un stade est déjà présent dans la base pour cet id transfermarkt
        Entrée :
            - nom : Nom du stade
            - construction : Date de construction du stade
        Sortie : 
            - bool : True si existe déjà, False sinon
    """

    def checkIfStadeByNomAndConstructionExist(self, nom:str, construction: int):
        params = {
            "nom": nom,
            "construction": construction
        }

        try:
            responseJson = self.exec(
                method=METHOD_GET, url=API_URL_GET_STADE, params=params)

            if responseJson['hydra:totalItems'] == 1:
                return True
            else:
                return False
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    def postStade(self, stade: Stade):
        params = stade.toJson(schema="persist.Stade")

        try:
            responseJson = self.exec(
                method=METHOD_POST, url=API_URL_POST_STADE, params=params)

            return Stade().fromJson(json=responseJson)

        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)
