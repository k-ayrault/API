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
            nom_complet = ""
            # Récupération de "noeud" contenant le texte correspondant au label du nom complet afin de récupérer son span
            label_nom_complet = self.transfermarkt_info_table_joueur.find(
                string=re.compile(transfermarkt_nom_joueur_find))

            if label_nom_complet is not None:
                # Récupération du span contenant le label afin de récupérer le prochain span qui contient le nom complet
                span_label_nom_complet = label_nom_complet.find_parent("span")
                # Récupération du span contenant le nom complet
                span_nom_complet = span_label_nom_complet.find_next_sibling(
                    "span")
                # Récupération du texte du span, donc le nom complet
                nom_complet = span_nom_complet.text.strip()

                return nom_complet
            else:
                raise Exception(
                    f"Le label '{transfermarkt_nom_joueur_find}' est introuvable dans la table d'info")
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
            # Récupération de "noeud" contenant le texte correspondant au label de la date de naissance afin de récupérer son span
            span_label_naissance = self.transfermarkt_info_table_joueur.find(string=re.compile(
                transfermarkt_naissance_joueur_find))

            if span_label_naissance is not None:

                # Récupération du span contenant le label afin de récupérer le prochain span qui contient la date de naissance
                span_label_naissance = span_label_naissance.find_parent(
                    "span")
                # Récupération du span contenant la date de naissance
                span_naissance = span_label_naissance.find_next_sibling(
                    "span")
                # Récupération du texte du span, donc la date de naissance
                text_naissance = span_naissance.text.strip()
                # Transformation du texte correspondant à la date de naissance en datetime puis date
                date_naissance = datetime.strptime(
                    text_naissance, '%d %b %Y').date()
                # Récupération de la date de naissance au format ISO8601
                date_iso_naissance = date_naissance.isoformat()

                return date_iso_naissance
            else:
                raise Exception(
                    f"Le label '{transfermarkt_naissance_joueur_find}' est introuvable dans la table d'info")
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
            # Récupération du "noeud" contenant le texte correspondant au label des nationnalités du joueur afin de récupérer son span
            label_nationalite = self.transfermarkt_info_table_joueur.find(
                string=re.compile(transfermarkt_nationalite_joueur_find))

            if label_nationalite is not None:
                # Récupération du span contenant le label afin de récupérer le prochain span contenant les nationalités du joueur
                span_label_nationalite = label_nationalite.find_parent("span")
                # Récupération du span contenant les nationalités
                span_nationalite = span_label_nationalite.find_next_sibling(
                    "span")
                # Récupération des images contenus dans ce span afin de récupérer les logos des pays et ainsi récupérer le nom de ces derniers dans leur span
                for img in span_nationalite.findAll("img"):
                    # Récupération du nom du pays
                    nom_pays = img["alt"]
                    # Filtrage du nom du pays, afin de le renommer selon certains cas spécifiques
                    nationalite = triNation(nom_pays)

                    nationalites.append(nationalite)

                return nationalites
            else:
                raise Exception(
                    f"Le label '{transfermarkt_nationalite_joueur_find}' est introuvable dans la table d'info")
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
            # Récupération de "noeud" contenant le texte correspondant au label du pied fort afin de récupérer son span
            label_pied_fort = self.transfermarkt_info_table_joueur.find(
                string=re.compile(transfermarkt_pied_joueur_find))
            
            if label_pied_fort is not None:
                # Récupération du span contenant le label afin de récupérer le prochain span qui contient le pied fort 
                span_label_pied_fort = label_pied_fort.find_parent("span")
                # Récupération du span contenant le pied fort
                span_pied_fort = span_label_pied_fort.find_next_sibling("span")
                # Récupération du texte du span, donc le pied fort
                pied_fort = span_pied_fort.text.strip()

                return pied_fort
            else:
                raise Exception(
                    f"Le label '{transfermarkt_pied_joueur_find}' est introuvable dans la table d'info")

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
            # Récupération du "noeud" contenant le texte correspondant au label de la taille afin de récupérer son span
            label_taille = self.transfermarkt_info_table_joueur.find(string=re.compile(transfermarkt_taille_joueur_find))
            if label_taille is not None :
                # Récupération du span contenant le label afin de récupérer le prochain span qui contien la taille
                span_label_taille = label_taille.find_parent("span")
                # Récupération du span contenant la taille
                span_taille = span_label_taille.find_next_sibling("span")
                # Récupération du texte du span, donc la taille
                taille_texte = span_taille.text.strip()
                # Ne récupère que les chiffres pour avoir le nombre de centimètre du joueur (son corp ^^)
                taille = re.sub('\D', '', taille_texte)

                return taille
            else:
                raise Exception(
                    f"Le label '{transfermarkt_taille_joueur_find}' est introuvable dans la table d'info")
        except Exception as exception:
            logging.error(
                f"[ERROR] Un problème a été rencontré lors de la récupération de la taille du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
            return None