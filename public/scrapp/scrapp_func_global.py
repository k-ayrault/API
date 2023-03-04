transfermarkt_base_url = 'https://www.transfermarkt.fr'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

link_classement_ligue_1 = '/ligue-1/daten/wettbewerb/FR1'

# Mots-clé dans url afin de récupérer
transfermarkt_url_replace = "{page_transfermarkt}"
transfermarkt_accueil_club = "startseite"
transfermarkt_info_club = "datenfakten"
transfermarkt_joueurs_club = "kader"
transfermarkt_info_stade = "stadion"
transfermarkt_info_joueur = "profil"

# Chaînes de caractères permettant de scrapp certaines infos
transfermarkt_stade_club_find = 'Stade'
transfermarkt_box_info_club_find = 'Informations et faits'
transfermarkt_nom_club_find = 'Nom officiel du club'
transfermarkt_adresse_club_find = 'Adresse'
transfermarkt_site_club_find = 'Page d\'accueil'
transfermarkt_annee_club_find = 'Fondation'
transfermarkt_couleurs_club_find = 'Couleurs de club'
transfermarkt_logo_club_find = 'Tous les sommets historiques'
transfermarkt_nom_stade_find = 'Nom du stade'
transfermarkt_capacite_stade_find = 'Capacité totale'
transfermarkt_construction_stade_find = 'Date de construction'
transfermarkt_box_adresse_stade_find = 'Contact'
transfermarkt_adresse_stade_find = 'Adresse'
transfermarkt_nom_joueur_find = 'Nom'
transfermarkt_naissance_joueur_find = 'Date de naissance'
transfermarkt_taille_joueur_find = 'Taille'
transfermarkt_nationalite_joueur_find = 'Nationalité'
transfermarkt_pied_joueur_find = 'Pied'
transfermarkt_equipementier_joueur_find = 'Équipementier'
transfermarkt_fin_contrat_pret_find = 'En contrat là-bas'
transfermarkt_fin_contrat_find = 'Contrat jusqu’à'

class_css_position_principale_start = 'position__primary--'
class_css_position_secondaire_start = 'position__secondary--'

clubs_scrapp = []
id_transfermarkt_clubs_deja_scrapp = []
all_joueurs = []
all_joueurs_id = []


transfermarkt_transferts_joueur = "transfers"
transfermarkt_historique_transfert_find = "Historique des transferts"
transfermarkt_class_transfert_ligne = "tm-player-transfer-history-grid"

contrat_vide = {
    "club": "",
    "debut": "",
    "fin": "",
    "pret": False,
    "libre": False,
    "transfert": False,
    "formation": False,
    "retraite_fin": False,
    "montant": 0,
}

montant_abrev_valeur = {
    "K": 1e3,
    "mio.": 1e6
}