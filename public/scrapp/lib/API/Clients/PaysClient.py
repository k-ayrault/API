from lib.configApi import *
from lib.API.ApiClient import ApiClient

from lib.Classes.Pays import Pays
from lib.Exception.PaysNotFoundException import PaysNotFoundException

import sys
import requests
from http import HTTPStatus


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
                method=METHOD_GET, url=API_URL_GET_PAYS_BY_NOM_FR, params=params)

            pays = Pays().fromJson(json=responseJson)

            return pays
        except requests.exceptions.HTTPError as httpError:
            httpStatusCode = httpError.response.status_code  # Status code de la réponse HTTP
            if httpStatusCode == HTTPStatus.NOT_FOUND:  # Si on aucun pays n'a été trouvé pour ce nom
                raise PaysNotFoundException(
                    f"Aucun pays n'a été trouvé pour le nom FR : {nomFr}")
            else:  # Si une erreur s'est produite
                sys.exit(httpError)

    def postPays(self, pays: Pays):
        params = pays.toJson(schema="persist.Pays")

        try:
            responseJson = self.exec(
                method=METHOD_POST, url=API_URL_PAYS, params=params)

        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    def patchPays(self, pays: Pays, schema: str):
        params = pays.toJson(schema=schema)
        url = f"{API_URL_PAYS}/{pays.code}"

        try:
            responseJson = self.exec(
                method=METHOD_PATCH, url=url, params=params)
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)
