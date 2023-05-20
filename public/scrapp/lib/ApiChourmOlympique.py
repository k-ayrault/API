from lib.Exception.JoueurNotFoundException import JoueurNotFoundException
from lib.config_api import *
import requests
from http import HTTPStatus
import sys


class ApiChourmOlympique:
    token = None

    def __init__(self):
        self.auth()

    def auth(self):
        params = {
            "username": API_LOGIN,
            "password": API_PASSWD
        }
        try:
            responseJson = self.exec(method=METHOD_POST, url=API_URL_LOGIN, params=params)
        except Exception as exception:
            sys.exit(exception)

        self.token = responseJson["token"]

        return self.token

    def getJoueurByIdTransferMarkt(self, idTransfermarkt: int):
        params = {
            "id_transfermarkt": idTransfermarkt
        }
        # On essaye de récupérer le joueur
        try:
            # Si on a trouvé un joueur pour cet ID TransferMarkt, et qu'il n'y a pas eu d'erreur on retourne le joueur
            responseJson = self.exec(method=METHOD_GET, url=API_URL_GET_JOUEUR_BY_ID_TM, params=params)
            return responseJson
        except requests.exceptions.HTTPError as httpError:
            httpStatusCode = httpError.response.status_code # Status code de la réponse HTTP
            if httpStatusCode == HTTPStatus.NOT_FOUND: # Si on aucun joueur n'a été trouvé pour cet ID TransferMarkt
                raise JoueurNotFoundException(
                    f"Aucun joueur n'a été trouvé pour l'ID TransferMarkt {idTransfermarkt} !")
            else: # Si une erreur s'est produite
                sys.exit(httpError)

    def exec(self, method: str, url: str, params: dict):
        header = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if self.token is not None:
            header["Authorization"] = f"Bearer {self.token}"

        if method == METHOD_GET:
            response = requests.get(headers=header, url=url, params=params)
        elif method == METHOD_POST:
            response = requests.post(headers=header, url=url, json=params)
        elif method == METHOD_PUT:
            pass
        else:
            raise Exception(f"La méthode communiqué {method} n'est pas prise en compte !")

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise Exception(f"La requête `{method}` vers l'URL `{url}` a rencontré une erreur : `{err}`")

        responseJson = response.json()

        return responseJson
