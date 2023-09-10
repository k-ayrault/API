from bs4 import BeautifulSoup
import requests
import unicodedata
import re
import validators

from scrapp_func_global import *

from lib.configScrapp import *
from lib.Classes.Stade import Stade
from lib.Classes.ImageStade import ImageStade


class ScrappStade:

    stade = Stade()

    # Lien TransferMarkt du stade du club que l'on scrapp
    lienTransferMarkt = ""

    # HTML de la page TransferMarkt du stade du club que l'on scrapp
    htmlTransferMarkt = None

    # Div contenant les infos du stade
    boxInfo = None

    def __init__(self, lienTransferMarkt: str) -> None:
        self.lienTransferMarkt = lienTransferMarkt.replace(
            TM_URL_REPLACE, TM_URL_INFO_STADE_CLUB)
        self.getHTML()
        self.getBoxInfo()
        pass

    """
        Fonction qui récupère l'HTML de la page TransferMarkt du stade et le BeautifulSoup
        Entrée :
        Sortie :
            - self.htmlTransferMarkt, objet BeautifulSoup de la page du club
    """

    def getHTML(self):
        try:
            # Requête HTTP vers la page du stade afin d'avoir le code HTML de cette dernière
            resultHttpStade = requests.get(
                self.lienTransferMarkt, headers=headers)

            # Si la requête s'est passé correctement, on récupère l'objet BeautifulSoup de l'HTML de la page sinon on lève une exception
            if resultHttpStade.ok:
                self.htmlTransferMarkt = BeautifulSoup(
                    resultHttpStade.text, "html.parser")
                return self.htmlTransferMarkt
            else:
                raise Exception(resultHttpStade.status_code)
        except Exception as exception:
            print(
                f"Un problème a été rencontré lors de la récupération de l'HTML du stade {self.lienTransferMarkt} : {exception}  ")

        return None

    """
        Fonction permettant de récupérer la zone contenant les informations du stade
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

            # Récupération de la div contenant les informations du stade via le nom de ce dernier
            h1BoxInfo = row.find("h2", text=re.compile(self.scrappNomStade()))
            self.boxInfo = h1BoxInfo.find_parent("div", {"class": "box"})

            return self.boxInfo

        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération de la section contenant les informations stade {self.lienTransferMarkt} : {e} !")
        return None

    """
        Fonction récupérant le nom du stade
        Entrée :
        Sortie :
            - self.stade.nom : Nom du stade
    """

    def scrappNomStade(self) -> str:
        try:
            # Récupération du bandeau bleu de navigation du club
            subnavi = self.htmlTransferMarkt.find("div", {"id": "subnavi"})

            # Récupération de la div contenant toutes les informations que l'on souhaite
            row = subnavi.find_next_sibling("div", {"class": "row"})

            # Récupération de la ligne contenant le nom du stade
            ligneNomStade = row.find("th", text=re.compile(
                TM_LIBELLE_NOM_STADE)).find_parent("tr")
            # Récupération du nom du stade
            nomStade = ligneNomStade.find("td").text.strip()

            self.stade.nom = nomStade

            return self.stade.nom

        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération nom du stade {self.lienTransferMarkt} : {e} !")

        return None

    """
        Fonction récupérant la capacité du stade
        Entrée :
        Sortie :
            - self.stade.capacite : Capacité du stade
    """

    def scrappCapaciteStade(self) -> int:
        try:
            # Récupération de la ligne correspondant à la capacité du stade
            ligneCapaciteStade = self.boxInfo.find("th", text=re.compile(
                TM_LIBELLE_CAPACITE_STADE)).find_parent("tr")
            # Récupération de la capacité du stade
            self.stade.capacite = int(
                ligneCapaciteStade.find("td").text.replace('.', ''))

            return self.stade.capacite
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération de la capacité du stade {self.lienTransferMarkt} : {e} !")
        return 0

    """
        Fonction récupérant la date de construction du stade
        Entrée :
        Sortie :
            - self.stade
    """

    def scrappDateConstructionStade(self) -> int:
        try:
            # Récupération de la ligne contenant l'année de construction du stade
            ligne_construction_stade = self.boxInfo.find("th", text=re.compile(
                TM_LIBELLE_CONSTRUCTION_STADE)).find_parent("tr")
            # Récupérationd de l'année de construction du stade
            self.stade.anneeConstruction = int(
                ligne_construction_stade.find("td").text.strip())

            return self.stade.anneeConstruction
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération de l'année de construction du stade {self.lienTransferMarkt} : {e} !")
        return -1

    """
        Fonction récupérant les images du stade
        Entrée :
        Sortie : 
            - self.stade.images : Images du stade 
    """

    def scrappImagesStade(self) -> list:
        try:
            # Récupération de toutes les images du stade
            images = self.boxInfo.findAll("img")
            # Récupération de chaque url
            for image in images:
                lienImage = image["src"]
                # Vérification que l'url vers l'image est valide
                if validators.url(lienImage):
                    imageStade = ImageStade()
                    imageStade.lien = lienImage
                    self.stade.images.append(imageStade)

            return self.stade.images
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération des images du stade {self.lienTransferMarkt} : {e} !")
        return []

    """
        Fonction récupérant l'adresse du stade
        Entrée : 
        Sortie : 
            - self.stade.adresse : Adresse du stade
    """

    def scrappAdresseStade(self) -> str:
        try:
            # Récupération du bandeau bleu de navigation du club
            subnavi = self.htmlTransferMarkt.find("div", {"id": "subnavi"})

            # Récupération de la div contenant toutes les informations que l'on souhaite
            row = subnavi.find_next_sibling("div", {"class": "row"})

            # Récupération du 'h2' de la box stockant l'adresse du stade
            h2BoxAdresse = row.find("h2", text=re.compile(
                TM_LIBELLE_BOX_ADRESSE_STADE))
            # Récupération de la box stockant l'adresse du stade
            boxAdresse = h2BoxAdresse.find_parent("div", {"class": "box"})
            # Récupération de la première ligne où est stocké l'adresse
            ligneAdresse = boxAdresse.find("th", text=re.compile(
                TM_LIBELLE_ADRESSE_STADE)).find_parent("tr")
            # Récupération du début de l'adresse
            adresse = ligneAdresse.find("td").text.strip()
            # Récupération de la prochaine ligne stockant la suite de l'adresse
            ligneAdresse = ligneAdresse.find_next_sibling("tr")
            # Récupération du texte de cette ligne correspondant à la suite de l'adresse
            thText = ligneAdresse.find("th").text
            # On complète l'adresse tant la ligne suivante existe et son texte n'est pas null
            while thText == "" and ligneAdresse is not None:
                # On ajoute le texte à l'adresse afin de compléter cette dernière
                # unidecode... afin d'éviter par exemple \xa0
                adresse += ", " + unicodedata.normalize("NFKD", ligneAdresse.find("td").text.strip())
                # Récupération de la ligne suivante
                ligneAdresse = ligneAdresse.find_next_sibling("tr")
                # Si cette ligne existe, on récupère son texte
                if ligneAdresse is not None:
                    thText = ligneAdresse.find("th").text.strip()

            self.stade.adresse = adresse

            return self.stade.adresse
        except Exception as e:
            print(
                f"Un problème est survenu lors de la récupération de l'adresse du stade {self.lienTransferMarkt} : {e} !")

        return None

    def scrapp(self) -> Stade:
        # TODO : vérifier que le stade n'est pas déjà présent en base

        self.scrappNomStade()
        self.scrappCapaciteStade()
        self.scrappDateConstructionStade()
        self.scrappImagesStade()
        self.scrappAdresseStade()

        # TODO : sauvegarder en base
        return self.stade
