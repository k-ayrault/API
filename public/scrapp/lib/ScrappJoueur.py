from lib.API.ApiClient import ApiClient

from lib.Classes.Joueur import Joueur

from lib.Exception.JoueurNotFoundException import JoueurNotFoundException

from lib.ScrappJoueurInfoPerso import ScrappJoueurInfoPerso

from bs4 import BeautifulSoup
import requests
from scrapp_func_global import *


class ScrappJoueur:  

    def __init__(self, idTransferMarkt: int, lienJoueurTransferMarkt: str):

        self.api = ApiClient()
        
        try :
            self.joueur = self.api.getJoueurByIdTransferMarkt(idTransfermarkt=idTransferMarkt)
        except JoueurNotFoundException as joueurNotFundException:
            self.joueur = Joueur()

        # Id TransferMarkt du joueur que l'on scrapp
        self.idTransferMarkt = idTransferMarkt
        # Lien TransferMarkt du joueur que l'on scrapp
        self.lienTransferMarkt = lienJoueurTransferMarkt.replace(
            transfermarkt_url_replace, transfermarkt_info_joueur)
        
        # HTML de la page TransferMarkt du joueur que l'on scrapp
        self.htmlTransferMarkt = None

        # Date de fin du contrat actuel du joueur
        self.dateFinContratActuel = None

        self.getHTML()

        self.scrappInfoPerso = ScrappJoueurInfoPerso(htmlTransferMarkt=self.htmlTransferMarkt, idTransferMarkt=self.idTransferMarkt, idInfoPerso=self.joueur.informationsPersonelles.id, api=self.api)


    """
        Fonction qui récupère l'HTML de la page TransferMarkt du joueur et le BeautifulSoup
        Entrée :
        Sortie :
            - self.htmlTransferMarkt, objet BeautifulSoup de la page du joueur
    """
    def getHTML(self):
        try:
            # Requête HTTP vers la page du joueur afin d'avoir le code HTML de cette dernière
            resultHttp = requests.get(
                self.lienTransferMarkt, headers=headers)

            # Si la requête s'est passé correctement, on récupère l'objet BeautifulSoup de l'HTML de la page sinon on lève une exception
            if resultHttp.ok:
                self.htmlTransferMarkt = BeautifulSoup(
                    resultHttp.text, "html.parser")
                return self.htmlTransferMarkt
            else:
                raise Exception(resultHttp.status_code)
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de l'HTML du joueur TransferMarkt n°{self.idTransferMarkt} : {exception}  ")
            return None

    def scrapp(self):
        infoPerso = self.scrappInfoPerso.scrapp()

        postesJoueur = self.scrappInfoPerso.scrappPostesJoueur()

        # TODO : Scrapp contrats

        if self.joueur.id : # Si le joueur a déjà un id => vient de l'api => existe dans la base
            # Si des informations sont différentes
            if self.joueur.informationsPersonelles().toJson() != infoPerso.toJson():
                # TODO : Créer une informations perso temp et la sauvegarder en base
                pass

            # TODO : Vérif si les postes sont différents et agir en conséquence
        else : # Sauvegarde du joueur
            self.joueur.informationsPersonelles = infoPerso
            # TODO : Post joueur et récupérer le retour (notamment les ids)
