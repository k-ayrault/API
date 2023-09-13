from bs4 import BeautifulSoup
import requests
import re
import json
import validators
from datetime import datetime

from scrapp_func_global import headers

from lib.API.Clients.ClubClient import ClubClient
from lib.API.Clients.PaysClient import PaysClient

from lib.Exception.ClubNotFoundException import ClubNotFoundException
from lib.Exception.PaysNotFoundException import PaysNotFoundException

from lib.configScrapp import *
from lib.ScrappStade import ScrappStade
from lib.Classes.Pays import Pays
from lib.Classes.Club import Club
from lib.Classes.CouleurClub import CouleurClub
from lib.Classes.LogoClub import LogoClub


class ScrappClub:

    def __init__(self, idTransferMarkt: int, lienTransferMarkt: str) -> None:
        # Id TransferMarkt que l'on scrapp
        self.idTransferMarkt = idTransferMarkt
        # Club que l'on scrapp
        self.club = Club()
        # Classe de scrapp d'un stade
        self.scrappStade = ScrappStade(lienTransferMarkt=lienTransferMarkt)
        # HTML de la page TransferMarkt du club que l'on scrapp
        self.htmlTransferMarkt = None
        # Div contenant les infos du club
        self.boxInfo = None

        self.clubClient = ClubClient()

        self.lienTransferMarkt = lienTransferMarkt.replace(
            TM_URL_REPLACE, TM_URL_INFO_CLUB)
        
        self.getHTML()
        
        self.getBoxInfo()

    """
        Fonction qui récupère l'HTML de la page TransferMarkt du club et le BeautifulSoup
        Entrée :
        Sortie :
            - self.htmlTransferMarkt, objet BeautifulSoup de la page du club
    """

    def getHTML(self):
        try:
            # Requête HTTP vers la page du club afin d'avoir le code HTML de cette dernière
            resultHttpClub = requests.get(
                self.lienTransferMarkt, headers=headers)

            # Si la requête s'est passé correctement, on récupère l'objet BeautifulSoup de l'HTML de la page sinon on lève une exception
            if resultHttpClub.ok:
                self.htmlTransferMarkt = BeautifulSoup(
                    resultHttpClub.text, "html.parser")
                return self.htmlTransferMarkt
            else:
                raise Exception(resultHttpClub.status_code)
        except Exception as exception:
            print(
                f"Un problème a été rencontré lors de la récupération de l'HTML du club TransferMarkt n°{self.idTransferMarkt} ({self.lienTransferMarkt}) : {exception}  ")

        return None

    """
        Fonction permettant de récupérer la zone contenant les informations du club
        Entrée :
        Sortie :
            - self.boxInfo : zone contenant les infos
    """

    def getBoxInfo(self):
        try:
            # Récupération du bandeau bleu de navigation du club
            subnavi = self.htmlTransferMarkt.find("div", {"id": "subnavi"})

            # Récupération de la div contenant toutes les informations que l'on souhaite
            row = subnavi.find_next_sibling("div", {"class": "row"})

            # Récupération de la div contenant les informations du club
            h2BoxInfo = row.find("h2", text=re.compile(
                TM_BOX_INFO_CLUB))

            self.boxInfo = h2BoxInfo.find_parent(
                "div", {"class": "box"}).find("div", {"class": "content"})

            return self.boxInfo

        except Exception as e:
            print(
                f"Une erreur est survenu lors de la récupération de la section contenant les informations du club : {e} !")
        return None

    """
        Fonction récupérant le nom du club
        Entrée :
        Sortie :
            - self.club.nom : Nom du club
    """

    def scrappNomClub(self) -> str:
        try:
            # Récupération de la ligne contenant le nom du club
            ligneNomClub = self.boxInfo.find("th", text=re.compile(
                TM_BOX_INFO_NOM_CLUB)).find_parent("tr")
            # Récupération du nom du club
            self.club.nom = ligneNomClub.find("td").text.strip()

            return self.club.nom
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération nom du club n°{self.idTransferMarkt} ({self.lienTransferMarkt}) : {e} !")

        return None

    """
        Fonction permettant de récupérer l'adresse du club
        Entrée :
        Sortie :
            - self.club.adresse : Adresse du club
    """

    def scrappAdresseClub(self) -> str:
        try:
            adresse = ""
            # Récupération de la ligne où l'adresse du club est
            ligneAdresse = self.boxInfo.find("th",
                                             text=re.compile(TM_BOX_INFO_ADRESSE_CLUB)).find_parent("tr")
            adresse += ligneAdresse.find("td").text.strip() + ", "
            adresse += ligneAdresse.find_next_sibling().find("td").text.strip() + ", "
            adresse += ligneAdresse.find_next_sibling().find_next_sibling().find("td").text.strip()

            self.club.adresse = adresse.strip()

            return self.club.adresse

        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération de l'adresse du club n°{self.idTransferMarkt} ({self.lienTransferMarkt}) : {e} !")
        return None

    """
        TODO : lier avec l'api pour récupérer le pays adéquat (modifier le test correspondant au passage)
        Fonction permettant de récupérer le pays du club
        Entrée :
        Sortie :
            - self.club.pays : Pays du club
    """

    def scrappPaysClub(self) -> str:
        try:
            paysClient = PaysClient()
            # Récupération de la ligne où l'adresse du club est
            ligneAdresse = self.boxInfo.find("th",
                                             text=re.compile(TM_BOX_INFO_ADRESSE_CLUB)).find_parent("tr")
           # Récupération de la ligne où le pays est, en déduisant qu'il s'agit de la troisième ligne de l'adresse donc deux tr plus loin que le premier de l'adresse
            ligne_pays_club = ligneAdresse.find_next_sibling().find_next_sibling()

            nomFrPays = ligne_pays_club.find("td").text.strip()
            pays = None
            try : 
                pays = paysClient.getPaysByNomFr(nomFr=nomFrPays)
            except PaysNotFoundException as paysNotFound :
                pays = Pays()
                print(f"[ERROR] Aucun pays n'a été trouvé via l'API pour le nom : {nomFrPays}")

            self.club.pays = pays

        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération du pays du club n°{self.idTransferMarkt} ({self.lienTransferMarkt}) : {e} !")
            
        return self.club.pays

    """
        Fonction récupérant le lien vers le site du club
        Entrée :
        Sortie :
            - self.club.siteWeb : Site web du club
    """

    def scrappSiteClub(self) -> str:
        try:
            # Récupération de la ligne où est présent le site du club
            ligneSite = self.boxInfo.find("th",
                                          text=re.compile(TM_BOX_INFO_SITE_CLUB)).find_parent("tr")
            # Récupération du lien vers le site du club
            site = ligneSite.find("a")["href"]

            self.club.siteWeb = site if validators.url(site) else None

            return self.club.siteWeb
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération du site du club n°{self.idTransferMarkt} ({self.lienTransferMarkt}) : {e} !")

        return None

    """
        Fonction récupérant la date de création du club
        Entrée :
        Sortie :
            - self.club.dateCreation : Date de création du club
    """

    def scrappDateCreationClub(self) -> str:
        try:
            # Récupération de la ligne contenant la date de création du club
            ligneDateCreation = self.boxInfo.find("th",
                                                  text=re.compile(TM_BOX_INFO_CREATION_CLUB)).find_parent("tr")
            # Récupération de la chaîne de caractère de la création du club
            dateCreationStr = ligneDateCreation.find("td").text.strip()
            # Format de la date de création
            formatDatetimeStr = "%d %b %Y"
            # Création de la datetime correspondant à la date de création du club
            datetimeCreation = datetime.strptime(
                dateCreationStr.strip(), formatDatetimeStr)
            # Date de la création du club au format ISO 8601
            isoDateCreation = datetimeCreation.date().isoformat()

            self.club.dateCreation = isoDateCreation

            return self.club.dateCreation
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération de la date de création du club n°{self.idTransferMarkt} ({self.lienTransferMarkt}) : {e} !")

    """
        Fonction permettant de récupérer les couleurs du club 
        Entrée : 
        Sortie :
            - self.club.couleurs : Couleurs du club
    """
    def scrappCouleursClub(self) -> list:
        try:
            self.club.couleurs = []
            # Récupération de la ligne contenant les couleurs du clubs
            ligneCouleurs = self.boxInfo.find("th", text=re.compile(
                TM_BOX_INFO_COULEURS_CLUB)).find_parent("tr")
            # Récupération des "blocs" ayant comme background-color, les couleurs du clubs
            blocsCouleurs = ligneCouleurs.find("td").find("p").find_all("span")

            # Traitement de chaque bloc pour récupérer la couleur du club
            for couleur in blocsCouleurs:
                couleurClub = CouleurClub()
                # Récupération de l'index où est normalement la couleur
                indexCouleurStyle = (
                    re.search("background-color:", couleur["style"])).end()
                # Récupération de la couleur du bloc
                couleurClub.hexa = couleur["style"][indexCouleurStyle:-1]
                # On ajoute la couleur à celles du club si cette dernière existe
                if couleurClub.hexa != '':
                    self.club.couleurs.append(couleurClub)

            return self.club.couleurs
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération des couleurs du club n°{self.idTransferMarkt} ({self.lienTransferMarkt}) : {e} !")

        return []

    """
        Fonction permettant de récupérer le logo principal du club
        Entrée : 
        Sortie :
            - logo : Logo principal du club
    """
    def scrappLogoPrincipalClub(self) -> LogoClub:
        try:
            logo = LogoClub()
            # Récupération de la div contenant l'image
            divLogo = self.boxInfo.find("div", {"class": "datenfakten-wappen"})
            # Récupération du logo
            logo.lien = divLogo.find("img")["src"]
            logo.principal = True
            # Vérification que l'url vers le logo est valide
            if validators.url(logo.lien):
                self.club.logos.append(logo)

            return logo
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération du logo principal du club n°{self.idTransferMarkt} ({self.lienTransferMarkt}) : {e} !")

        return None
    
    """
        Fonction permettant de récupérer tous les logos qu'à pu avoir le club
        Entrée : 
        Sortie :
            - self.club.logos : Les logos du club
    """
    def scrappLogosClub(self) -> list:
        try:
            # Récupération du titre indiquant les anciens logos
            h2OldLogos = self.htmlTransferMarkt.find(
                "h2", text=re.compile(TM_BOX_INFO_LOGOS_CLUB))
            # Récupération du bloc contenant les anciens logos
            blocOldLogos = h2OldLogos.find_parent(
                "div", {"class": "box"})
            # Récupération de tous les anciens logos
            logos = blocOldLogos.findAll("img")
            # Vérificatiopn de la validité des logos
            for logo in logos:
                    logoClub = LogoClub()
                    lienLogo = logo["src"]
                    # Vérification que src soit bien un lien afin de ne pas récupérer uniquement un chemin sur un serv par ex.
                    if validators.url(lienLogo):
                        logoClub.lien = lienLogo 
                        self.club.logos.append(logoClub)

            return self.club.logos
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération des logos du club n°{self.idTransferMarkt} ({self.lienTransferMarkt}) : {e} !")

        return []

    def scrapp(self) -> Club:
        # On récupère le club s'il existe via l'id TransferMarkt, sinon on le scrapp
        try :
            self.club = self.clubClient.getClubByIdTransferMarkt(self.idTransferMarkt)
            
            return self.club
        except ClubNotFoundException as clubNotFound :
            self.club = Club()
            self.club.idTransferMarkt = self.idTransferMarkt

        self.scrappNomClub()
        self.scrappAdresseClub()
        self.scrappPaysClub()
        self.scrappSiteClub()
        self.scrappDateCreationClub()
        self.scrappCouleursClub()
        self.scrappLogoPrincipalClub()
        self.scrappLogosClub()
        self.club.stade = self.scrappStade.scrapp()
        self.club.stade.pays = self.club.pays

        self.club = self.clubClient.postClub(self.club)

        return self.club
