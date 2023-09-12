from lib.configApi import *
from lib.API.ApiClient import ApiClient

from lib.Classes.Club import Club
from lib.Exception.ClubNotFoundException import ClubNotFoundException

import sys
import requests
from http import HTTPStatus
import json

#   TODO : add tests
class ClubClient(ApiClient):

    def __init__(self):
        super().__init__()

    """
        Fonction permettant de les informations d'un club via son id transfermarkt
        Entrée :
            - idTransferMarkt : Id TransferMarkt du club
        Sortie : 
            - Club : Club contenant les infos récupérées
        Raise :
            - ClubNotFoundException : Si la liste des clubs récupérés est vide, donc qu'aucun club n'a été trouvé pour cet id tm
    """
    def getClubByIdTransferMarkt(self, idTransferMarkt: int):
        params = {
            "id_transfermarkt": idTransferMarkt
        }

        try:
            responseJson = self.exec(
                method=METHOD_GET, url=API_URL_GET_CLUB, params=params)

            if len(responseJson) == 0:
                raise ClubNotFoundException(f"Aucun club n'a été trouvé pour l'ID TransferMarkt {idTransferMarkt} !")

            club = Club().fromJson(json=responseJson[0])

            return club
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    """
        Fonction permettant de savoir si un club est déjà présent dans la base pour cet id transfermarkt
        Entrée :
            - idTransferMarkt : Id TransferMarkt du club
        Sortie : 
            - bool : True si existe déjà, False sinon
    """
    def checkIfClubWithIdTransferMarktExist(self, idTransferMarkt: int):
        params = {
            "id_transfermarkt": idTransferMarkt
        }

        try:
            responseJson = self.exec(
                method=METHOD_GET, url=API_URL_GET_CLUB, params=params)

            if len(responseJson) == 1:
                return True
            else:
                return False
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)
