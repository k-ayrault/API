from lib.Classes.InformationsPersonelles import InformationsPersonelles
from lib.Classes.InformationsPersonellesTemp import InformationsPersonellesTemp
from lib.Classes.Pays import Pays
from lib.Classes.Poste import Poste
from lib.Exception.JoueurNotFoundException import JoueurNotFoundException
from lib.Exception.PaysNotFoundException import PaysNotFoundException
from lib.Exception.PosteNotFoundException import PosteNotFoundException
from lib.configApi import *
import requests
from http import HTTPStatus
import sys
from lib.Classes.Joueur import Joueur


class ApiClient:

    def __init__(self):
        self.token = None
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

            joueur = Joueur().fromJson(json=responseJson)

            return joueur
        except requests.exceptions.HTTPError as httpError:
            httpStatusCode = httpError.response.status_code  # Status code de la réponse HTTP
            if httpStatusCode == HTTPStatus.NOT_FOUND:  # Si on aucun joueur n'a été trouvé pour cet ID TransferMarkt
                raise JoueurNotFoundException(
            f"Aucun joueur n'a été trouvé pour l'ID TransferMarkt {idTransfermarkt} !")
            else:  # Si une erreur s'est produite
                sys.exit(httpError)

    def patchInformationsPersonelles(self, informationsPersonelles:InformationsPersonelles):
        params = informationsPersonelles.toJson(schema='persist.InformationsPersonelles')
        url = f"{API_URL_INFORMATIONS_PERSONELLES}/{informationsPersonelles.id}"

        try :
            responseJson = self.exec(method=METHOD_PATCH, url=url, params=params)
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    def postInformationsPersonellesTemp(self, informationsPersonellesTemp:InformationsPersonellesTemp):
        params = informationsPersonellesTemp.toJson(schema='persist.InformationsPersonellesTemp')
        url = f"{API_URL_INFORMATIONS_PERSONELLES_TEMP}"

        try:
            responseJson = self.exec(method=METHOD_POST, url=url, params=params)
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    def getPaysByNomFr(self, nomFr: str):
        params = {
            "nom_fr": nomFr
        }

        try:
            responseJson = self.exec(method=METHOD_GET, url=API_URL_GET_PAYS_BY_NOM_FR, params=params)

            pays = Pays().fromJson(json=responseJson)

            return pays
        except requests.exceptions.HTTPError as httpError:
            httpStatusCode = httpError.response.status_code # Status code de la réponse HTTP
            if httpStatusCode == HTTPStatus.NOT_FOUND: # Si on aucun pays n'a été trouvé pour ce nom
                raise PaysNotFoundException(f"Aucun pays n'a été trouvé pour le nom FR : {nomFr}")
            else: # Si une erreur s'est produite
                sys.exit(httpError)

    def postPays(self, pays: Pays):
        params = pays.toJson(schema="persist.Pays")

        try:
            responseJson = self.exec(method=METHOD_POST, url=API_URL_PAYS, params=params)

            
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    def patchPays(self, pays: Pays, schema: str):
        params = pays.toJson(schema=schema)
        url = f"{API_URL_PAYS}/{pays.code}"

        try:
            responseJson = self.exec(method=METHOD_PATCH, url=url, params=params)
        except requests.exceptions.HTTPError as httpError:
            sys.exit(httpError)

    def getPosteByIdTransfermarkt(self, idTransfermarkt:int):
        params = {
            "id_transfermarkt": idTransfermarkt
        }
        # On essaye de récupérer le joueur
        try:
            # Si on a trouvé un joueur pour cet ID TransferMarkt, et qu'il n'y a pas eu d'erreur on retourne le joueur
            responseJson = self.exec(method=METHOD_GET, url=API_URL_GET_POSTE_BY_ID_TM, params=params)

            poste = Poste().fromJson(json=responseJson)

            return poste
        except requests.exceptions.HTTPError as httpError:
            httpStatusCode = httpError.response.status_code  # Status code de la réponse HTTP
            if httpStatusCode == HTTPStatus.NOT_FOUND:  # Si on aucun joueur n'a été trouvé pour cet ID TransferMarkt
                raise PosteNotFoundException(
                    f"Aucun poste n'a été trouvé pour l'ID TransferMarkt {idTransfermarkt} !")
            else:  # Si une erreur s'est produite
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
        elif method == METHOD_PATCH:
            header["Content-Type"] = "application/merge-patch+json"
            response = requests.patch(headers=header, url=url, json=params)
        elif method == METHOD_PUT:
            pass
        else:
            raise Exception(f"La méthode communiqué {method} n'est pas prise en compte !")


        response.raise_for_status()

        responseJson = response.json()

        return responseJson

    def logout(self):
        del self.token