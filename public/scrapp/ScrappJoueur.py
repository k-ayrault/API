from scrapp_func_global import *

class ScrappJoueur:
    
    # Id TransferMarkt du joueur que l'on scrapp 
    id_joueur_transfermarkt  = -1

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
        self.lien_joueur_transfermarkt = lien_joueur_transfermarkt.replace(transfermarkt_url_replace, transfermarkt_info_joueur)

    """
        Fonction qui récupère l'HTML de la page TransferMarkt du joueur et le BeautifulSoup
        Entrée :
        Sortie :
            - self.transfermarkt_html_joueur, objet BeautifulSoup de la page du joueur
    """
    def getHTML(self):
        try:
            # Requête HTTP vers la page du joueur afin d'avoir le code HTML de cette dernière
            result_http = requests.get(self.lien_joueur_transfermarkt, headers=headers)

            # Si la requête s'est passé correctement, on récupère l'objet BeautifulSoup de l'HTML de la page sinon on lève une exception
            if result_http.ok:
                self.transfermarkt_html_joueur = BeautifulSoup(result_http.text, "html.parser")
                return self.transfermarkt_html_joueur
            else: 
                raise Exception(result_http.status_code)
        except Exception as exception:
            logging.error(f"[ERROR] Un problème a été rencontré lors de la récupération de l'HTML du joueur TransferMarkt n°{self.id_joueur_transfermarkt} : {exception}  ")
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
            self.transfermarkt_header_joueur = self.transfermarkt_html_joueur.find("main").find("header", {"class": "data-header"})
            
            return self.transfermarkt_header_joueur
        except Exception as exception:
            logging.error(f"[ERROR] Un problème a été rencontré lors de la récupération du header sur la page du joueur TransferMarkt n°{self.id_joueur_transfermarkt} : {exception}  ")
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
            body = self.transfermarkt_html_joueur.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
            # Récupération du tableau contenant les informations personnelles du joueur
            self.transfermarkt_info_table_joueur = body.find("div", {"class": "info-table"})

            return self.transfermarkt_info_table_joueur
        except Exception as exception:
            logging.error(f"[ERROR] Un problème a été rencontré lors de la récupération de la 'table' contenant les infos du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
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
            logging.error(f"[ERROR] Un problème a été rencontré lors de la récupération du nom et prénom du joueur {self.id_joueur_transfermarkt} sur sa page TransferMarkt : {exception}  ")
            return None