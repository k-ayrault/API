from lib.ApiChourmOlympique import ApiChourmOlympique
from lib.Classes.Joueur import Joueur
from lib.Classes.PosteJoueur import PosteJoueur
from lib.Exception.PaysNotFoundException import PaysNotFoundException
from scrapp_func_global import *
from lib.Exception.JoueurNotFoundException import JoueurNotFoundException

class ScrappJoueur:

    # Id TransferMarkt du joueur que l'on scrapp
    idJoueurTransferMarkt = -1

    # Lien TransferMarkt du joueur que l'on scrapp
    lienJoueurTransferMarkt = ""

    # HTML de la page TransferMarkt du joueur que l'on scrapp
    htmlTransferMarktJoueur = None

    # Header de la page du joueur
    headerTransferMarktJoueur = None

    # Table HTML où sont stockée les informations "personnelles" du joueur
    infoTableTransferMarktJoueur = None

    # Date de fin du contrat actuel du joueur
    dateFinContratActuel = None

    api = ApiChourmOlympique()

    joueur = None

    def __init__(self, idJoueurTransferMarkt: int, lienJoueurTransferMarkt: str):
        try :
            self.joueur = self.api.getJoueurByIdTransferMarkt(idTransfermarkt=idJoueurTransferMarkt)
        except JoueurNotFoundException as joueurNotFundException:
            self.joueur = Joueur()
        self.idJoueurTransferMarkt = idJoueurTransferMarkt
        self.lienJoueurTransferMarkt = lienJoueurTransferMarkt.replace(
            transfermarkt_url_replace, transfermarkt_info_joueur)

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

    """
        Fonction qui récupère le header du joueur sur sa page TransferMarkt où est notamment son nom et son prénom "différenciés".
        Entrée:
        Sortie:
            - self.headerTransferMarktJoueur, header du joueur si correctement récupéré sinon None
    """
    def getHeaderInfoJoueur(self):
        try:
            # Récupération de la div contenant ces infos
            self.headerTransferMarktJoueur = self.htmlTransferMarktJoueur.find(
                "main").find("header", {"class": "data-header"})

            return self.headerTransferMarktJoueur
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération du header sur la page du joueur TransferMarkt n°{self.idJoueurTransferMarkt} : {exception}  ")
            return None

    """
        Fonction qui récupère la "table" contenant les informations personnelles du joueur sur sa page TransferMarkt
        Entrée :
        Sortie :
            - self.infoTableTransferMarktJoueur, la "table" si correctement récupéré sinon None
    """
    def getInfoTableJoueur(self):
        try:
            # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
            body = self.htmlTransferMarktJoueur.find(
                "div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
            # Récupération du tableau contenant les informations personnelles du joueur
            self.infoTableTransferMarktJoueur = body.find(
                "div", {"class": "info-table"})

            return self.infoTableTransferMarktJoueur
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la 'table' contenant les infos du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère le span contenant la valeur correspondant au label en entrée
        Entrée : 
            - labelText, texte du "label" correspondant à la valeur que l'on souhaite récupérer
        Sortie :
            - span, le span contenant la valeur correspondant au label en entrée 
                sinon lève une exception
    """
    def getSpanValeurDansInfoTableViaLabel(self, labelText):
        # Récupération du "noeud" contenant le texte correspondant au label afin de récupérer son span
        label = self.infoTableTransferMarktJoueur.find(string=re.compile(labelText))
        if label is not None :
            # Récupération du span contenant le label afin de récupérer le prochain span qui contient la valeur recherché
            spanLabel = label.find_parent("span")
            # Récupération du span contenant la valeur recherché
            span = spanLabel.find_next_sibling("span")

            return span
        else:
            raise Exception(
                f"Le label '{labelText}' est introuvable dans la table d'info")
        
    """
        Fonction qui récupère le nom et le prénom du joueur via le header de sa page TransferMarkt
        Entrée : 
        Sortie :
            - nom, Nom du joueur
            - prenom, Prénom du joueur
            - ou None si la récupération ne s'est pas passé comme prévu
    """
    def scrappNomEtPrenom(self):
        try:
            nom, prenom = "", ""
            # Récupération du "titre" du nom/prénom du joueur
            h1NomJoueur = self.headerTransferMarktJoueur.find(
                "div", {"class": "data-header__headline-container"}).find("h1")
            # Suppression du numéro du joueur dans ce titre
            spanNumeroJoueur = h1NomJoueur.find(
                "span", {"class": "data-header__shirt-number"})
            if spanNumeroJoueur is not None:
                spanNumeroJoueur.decompose()
            # Récupération du nom du joueur présent dans la balise <strong>
            nom = h1NomJoueur.find("strong").text
            # Suppression du nom dans le titre afin de n'avoir plus que le prénom
            h1NomJoueur.find("strong").decompose()
            # Récupération du prénom qui est présent dans le reste du titre
            prenom = h1NomJoueur.text.strip()

            self.joueur.informationsPersonelles.nom = nom
            self.joueur.informationsPersonelles.prenom = prenom

            return nom, prenom
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération du nom et prénom du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère le nom complet dans la table contenant les informations personnelles du joueur sur sa page TransferMarkt
        Entrée :
        Sortie :
        - nomComplet, Nom complet du joueur si la récupération s'est déroulé correctement
        sinon None
        """
    def scrappNomComplet(self):
        try:
            # Récupération du span contenant le nom complet du joueur
            spanNomComplet = self.getSpanValeurDansInfoTableViaLabel(labelText=TM_JOUEUR_NOM_COMPLET_LABEL_TEXT)

            # Récupération du texte du span, donc le nom complet
            nomComplet = spanNomComplet.text.strip()

            self.joueur.informationsPersonelles.nomComplet = nomComplet

            return nomComplet

        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération du nom complet du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère la date de naissance dans la table contenant les informations personelles du joueur sur sa page TransferMarkt et la renvoie au format ISO8601
        Entrée : 
        Sortie : 
        - dateIsoNaissance, date de naissance du joueur au format ISO8601
        """
    def scrappDateDeNaissance(self):
        # Récupération de la date de naissance du joueur
        try:
            # Récupération du span contenant le nom complet du joueur
            spanNaissance = self.getSpanValeurDansInfoTableViaLabel(labelText=TM_JOUEUR_NAISSANCE_LABEL_TEXT)
            # Récupération du texte du span, donc la date de naissance
            textNaissance = spanNaissance.text.strip()
            # Transformation du texte correspondant à la date de naissance en datetime puis date
            dateNaissance = datetime.strptime(textNaissance,'%d %b %Y').date()
            # Récupération de la date de naissance au format ISO8601
            dateIsoNaissance = dateNaissance.isoformat()

            self.joueur.informationsPersonelles.dateNaissance = dateIsoNaissance

            return dateIsoNaissance

        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la date de naissance du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère la/les nationalité(s) dans la table contenant les informations personelles du joueur sur sa page TransferMarkt
        Entrée :
        Sortie :
        - nationalites, tableau contenant les différentes nationalités du joueur avec le nom des pays respectifs
        """
    def scrappNationalites(self):
        # Récupération des nationalités du joueur
        nationalites = []
        try:

            # Récupération du span contenant les nationalités
            spanNationalite = self.getSpanValeurDansInfoTableViaLabel(labelText=TM_JOUEUR_NATIONALITES_LABEL_TEXT)

            # Récupération des images contenus dans ce span afin de récupérer les logos des pays et ainsi récupérer le nom de ces derniers dans leur span
            for imgNationalite in spanNationalite.findAll("img"):
                nationalite = ""
                # Récupération du nom du pays
                nomPays = imgNationalite["alt"]
                # Filtrage du nom du pays, afin de le renommer selon certains cas spécifiques
                nationalite = triNation(nomPays)

                # TODO : Test la modification et modifier le test correspondant
                if nationalite :
                    try:
                        pays = self.api.getPaysByNomFr(nomFr=nationalite)
                        self.joueur.informationsPersonelles.nationalites.append(pays)
                    except PaysNotFoundException as paysNotFoundException:
                        logging.error(f"[ERROR] Aucun pays n'a été trouvé via l'API pour le nom : {nationalite}")

                return self.joueur.informationsPersonelles.nationalites
        
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de(s) nationalite(s) du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère le pied fort dans la table contenant les informations personelles du joueur sur sa page TransferMarkt
        Entrée :
        Sortie :
            - piedFort, pied fort du joueur si la récupération s'est déroulé correctement 
                sinon None
    """
    def scrappPiedFort(self):
        try:
            # Récupération du span contenant le pied fort 
            spanPiedFort = self.getSpanValeurDansInfoTableViaLabel(labelText=TM_JOUEUR_PIED_FORT_LABEL_TEXT)

            # Récupération du texte du span, donc le pied fort
            piedFort = spanPiedFort.text.strip()

            self.joueur.informationsPersonelles.meilleurPied = piedFort

            return piedFort
        
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération du pied fort du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère la taille dans la table contenant les informations personnelles du joueur sur sa page TransferMarkt
        Entrée :
        Sortie :
            - taille, taille du joueur si la récupération s'est déroulé correctement
                sinon None
    """
    def scrappTaile(self):
        try:
            # Récupération du span contenant la taille 
            spanTaille = self.getSpanValeurDansInfoTableViaLabel(labelText=TM_JOUEUR_TAILLE_LABEL_TEXT)

            # Récupération du texte du span, donc la taille
            tailleText = spanTaille.text.strip()
            # Ne récupère que les chiffres pour avoir le nombre de centimètre du joueur (son corp ^^)
            taille = re.sub('\D', '', tailleText)

            self.joueur.informationsPersonelles.taille = taille

            return taille
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la taille du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None
    
    """
        Fonction qui récupère la taille dans la table contenant les informations personnelles du joueur sur sa page TransferMarkt
        Entrée :
        Sortie : 
            - equipementier, l'équipementier actuel du joueur si la récupération s'est déroulé correctement
                sinon None
    """
    def scrappEquipementierActuel(self):
        try:
            # Récupération du span contenant l'équipementier
            spanEquipementier = self.getSpanValeurDansInfoTableViaLabel(labelText=TM_JOUEUR_EQUIPEMENTIER_LABEL_TEXT)
            # Récupération du texte du span, donc de l'équipementier
            equipementier = spanEquipementier.text.strip()

            self.joueur.informationsPersonelles.equipementier = equipementier

            return equipementier
        except Exception as exception :
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de l'équipementier du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère la/les position(s) principale(s) et secondaire(s) du joueur sur sa page TransferMarkt
        Entrée :
        Sortie : 
            - positionsPrincipales, tableau avec les identifiants TransferMarkt des positions principales du joueur
            - positionsSecondaires, tableau avec les identifiants TransferMarkt des positions secondaires du joueur
            Tout cela si la récupération se passe bien, sinon None 
    """
    def scrappPositions(self):
        try :
            # Récupération de la div contenant les différentes positions du joueur (point sur le terrain)
            boxPositions = self.htmlTransferMarktJoueur.find("div", {"class": "detail-position__matchfield"})


            spanPositions = boxPositions.findAll("span", { "class" : "position" })

            for spanPosition in spanPositions :
                posteJoueur = PosteJoueur()

                # On récupère le type de la position que l'on traite
                if "position__primary" in spanPosition["class"] : # Position principale
                    classTypePosition = "position__primary"
                elif "position__secondary" in spanPosition["class"] : # Position secondaire
                    classTypePosition = "position__secondary"
                else : 
                    continue

                # Création du début de la class contenant l'identifiant de la position
                debutClassPosition = classTypePosition + "--"
                
                # Récupération de la class contenant l'identifiant de la position
                classPosition = [
                    class_type for class_type in spanPosition["class"]
                    if debutClassPosition in class_type
                ]
                # Si plus d'une class est retourné pour la class contenant l'identifiant de la position on passe à la prochaine position car pas normal
                if len(classPosition) != 1 :
                    continue
                classPosition = classPosition[0]
                
                # Récupération de l'identifiant de la position en supprimant le début de la class
                position = classPosition.replace(debutClassPosition, "")

                poste = self.api.getPosteByIdTransfermarkt(idTransfermarkt=position)
                posteJoueur.poste = poste

                # Ajout de la position dans le bon tableau
                if classTypePosition == "position__primary" :
                    posteJoueur.principale = True
                elif classTypePosition == "position__secondary" :
                    posteJoueur.principale = False

                self.joueur.postes.append(posteJoueur)
            
            return self.joueur.postes

        except Exception as exception :
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération des postes du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère la date de fin du contrat actuel du joueur dans la table contenant les informations personnelles du joueur sur page TransferMarkt
        Entrée : 
        Sortie :
            - self.date_fin_contrat_actuel, la date de fin du contrat actuel au format ISO8601 si la récupération s'est déroulé correctement 
                sinon None
    """
    def scrappDateFinContratActuel(self):
        try:
            # Récupération du span contenant la date de fin du contrat actuel du joueur selon s'il est en prêt ou non (le label change)
            try:
                # Récupération du span contenant la date de fin du contrat actuel du joueur s'il est en prêt
                spanDateFinContratActuel = self.getSpanValeurDansInfoTableViaLabel(labelText=TM_JOUEUR_PRETE_DATE_FIN_CONTRAT_ACTUEL_LABEL_TEXT)
            except :
                # Récupération du span contenant la date de fin du contrat actuel du joueur s'il n'est pas en prêt
                spanDateFinContratActuel = self.getSpanValeurDansInfoTableViaLabel(labelText=TM_JOUEUR_DATE_FIN_CONTRAT_ACTUEL_LABEL_TEXT)
            # Récupération du texte du span, donc la date de fin du contrat
            dateFinContratActuelText = spanDateFinContratActuel.text.strip()

            # Transformation du texte correspondant à la date de fin du contrat en datetime puis date
            dateFinContratActuel = datetime.strptime(dateFinContratActuelText, '%d %b %Y').date()
            
            # Récupération de la date de fin du contrat au format ISO8601
            dateFinContratActuelIsoFormat = dateFinContratActuel.isoformat()

            self.dateFinContratActuel = dateFinContratActuelIsoFormat

            return self.dateFinContratActuel
        except Exception as exception :
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la date de fin du contrat actuel du joueur {self.idJoueurTransferMarkt} sur sa page TransferMarkt : {exception}  ")
            return None
