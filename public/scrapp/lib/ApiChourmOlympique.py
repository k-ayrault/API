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
        try :
            responseJson = self.exec(method=METHOD_POST, url=API_URL_LOGIN, params=params)
        except Exception as exception :
            sys.exit(exception)
        self.token = responseJson["token"]

        return self.token
    
    def exec(self, method: str, url:str, params:list) : 
        header = {}

        if self.token is not None :
            header["Authorization"] = f"Bearer {self.token}"

        if method == METHOD_GET :
            response = requests.get(headers=header, url=url, params=params)
        elif method == METHOD_POST :
            response = requests.post(headers=header, url=url, json=params)
        elif method == METHOD_PUT :
                pass
        else :
            raise Exception(f"La méthode communiqué {method} n'est pas prise en compte !")
        
        try :
            response.raise_for_status()
        except requests.exceptions.HTTPError as err :
            raise Exception(f"La requête `{method}` vers l'URL `{url}` a rencontré une erreur : `{err}`")
        
        responseJson = response.json()
    
        return responseJson