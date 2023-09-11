from lib.configScrapp import *

from lib.ScrappClub import ScrappClub
from lib.Classes.Pret import Pret
from lib.Classes.Transfert import Transfert
from lib.Classes.Club import Club

import re
from datetime import datetime


class ScrappContrats:

    def __init__(self, idJoueurTransferMarkt: int, htmlTransferMarkt) -> None:
        # Id TransferMarkt du joueur
        self.idTransferMarkt = idJoueurTransferMarkt
        # HTML de la page TransferMarkt du joueur que l'on scrapp
        self.htmlTransferMarkt = htmlTransferMarkt
        # Tableau allant contenir les différents contrats/transferts du joueur
        self.contrats = []
        # Tableau allant contenir les différentes lignes correspondants aux différents transferts du joueru
        self.lignesTransferts = []
        # Va contenir l'HTML de la ligne que l'on traite à l'instant t
        self.currentLigne = ""
        # Va contenir l'index de la ligne que l'on traite à l'instant t dans le tableau self.lignesTransferts
        self.indexCurrentLigne = -1

        self.getTableauTransfert()
        self.getLignesTransferts()

    """
        Fonction permettant de récupérer le tableau récapitulatif des transferts du joueur
        Entrée:
        Sortie:
            - self.tableauTransferts : html correspondant aux différents transfert du joueur
    """

    def getTableauTransfert(self):
        try:
            # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
            row = self.htmlTransferMarkt.find("div", {"id": "subnavi"}).find_next_sibling(
                "div", {"class": "row"})
            # Récupération du tableau contenant les différents transferts du joueur
            titreTableauTransferts = row.find(
                "h2", string=re.compile(TM_HISTORIQUE_TRANSFERT_FIND))

            self.tableauTransferts = titreTableauTransferts.find_parent()

        except Exception as e:
            print(f"Une erreur est survenu lors de la récupération du tableau de récapitulatif des transferts du joueur : !")

        return self.tableauTransferts

    """
        Fonction permettant de récupérer uniquement les lignes correspondant à un transfert² dans le tableau de récapitulatif
        ² : Il peut contenir des lignes qui ne sont pas des transferts (par exemple passage des u19 à la 2 et de la 2 aux pros)
        Entrée:
        Sortie:
            - self.lignesTransferts : Tableau contenant les lignes des différents transferts du joueur dans l'ordre ASC
    """

    def getLignesTransferts(self):
        try:
            # Récupération des lignes du tableau correspondant à un 'transfert' (une seule classe)
            lignes = self.tableauTransferts.findAll(
                "div", {"class": TM_CLASS_TRANSFERT_LIGNE})

            lignes = [ligne for ligne in lignes if len(ligne["class"]) == 2]
            # Inverse le tableau afin d'avoir les contrats dans un ordre croissant de date
            lignes = lignes[::-1]

            self.lignesTransferts = lignes

        except Exception as e:
            print(f"Une erreur est survenu lors de la récupération des lignes de transferts dans le tableau de récapitulatif des transferts du joueur : !")

        return self.lignesTransferts

    """
        Fonction permettant de récupérer la date de la ligne que l'on traite actuellement, currentLigne, et de la transformer en format ISO
        Entrée:
        Sortie:
            - date : date du transfert de la ligne sous format iso
    """

    def scrappDateFromLigne(self):
        date = ""
        if not self.currentLigne:
            print("Current ligne pas initialisé")
            return date
        try:
            date_transfert = self.currentLigne.find(
                "div", {"class": TM_CLASS_TRANSFERT_LIGNE_DATE})
            date_transfert = date_transfert.text.strip()
            date_transfert = datetime.strptime(date_transfert, "%d %b %Y")
            date = date_transfert.date().isoformat()
        except Exception as e:
            print(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la date d'un transfert : {e} !")

        return date

    """
        Fonction permettant de récupérer la chaine de caractère du nom du club (départ ou arrivé en fonction de depart en entrée)
        Entrée : 
            - depart :  boolean indiquant si on veut le club de départ (true) ou d'arrivée (false)
        Sortie : 
            - nomClub : chaine de caractère correspondant au nom du club
    """

    def scrappNomClubLigne(self, depart=True) -> str:

        if not self.currentLigne:
            return False

        classDiv = ""
        if depart:
            classDiv = TM_CLASS_TRANSFERT_LIGNE_CLUB_DEPART
        else:
            classDiv = TM_CLASS_TRANSFERT_LIGNE_CLUB_ARRIVEE
        divClub = self.currentLigne.find("div", {"class": classDiv})
        if divClub is not None:
            return divClub.text.strip()

        return False

    """
        TODO : Modifier avec l'ajout ScrappClub quand opérationnelle
        Fonction permettant de récupérer les informations du club dont le joueur part, de la ligne que l'on traite actuellement, currentLigne.
        Entrée : 
            - depart : boolean indiquant si on veut le club de départ (true) ou d'arrivée (false)
    """

    def scrappClubLigne(self, depart):
        if not self.currentLigne:
            print("Current ligne pas initialisé")
            return club
        try:
            classDiv = ""
            if depart:
                classDiv = TM_CLASS_TRANSFERT_LIGNE_CLUB_DEPART
            else:
                classDiv = TM_CLASS_TRANSFERT_LIGNE_CLUB_ARRIVEE
            divClub = self.currentLigne.find("div", {"class": classDiv})

            idClub = -1
            nomClub = ""
            lienClub = ""
            if divClub is not None:
                nomClub = divClub.text.strip()
            if nomClub != TM_LIBELLE_FIN_CARRIERE and nomClub != TM_LIBELLE_PAUSE_CARRIERE and nomClub != "":
                lienClub = divClub.find("a")
                if lienClub is not None:
                    lienClub = lienClub["href"]
                    lienClub = lienClub[:lienClub.find("/saison_id/")]
                    match = (re.search("/verein/", lienClub))
                    idClub = lienClub[match.end():]
                    lienClub = TM_URL + lienClub.replace(
                        TM_URL_TRANSFERTS, TM_URL_REPLACE)
                    scrappClub = ScrappClub(idTransferMarkt=idClub, lienTransferMarkt=lienClub)
                    club = scrappClub.scrapp()
                    del scrappClub

                    return club
        except Exception as e:
            print(
                f"[ERROR] Un problème a été rencontré lors de la récupération d'un club partant d'un transfert : {e} !")

        return None

    """
        Fonction permettant de récupérer le montant du transfert ou action (Tr. Libre, Prêt, etc.)
        Entrée:
        Sortie: 
            - montant : valeur dans la colonne montant du transfert
    """

    def scrappMontantLigne(self):
        montant = 0
        if not self.currentLigne:
            print("Current ligne pas initialisé")
            return montant
        try:
            montantTransfert = self.currentLigne.find(
                "div", {"class": TM_CLASS_TRANSFERT_LIGNE_MONTANT})
            if montantTransfert is not None:
                montant = montantTransfert.text.strip()
        except Exception as e:
            print(
                f"[ERROR] Un problème a été rencontré lors de la récupération du montant d'un transfert : {e} !")
        return montant

    """
        TODO : Scrapp montant du prêt 
        Fonction permettant de récupérer les informations d'un Pret
        Entrée : 
        Sortie : 
            -   pret : Pret contenant les infos de ce dernier
    """

    def scrappContratPret(self):
        pret = Pret()
        pret.debut = self.scrappDateFromLigne()
        pret.club = self.scrappClubLigne(depart=False)
        #   Index de la ligne indiquant le début du prêt
        indexLigneStartPret = self.indexCurrentLigne
        #   On boucle le tableau contenant les lignes des transferts à partir du début du prêt pour récupérer la ligne contenant la fin du prêt
        while self.indexCurrentLigne < len(self.lignesTransferts) - 1:
            self.indexCurrentLigne += 1
            self.currentLigne = self.lignesTransferts[self.indexCurrentLigne]
            montantTransfert = self.scrappMontantLigne()
            clubDepart = self.scrappClubLigne(depart=True)
            clubArrivee = self.scrappClubLigne(depart=False)
            if montantTransfert == TM_LIBELLE_FIN_DE_PRET and clubDepart != clubArrivee:
                pret.fin = self.scrappDateFromLigne()
                #   On supprime la ligne afin de ne pas à réavoir à faire un traitement dessus
                del self.lignesTransferts[self.indexCurrentLigne]
                # On réinitialise la ligne que l'on traite à celui du début du prêt
                self.indexCurrentLigne = indexLigneStartPret
                self.currentLigne = self.lignesTransferts[self.indexCurrentLigne]
                break

        self.contrats.append(pret)
        return pret

    """
        Fonction permettant de parcourir le tableau des transferts du joueur et d'en extraire ces différents transferts/contrats
        Entrée :
        Sortie : 
            - self.contrats : tableau contenant les Contrats (Transfert et Pret) du joueur
    """

    def scrappContrats(self):
        transfert = Transfert()
        while self.indexCurrentLigne < len(self.lignesTransferts) - 1:
            #   Initialisation de la ligne que l'on traite
            self.indexCurrentLigne += 1
            self.currentLigne = self.lignesTransferts[self.indexCurrentLigne]

            #   Récupération de la chaine de caractère correspondant au montant du transfert
            montantTransfert = self.scrappMontantLigne()

            #   S'il s'agit du début d'un prêt
            if re.search("prêt", montantTransfert, re.IGNORECASE) and montantTransfert != TM_LIBELLE_FIN_DE_PRET:
                self.scrappContratPret()
            else:  # S'il s'agit d'un transfert 'basique'
                dateLigne = self.scrappDateFromLigne()
                montantTransfert = self.scrappMontantLigne()
                #   S'il ne s'agit pas de la première ligne et qu'un contrat a déjà commencé à être initialisé on finalise ce contrat
                if self.indexCurrentLigne != 0 and transfert.debut is not None:
                    nomClubArrive = self.scrappNomClubLigne(depart=False)
                    #   Si aucun montant de transfert ("-") => aucun transfert => pas besoin de compléter
                    #   Cependant, il peut y avoir des pauses et des fin de carrière => besoin de compléter le contrat
                    if montantTransfert == TM_LIBELLE_PAS_DE_MOUVEMENT and nomClubArrive != TM_LIBELLE_FIN_CARRIERE and nomClubArrive != TM_LIBELLE_PAUSE_CARRIERE:
                        continue
                    #   Récupération du club de départ afin d'être quasi sûr d'avoir la plus grosse équipe du club comme club (ex: club formateur le couz' passe par u19, 2, pro)
                    transfert.club = self.scrappClubLigne(depart=True)
                    transfert.fin = dateLigne
                    #   Ajout du transfert aux contrats scrappés
                    self.contrats.append(transfert)
                    
                    #   Réinitialisation du transfert
                    transfert = Transfert()

                #   Permet d'indiquer les montants des transferts en fonction des différents cas
                if montantTransfert == TM_LIBELLE_TRANSFERT_LIBRE or self.scrappNomClubLigne(depart=True) == TM_LIBELLE_PAUSE_CARRIERE:
                    transfert.libre = True
                elif montantTransfert == TM_LIBELLE_PAS_DE_MOUVEMENT and self.indexCurrentLigne == 0:
                    transfert.club_formateur = True
                elif montantTransfert == TM_LIBELLE_PAS_DE_MOUVEMENT:
                    continue
                else:
                    transfert.montant = montantTransfert

                transfert.debut = dateLigne
                transfert.club = self.scrappClubLigne(depart=False)
        #   S'il s'agit du contrat en cours du joueur
        if transfert.debut is not None:
            #   TODO : Ajouter fin de contrat
            self.contrats.append(transfert)
        self.contrats = sorted(self.contrats, key=lambda x: x.debut)

        return self.contrats
