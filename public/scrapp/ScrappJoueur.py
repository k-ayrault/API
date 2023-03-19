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
        except Exception as excepetion:
            logging.error(f"[ERROR] Un problème a été rencontré lors de la récupération de l'HTML du joueur TransferMarkt n°{self.id_joueur_transfermarkt} : {excepetion}  ")
            

