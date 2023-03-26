from scrapp_func_global import *


class ScrappJoueur:

    # Id TransferMarkt du joueur que l'on scrapp
    id_joueur_transfermarkt = -1

    # Lien TransferMarkt du joueur que l'on scrapp
    lien_joueur_transfermarkt = ""

    # HTML de la page TransferMarkt du joueur que l'on scrapp
    transfermarkt_html_joueur = None

    # Header de la page du joueur
    transfermarkt_header_joueur = None

    # Table HTML où sont stockée les informations "personnelles" du joueur
    transfermarkt_info_table_joueur = None

    # Date de fin du contrat actuel du joueur
    date_fin_contrat_actuel = None

    def __init__(self, id_joueur_transfermarkt, lien_joueur_transfermarkt):
        self.id_joueur_transfermarkt = id_joueur_transfermarkt
        self.lien_joueur_transfermarkt = lien_joueur_transfermarkt.replace(
            transfermarkt_url_replace, transfermarkt_info_joueur)

    """
        Fonction qui récupère l'HTML de la page TransferMarkt du joueur et le BeautifulSoup
        Entrée :
        Sortie :
            - self.transfermarkt_html_joueur, objet BeautifulSoup de la page du joueur
    """
    def getHTML(self):
        try:
            # Requête HTTP vers la page du joueur afin d'avoir le code HTML de cette dernière
            result_http = requests.get(
                self.lien_joueur_transfermarkt, headers=headers)

            # Si la requête s'est passé correctement, on récupère l'objet BeautifulSoup de l'HTML de la page sinon on lève une exception
            if result_http.ok:
                self.transfermarkt_html_joueur = BeautifulSoup(
                    result_http.text, "html.parser")
                return self.transfermarkt_html_joueur
            else:
                raise Exception(result_http.status_code)
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de l'HTML du joueur TransferMarkt n°{self.id_joueur_transfermarkt} : {exception}  ")
            return None

    """
        Fonction qui récupère le header du joueur sur sa page TransferMarkt où est notamment son nom et son prénom "différenciés".
        Entrée:
        Sortie:
            - self.transfermarkt_header_joueur, header du joueur si correctement récupéré sinon None
    """
    def getHeaderInfoJoueur(self):
        try:
            # Récupération de la div contenant ces infos
            self.transfermarkt_header_joueur = self.transfermarkt_html_joueur.find(
                "main").find("header", {"class": "data-header"})

            return self.transfermarkt_header_joueur
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération du header sur la page du joueur TransferMarkt n°{self.id_joueur_transfermarkt} : {exception}  ")
            return None

    """
        Fonction qui récupère la "table" contenant les informations personnelles du joueur sur sa page TransferMarkt
        Entrée :
        Sortie :
            - self.transfermarkt_info_table_joueur, la "table" si correctement récupéré sinon None
    """
    def getInfoTableJoueur(self):
        try:
            # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
            body = self.transfermarkt_html_joueur.find(
                "div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
            # Récupération du tableau contenant les informations personnelles du joueur
            self.transfermarkt_info_table_joueur = body.find(
                "div", {"class": "info-table"})

            return self.transfermarkt_info_table_joueur
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la 'table' contenant les infos du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
            return None


    """
        Fonction qui récupère le span contenant la valeur correspondant au label en entrée
        Entrée : 
            - label_text, texte du "label" correspondant à la valeur que l'on souhaite récupérer
        Sortie :
            - span, le span contenant la valeur correspondant au label en entrée 
                sinon lève une exception
    """
    def getSpanValeurDansInfoTableViaLabel(self, label_text):
        # Récupération du "noeud" contenant le texte correspondant au label afin de récupérer son span
        label = self.transfermarkt_info_table_joueur.find(string=re.compile(label_text))
        if label is not None :
            # Récupération du span contenant le label afin de récupérer le prochain span qui contient la valeur recherché
            span_label = label.find_parent("span")
            # Récupération du span contenant la valeur recherché
            span = span_label.find_next_sibling("span")

            return span
        else:
            raise Exception(
                f"Le label '{label_text}' est introuvable dans la table d'info")
        

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
            h1_name_joueur = self.transfermarkt_header_joueur.find(
                "div", {"class": "data-header__headline-container"}).find("h1")
            # Suppression du numéro du joueur dans ce titre
            span_numero_joueur = h1_name_joueur.find(
                "span", {"class": "data-header__shirt-number"})
            if span_numero_joueur is not None:
                span_numero_joueur.decompose()
            # Récupération du nom du joueur présent dans la balise <strong>
            nom = h1_name_joueur.find("strong").text
            # Suppression du nom dans le titre afin de n'avoir plus que le prénom
            h1_name_joueur.find("strong").decompose()
            # Récupération du prénom qui est présent dans le reste du titre
            prenom = h1_name_joueur.text.strip()

            return nom, prenom
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération du nom et prénom du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère le nom complet dans la table contenant les informations personnelles du joueur sur sa page TransferMarkt
        Entrée :
        Sortie :
            - nom_complet, Nom complet du joueur si la récupération s'est déroulé correctement
                sinon None
    """
    def scrappNomComplet(self):
        try:
            # Récupération du span contenant le nom complet du joueur
            span_nom_complet = self.getSpanValeurDansInfoTableViaLabel(transfermarkt_nom_joueur_find)
            
            # Récupération du texte du span, donc le nom complet
            nom_complet = span_nom_complet.text.strip()

            return nom_complet
            
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération du nom complet du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère la date de naissance dans la table contenant les informations personelles du joueur sur sa page TransferMarkt et la renvoie au format ISO8601
        Entrée : 
        Sortie : 
            - date_iso_naissance, date de naissance du joueur au format ISO8601
    """
    def scrappDateDeNaissance(self):
        # Récupération de la date de naissance du joueur
        try:
            # Récupération du span contenant le nom complet du joueur
            span_naissance = self.getSpanValeurDansInfoTableViaLabel(transfermarkt_naissance_joueur_find)
            # Récupération du texte du span, donc la date de naissance
            text_naissance = span_naissance.text.strip()
            # Transformation du texte correspondant à la date de naissance en datetime puis date
            date_naissance = datetime.strptime(text_naissance, '%d %b %Y').date()
            # Récupération de la date de naissance au format ISO8601
            date_iso_naissance = date_naissance.isoformat()
            
            return date_iso_naissance
        
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la date de naissance du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
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
            span_nationalite = self.getSpanValeurDansInfoTableViaLabel(transfermarkt_nationalite_joueur_find)

            # Récupération des images contenus dans ce span afin de récupérer les logos des pays et ainsi récupérer le nom de ces derniers dans leur span
            for img in span_nationalite.findAll("img"):
                nationalite = ""
                # Récupération du nom du pays
                nom_pays = img["alt"]
                # Filtrage du nom du pays, afin de le renommer selon certains cas spécifiques
                nationalite = triNation(nom_pays)

                if nationalite :
                    nationalites.append(nationalite)    

            return nationalites
        
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de(s) nationalite(s) du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère le pied fort dans la table contenant les informations personelles du joueur sur sa page TransferMarkt
        Entrée :
        Sortie :
            - pied_fort, pied fort du joueur si la récupération s'est déroulé correctement 
                sinon None
    """
    def scrappPiedFort(self):
        try:
            # Récupération du span contenant le pied fort 
            span_pied_fort = self.getSpanValeurDansInfoTableViaLabel(transfermarkt_pied_joueur_find)

            # Récupération du texte du span, donc le pied fort
            pied_fort = span_pied_fort.text.strip()

            return pied_fort
        
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération du pied fort du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
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
            span_taille = self.getSpanValeurDansInfoTableViaLabel(transfermarkt_taille_joueur_find)

            # Récupération du texte du span, donc la taille
            taille_texte = span_taille.text.strip()
            # Ne récupère que les chiffres pour avoir le nombre de centimètre du joueur (son corp ^^)
            taille = re.sub('\D', '', taille_texte)

            return taille
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la taille du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
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
            span_equipementier = self.getSpanValeurDansInfoTableViaLabel(transfermarkt_equipementier_joueur_find)
            # Récupération du texte du span, donc de l'équipementier
            equipementier = span_equipementier.text.strip()

            return equipementier
        except Exception as exception :
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de l'équipementier du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
            return None

    """
        Fonction qui récupère la/les position(s) principale(s) et secondaire(s) du joueur sur sa page TransferMarkt
        Entrée :
        Sortie : 
            - positions_principales, tableau avec les identifiants TransferMarkt des positions principales du joueur
            - positions_secondaires, tableau avec les identifiants TransferMarkt des positions secondaires du joueur
            Tout cela si la récupération se passe bien, sinon None 
    """
    def scrappPositions(self):
        positions_principales = []
        positions_secondaires = []
        try :
            # Récupération de la div contenant les différentes positions du joueur (point sur le terrain)
            box_positions = self.transfermarkt_html_joueur.find("div", {"class": "detail-position__matchfield"})


            span_positions = box_positions.findAll("span", { "class" : "position" })

            for span_position in span_positions :
                # On récupère le type de la position que l'on traite
                if "position__primary" in span_position["class"] : # Position principale
                    class_type_position = "position__primary"
                elif "position__secondary" in span_position["class"] : # Position secondaire
                    class_type_position = "position__secondary"
                else : 
                    continue

                # Création du début de la class contenant l'identifiant de la position
                debut_class_position = class_type_position + "--"
                
                # Récupération de la class contenant l'identifiant de la position
                class_position = [
                    class_type for class_type in span_position["class"]
                    if debut_class_position in class_type
                ]
                # Si plus d'une class est retourné pour la class contenant l'identifiant de la position on passe à la prochaine position car pas normal
                if len(class_position) != 1 :
                    continue
                class_position = class_position[0]
                
                # Récupération de l'identifiant de la position en supprimant le début de la class
                position = class_position.replace(debut_class_position, "")

                # Ajout de la position dans le bon tableau
                if class_type_position == "position__primary" :
                    positions_principales.append(position)
                elif class_type_position == "position__secondary" :
                    positions_secondaires.append(position)
            
            return positions_principales, positions_secondaires

        except Exception as exception :
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération des postes du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
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
                span_date_fin_contrat_actuel = self.getSpanValeurDansInfoTableViaLabel(label_text=transfermarkt_fin_contrat_pret_find)
            except :
                # Récupération du span contenant la date de fin du contrat actuel du joueur s'il n'est pas en prêt
                span_date_fin_contrat_actuel = self.getSpanValeurDansInfoTableViaLabel(label_text=transfermarkt_fin_contrat_find)
            # Récupération du texte du span, donc la date de fin du contrat
            date_fin_contrat_actuel_text = span_date_fin_contrat_actuel.text.strip()

            # Transformation du texte correspondant à la date de fin du contrat en datetime puis date
            date_fin_contrat_actuel = datetime.strptime(date_fin_contrat_actuel_text, '%d %b %Y').date()
            
            # Récupération de la date de fin du contrat au format ISO8601
            date_fin_contrat_actuel_iso_format = date_fin_contrat_actuel.isoformat()

            self.date_fin_contrat_actuel = date_fin_contrat_actuel_iso_format

            return self.date_fin_contrat_actuel
        except Exception as exception :
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la date de fin du contrat actuel du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
            return None
