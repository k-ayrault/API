from lib.configApi import *
from lib.API.ApiClient import ApiClient

from lib.Classes.Pays import Pays
from lib.Exception.PaysNotFoundException import PaysNotFoundException

import sys
import requests
from http import HTTPStatus
import json


class PaysClient(ApiClient):

    def __init__(self):
        super().__init__()

    """
        Fonction permettant de les informations d'un pays via son nom français
        Entrée :
            - nomFr : Nom français du pays
        Sortie : 
            - Pays : Pays contenant les infos récupérées
        Raise :
            - PaysNotFoundException : Si aucun pays correspondant à ce nom
    """

    def getPaysByNomFr(self, nomFr: str):
        params = {
            "nom_fr": nomFr
        }

        try:
            responseJson = self.exec(
                method=METHOD_GET, url=API_URL_GET_PAYS, params=params)

            if responseJson['hydra:totalItems'] == 1:
                pays = Pays().fromJson(json=responseJson['hydra:member'][0])

                return pays
            else:
                raise PaysNotFoundException(
                    f"Aucun pays unique correspondant pour le nom FR : {nomFr}")
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    def postPays(self, pays: Pays):
        params = pays.toJson(schema="persist.Pays")

        try:
            responseJson = self.exec(
                method=METHOD_POST, url=API_URL_POST_PAYS, params=params)

        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    def patchPays(self, pays: Pays, schema: str):
        params = pays.toJson(schema=schema)
        url = f"{API_URL_PATCH_PAYS}/{pays.code}"

        try:
            responseJson = self.exec(
                method=METHOD_PATCH, url=url, params=params)
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)
