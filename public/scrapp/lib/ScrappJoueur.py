from lib.ApiChourmOlympique import ApiChourmOlympique

from lib.Classes.Joueur import Joueur

from lib.Exception.JoueurNotFoundException import JoueurNotFoundException

from lib.ScrappJoueurInfoPerso import ScrappJoueurInfoPerso

from scrapp_func_global import *


class ScrappJoueur:

    # Id TransferMarkt du joueur que l'on scrapp
    idJoueurTransferMarkt = -1

    # Lien TransferMarkt du joueur que l'on scrapp
    lienJoueurTransferMarkt = ""

    # HTML de la page TransferMarkt du joueur que l'on scrapp
    htmlTransferMarktJoueur = None

    # Date de fin du contrat actuel du joueur
    dateFinContratActuel = None

    api = ApiChourmOlympique()

    joueur = None

    scrappInfoPerso = None

    def __init__(self, idJoueurTransferMarkt: int, lienJoueurTransferMarkt: str):
        try :
            self.joueur = self.api.getJoueurByIdTransferMarkt(idTransfermarkt=idJoueurTransferMarkt)
        except JoueurNotFoundException as joueurNotFundException:
            self.joueur = Joueur()

        self.idJoueurTransferMarkt = idJoueurTransferMarkt
        self.lienJoueurTransferMarkt = lienJoueurTransferMarkt.replace(
            transfermarkt_url_replace, transfermarkt_info_joueur)

        self.getHTML()
        self.scrappInfoPerso = ScrappJoueurInfoPerso(html=self.htmlTransferMarktJoueur, idJoueurTransferMarkt=self.idJoueurTransferMarkt, idInfoPerso=self.joueur.informationsPersonelles.id, api=self.api)


    """
        Fonction qui récupère l'HTML de la page TransferMarkt du joueur et le BeautifulSoup
        Entrée :
        Sortie :
            - self.htmlTransferMarktJoueur, objet BeautifulSoup de la page du joueur
    """
    def getHTML(self):
        try:
            # Requête HTTP vers la page du joueur afin d'avoir le code HTML de cette dernière
            resultHttp = requests.get(
                self.lienJoueurTransferMarkt, headers=headers)

            # Si la requête s'est passé correctement, on récupère l'objet BeautifulSoup de l'HTML de la page sinon on lève une exception
            if resultHttp.ok:
                self.htmlTransferMarktJoueur = BeautifulSoup(
                    resultHttp.text, "html.parser")
                return self.htmlTransferMarktJoueur
            else:
                raise Exception(resultHttp.status_code)
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de l'HTML du joueur TransferMarkt n°{self.idJoueurTransferMarkt} : {exception}  ")
            return None

    def scrapp(self):
        infoPerso = self.scrappInfoPerso.scrapp()

        if self.joueur.id : # Si le joueur a déjà un id => vient de l'api => existe dans la base
            # Si des informations sont différentes
            if self.joueur.informationsPersonelles().toJson() != self.informationsPersonelles.toJson():
                # TODO : Créer une informations perso temp et la sauvegarder en base
                pass
        else : # Sauvegarde du joueur
            self.joueur.informationsPersonelles = infoPerso

        postesJoueur = self.scrappInfoPerso.scrappPostesJoueur()