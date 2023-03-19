from scrapp_func_global import *

"""
    Fonction permettant de récupérer le nom et le prénom du joueur 
    Entrée : 
        - header, objet BeautifulSoup contenant le header où on peut récupérer le nom et prénom
    Sortie :
        - nom, nom du joueur
        - prenom, prénom du joueur
"""
def getNomPrenom(header):
    nom, prenom = "", ""
    # Récupération du "titre" du nom/prénom du joueur
    h1_name_joueur = header.find(
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


"""
    Fonction permettant de récupérer le nom complet du joueur (utile pour les sudaméricains notamment)
    Entrée :
        - info_table, table html où sont stockées les informations du joueurs
    Sortie :
        - nom_complet, nom complet du joueur
"""
def getNomComplet(info_table):
    nom_complet = ""
    label_nom_complet = info_table.find(
        text=re.compile(transfermarkt_nom_joueur_find))
    if label_nom_complet is not None:
        span_nom_complet = label_nom_complet.find_parent().find_next_sibling()
        nom_complet = span_nom_complet.text

    return nom_complet    

