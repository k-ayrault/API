import json
import logging

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import validators
import scrapp_func_global
import copy
import sys
from inspect import currentframe, getframeinfo

# TODO vérifier date de fin contrat club qui prête actuellement un joueur

def getIdClubsPresent():
    for club in scrapp_func_global.all_clubs:
        scrapp_func_global.all_clubs_id.append(club["id_transfermarkt"])


def getClubsLigue1():
    result = requests.get(scrapp_func_global.transfermarkt_base_url + scrapp_func_global.link_classement_ligue_1,
                          headers=scrapp_func_global.headers)
    clubs = []
    if (result.ok):
        soup = BeautifulSoup(result.text, "html.parser")
        try:
            classement = soup.find("div", {"id": "yw1"}).find("table")
            tds = classement.find("tbody").findAll("tr")
            for td in tds:
                try:
                    href = td.find("a")['href']
                    link = scrapp_func_global.transfermarkt_base_url + href
                    link = link.replace(scrapp_func_global.transfermarkt_accueil_club,
                                        scrapp_func_global.transfermarkt_url_replace)
                    match = (re.search("/verein/", link))
                    name = href[href.find("/") + 1: href.find("/" + scrapp_func_global.transfermarkt_accueil_club)]
                    id = link[match.end():]
                    id_find = id.find("/")
                    if id_find == -1:
                        id_find = len(id)
                    id = id[:id_find]
                    clubs.append({"id": id, "link": link, "nom": name})
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Problème au niveau de la récupération de l'id, nom et lien du club : {e} !")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Le classement de la ligue 1 n'a pu être récupéré dans le DOM : {e} !")
    return clubs


def getInfoClub(club_to_scrapp):
    id_transfermarkt = club_to_scrapp["id"]
    if id_transfermarkt not in scrapp_func_global.all_clubs_id:
        # "Création" du lien du club où sont les infos de ce dernier
        link = club_to_scrapp["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                              scrapp_func_global.transfermarkt_info_club)
        result = requests.get(link, headers=scrapp_func_global.headers)
        club = {
            "id_transfermarkt": club_to_scrapp["id"],
            "nom": '',
            "pays": '',
            "site": '',
            "creation": '',
            "couleurs": [],
            "logo_principal": '',
            "logos": [],
            "stade": {}
        }
        if result.ok:
            soup = BeautifulSoup(result.text, "html.parser")
            try:
                # Récupération du bandeau bleu de navigation du club
                subnavi = soup.find("div", {"id": "subnavi"})
                # Récupération de la div contenant toutes les informations que l'on souhaite
                row = subnavi.find_next_sibling("div", {"class": "row"})

                try:
                    # Récupération de la div contenant les informations du club
                    box_info = row.find("h2", text=re.compile(scrapp_func_global.transfermarkt_box_info_club_find))
                    box_info = box_info.find_parent("div", {"class": "box"}).find("div", {"class": "content"})

                    # Récupération du nom du club
                    try:
                        nom_club = box_info.find("th", text=re.compile(scrapp_func_global.transfermarkt_nom_club_find))
                        nom_club = nom_club.find_parent().find("td").text
                        club["nom"] = nom_club
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du nom "
                            f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) dans le DOM : {e} !")

                    # Récupération du pays où le club est
                    try:
                        pays_club = box_info.find("th",
                                                  text=re.compile(scrapp_func_global.transfermarkt_adresse_club_find))
                        # On déduit que le pays du club est au troisième tr de l'adresse
                        pays_club = pays_club.find_parent().find_next_sibling().find_next_sibling().find("td").text
                        club["pays"] = triNation(pays_club)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du pays "
                            f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) dans le DOM : {e} !")

                    # Récupération du site du club
                    try:
                        site_club = box_info.find("th",
                                                  text=re.compile(scrapp_func_global.transfermarkt_site_club_find))

                        site_club = site_club.find_parent().find("a")["href"]
                        club["site"] = site_club
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du site "
                            f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) dans le DOM : {e} !")

                    # Récupération de la date de création du club
                    try:
                        creation_club = box_info.find("th",
                                                      text=re.compile(scrapp_func_global.transfermarkt_annee_club_find))
                        creation_club = creation_club.find_parent().find("td").text
                        creation_club = datetime.strptime(creation_club.strip(), '%d %b %Y')
                        club["creation"] = creation_club.date().isoformat()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de de la "
                            f"date de création du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) dans le DOM : {e} !")

                    # Récupération des couleurs du club
                    couleurs_club = []
                    try:
                        couleurs = box_info.find("th",
                                                 text=re.compile(scrapp_func_global.transfermarkt_couleurs_club_find))
                        couleurs = couleurs.find_parent().find("td").find("p")
                        for couleur in couleurs.findAll():
                            try:
                                match = (re.search("background-color:", couleur["style"]))
                                couleur = couleur["style"][match.end():-1]
                                if couleur != '':
                                    couleurs_club.append(couleur)
                                    club["couleurs"] = couleurs_club
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logging.error(
                                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une couleur "
                                    f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) dans le DOM : {e} !")
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des couleurs  "
                            f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) dans le DOM : {e} !")

                    # Récupération du logo actuel du club
                    try:
                        lien_club = club_to_scrapp["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                                                   scrapp_func_global.transfermarkt_accueil_club)
                        lien_club = lien_club[lien_club.index(scrapp_func_global.transfermarkt_base_url) + len(scrapp_func_global.transfermarkt_base_url): lien_club.index(
                            str(club_to_scrapp["id"])) + len(str(club_to_scrapp["id"]))]
                        img_link = box_info.find("a", {"href": lien_club})
                        img = img_link.find("img")["src"]
                        club["logo_principal"] = img
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du logo actuel "
                            f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) dans le DOM : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des "
                        f"informations du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) : {e} !")

                # Récupération des anciens logos du club
                logos_club = []
                try:
                    logos = soup.find("h2", text=re.compile(scrapp_func_global.transfermarkt_logo_club_find))
                    logos = logos.find_parent("div", {"class": "box"}).findAll("img")
                    for logo in logos:
                        try:
                            # Vérification que src soit bien un lien afin de ne pas récupérer uniquement un chemin sur un serv par ex.
                            if validators.url(logo["src"]):
                                logos_club.append(logo["src"])
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'un ancien logo "
                                f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des anciens logos "
                        f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) : {e} !")

                club["logos"] = logos_club
                club["stade"] = getInfoStadeClub(club_to_scrapp)
                scrapp_func_global.all_clubs.append(club)
                scrapp_func_global.all_clubs_id.append(club["id_transfermarkt"])

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des informations "
                    f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) : {e} !")
    else:
        frameinfo = getframeinfo(currentframe())
        logging.error(
            f"[ERROR] {frameinfo.lineno} Le club {club_to_scrapp['nom']} est déjà récupéré !")


def getInfoStadeClub(club):
    stade = {
        'nom': '',
        'capacite': 0,
        'construction': 0000,
        'adresse': '',
        'images': []
    }
    link = club["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                scrapp_func_global.transfermarkt_info_stade)
    result = requests.get(link, headers=scrapp_func_global.headers)
    if result.ok:
        soup = BeautifulSoup(result.text, "html.parser")

        # Récupération de la div contenant ces infos
        try:
            row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})

            # Récupération du nom du stade
            try:
                nom_stade = row.find("th", text=re.compile(scrapp_func_global.transfermarkt_nom_stade_find))
                nom_stade = nom_stade.find_parent().find("td").text
                stade["nom"] = nom_stade
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du nom du stade "
                    f"du club {club['nom']} ({club['id']}) : {e} !")

            # Récupération de la div contenant les informations du stade via le nom de ce dernier
            box_info = row.find("h1", text=re.compile(stade["nom"]))
            box_info = box_info.find_parent("div", {"class": "box"})

            # Récupération de la capacité du stade
            try:
                capacite = box_info.find("th", text=re.compile(scrapp_func_global.transfermarkt_capacite_stade_find))
                capacite = capacite.find_parent().find("td").text
                stade["capacite"] = int(capacite.replace('.', ''))
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la capacité du stade "
                    f"du club {club['nom']} ({club['id']}) : {e} !")

            # Récupération de l'année de construction du stade
            try:
                construction = box_info.find("th", text=re.compile(
                    scrapp_func_global.transfermarkt_construction_stade_find))
                construction = construction.find_parent().find("td").text
                stade["construction"] = int(construction)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de l'année de "
                    f"construction du stade du club {club['nom']} ({club['id']}) : {e} !")

            # Récupération des images du stade
            images_stade = []
            try:
                images = box_info.findAll("img")
                for logo in images:
                    try:
                        if validators.url(logo["src"]):
                            images_stade.append(logo["src"])
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une image du "
                            f"stade du club {club['nom']} ({club['id']}) : {e} !")
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des images du "
                    f"stade du club {club['nom']} ({club['id']}) : {e} !")

            stade["images"] = images_stade

            # Récupération de l'adresse du stade
            adresse = ""
            try:
                box_adresse = row.find("h2", text=re.compile(scrapp_func_global.transfermarkt_box_adresse_stade_find))
                box_adresse = box_adresse.find_parent("div", {
                    "class": "box"})
                tr_adresse = box_adresse.find("th",
                                              text=re.compile(
                                                  scrapp_func_global.transfermarkt_adresse_stade_find)).find_parent(
                    "tr")
                adresse = tr_adresse.find("td").text.strip()
                tr_adresse = tr_adresse.find_next_sibling("tr")
                th_text = tr_adresse.find("th").text
                while th_text == "" and tr_adresse is not None:
                    adresse += ", " + tr_adresse.find("td").text.strip()
                    tr_adresse = tr_adresse.find_next_sibling("tr")
                    if tr_adresse is not None:
                        th_text = tr_adresse.find("th").text
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de l'adresse du "
                    f"stade du club {club['nom']} ({club['id']}) : {e} !")

            stade["adresse"] = adresse

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du club {club['nom']} ({club['id']}) : {e} !")

    return stade


def getJoueursClub(club_to_scrapp):
    joueurs = []
    # "Création" du lien du club où sont les infos de ce dernier
    link = club_to_scrapp["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                          scrapp_func_global.transfermarkt_joueurs_club)
    result = requests.get(link, headers=scrapp_func_global.headers)
    if result.ok:
        soup = BeautifulSoup(result.text, "html.parser")
        table_effectif = soup.find("div", {"id": "yw1"}).find("table")
        try:
            tr_joueurs = table_effectif.find("tbody").findAll("td", {"class": "posrela"})
            for tr_joueur in tr_joueurs:
                try:
                    link = tr_joueur.find("table").find("a")["href"]
                    link = link.replace(scrapp_func_global.transfermarkt_info_joueur,
                                        scrapp_func_global.transfermarkt_url_replace)
                    match = (re.search("/spieler/", link))
                    id = link[match.end():]
                    joueur = {"id": id, "link": scrapp_func_global.transfermarkt_base_url + link}
                    joueurs.append(joueur)
                    getInfoJoueur(joueur)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de l'id et du "
                        f"lien d'un joueur du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) : {e} !")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la liste des joueurs "
                f"du club {club_to_scrapp['nom']} ({club_to_scrapp['id']}) : {e} !")

    return joueurs


def getInfoJoueur(joueur_to_scrapp):
    id_transfermarkt = joueur_to_scrapp["id"]
    # "Création" du lien du club où sont les infos de ce dernier
    link = joueur_to_scrapp["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                            scrapp_func_global.transfermarkt_info_joueur)
    result = requests.get(link, headers=scrapp_func_global.headers)
    if result.ok:
        soup = BeautifulSoup(result.text, "html.parser")
        # Si le joueur n'est pas encore présent dans les données actuelles, récupération infos persos + carrière sinon
        # juste mise à jour de la carrière
        if id_transfermarkt not in scrapp_func_global.all_joueurs_id:
            joueur = {
                "id_transfermarkt": joueur_to_scrapp["id"],
                "lien_transfermarkt": joueur_to_scrapp["link"],
                "nom": '',
                "prenom": '',
                "nom_complet": '',
                "date_naissance": '',
                "pays": [],
                "positions_principales": [],
                "positions_secondaires": [],
                "pied": '',
                "taille": 0,
                "equipementier": '',
                "contrats": [],
                "date_maj": None
            }
            # Récupération des informations "personnelles" du joueur
            try:
                # Récupération de la div contenant ces infos
                header = soup.find("main").find("header", {"class": "data-header"})

                # Récupération du nom/prénom du joueur
                try:
                    # Récupération du "titre" du nom/prénom du joueur
                    h1_name_joueur = header.find("div", {"class": "data-header__headline-container"}).find("h1")
                    # Suppression du numéro du joueur dans ce titre
                    span_numero_joueur = h1_name_joueur.find("span", {"class": "data-header__shirt-number"})
                    if span_numero_joueur is not None:
                        span_numero_joueur.decompose()
                    # Récupération du nom du joueur présent dans la balise <strong>
                    joueur["nom"] = h1_name_joueur.find("strong").text
                    # Suppression du nom dans le titre afin de n'avoir plus que le prénom
                    h1_name_joueur.find("strong").decompose()
                    # Récupération du prénom qui est présent dans le reste du titre
                    joueur["prenom"] = h1_name_joueur.text.strip()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du nom/prénom "
                        f"du joueur {joueur_to_scrapp['id']} via le header : {e} !")

                # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
                row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
                # Récupération du tableau contenant les informations personnelles du joueur
                info_table = row.find("div", {"class": "info-table"})

                # Récupération du nom complet du joueur
                try:
                    nom_complet = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_nom_joueur_find))
                    if nom_complet is not None:
                        joueur["nom_complet"] = nom_complet.find_parent().find_next_sibling().text
                    else:
                        joueur["nom_complet"] = joueur["prenom"] + " " + joueur["nom"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du nom complet "
                        f"du joueur {joueur_to_scrapp['id']} : {e} !")

                # Indiquer dans le log le joueur que l'on est en train de traiter
                logging.info(f"[INFO] - {joueur['nom_complet']} : En cours")

                # Récupération de la date de naissance du joueur
                try:
                    naissance = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_naissance_joueur_find))
                    naissance = naissance.find_parent().find_next_sibling().find("a").text
                    naissance = datetime.strptime(naissance.strip(), '%d %b %Y')
                    joueur["date_naissance"] = naissance.date().isoformat()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la date "
                        f"de naissance du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                # Récupération des nationalités du joueur
                try:
                    nationalite = info_table.find(
                        text=re.compile(scrapp_func_global.transfermarkt_nationalite_joueur_find))
                    nationalite = nationalite.find_parent().find_next_sibling()
                    for img in nationalite.findAll("img"):
                        try:
                            pays = triNation(img["alt"])
                            joueur["pays"].append(pays)
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                f"nationalité du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des "
                        f"nationalités du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                # Récupération du pied fort du joueur
                try:
                    pied = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_pied_joueur_find))
                    joueur["pied"] = pied.find_parent().find_next_sibling().text
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du pied fort "
                        f"du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                # Récupération de la taille du joueur
                try:
                    taille = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_taille_joueur_find))
                    joueur["taille"] = re.sub('\D', '', taille.find_parent().find_next_sibling().text)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la taille "
                        f"du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                # Récupération de l'équipementier actuel du joueur
                try:
                    equipementier = info_table.find(
                        text=re.compile(scrapp_func_global.transfermarkt_equipementier_joueur_find))
                    joueur["equipementier"] = equipementier.find_parent().find_next_sibling().text
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de "
                        f"l'équipementier actuel du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                # Récupérations des positions du joueur
                try:
                    # Récupération de la div contenant les différentes positions du joueur (point sur le terrain)
                    box_positions = soup.find("div", {"class": "detail-position__matchfield"})

                    # Récupération des spans correspondants aux positions principales du joueur
                    span_positions_principales = box_positions.findAll("span", {"class": "position__primary"})

                    positions_principales = []
                    for span_position_principale in span_positions_principales:
                        try:
                            position = [class_type for class_type in span_position_principale["class"]
                                        if scrapp_func_global.class_css_position_principale_start in class_type
                                        ][0].replace(scrapp_func_global.class_css_position_principale_start, "")
                            if position.isdigit():
                                positions_principales.append(int(position))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                f"position principale du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) "
                                f": {e} !")

                    joueur["positions_principales"] = positions_principales

                    # Récupération des spans correspondants aux positions secondaires du joueur
                    span_positions_secondaires = box_positions.findAll("span", {"class": "position__secondary"})

                    positions_secondaires = []

                    for span_position_secondaire in span_positions_secondaires:
                        try:
                            position = [class_type for class_type in span_position_secondaire["class"]
                                        if scrapp_func_global.class_css_position_secondaire_start in class_type
                                        ][0].replace(scrapp_func_global.class_css_position_secondaire_start, "")
                            if position.isdigit():
                                positions_secondaires.append(int(position))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                f"position secondaire du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) "
                                f": {e} !")

                    joueur["positions_secondaires"] = positions_secondaires
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des positions "
                        f"du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                # Récupération date de fin du dernier contrat du joueur (çàd celui actuel normalement)
                date_fin_contrat = None
                try:
                    # Récupère la date de fin du contrat avec le club qui prête le joueur (si prêté)
                    fin_contrat = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_fin_contrat_pret_find))
                    # Si le joueur n'est pas prêté, récupère la date de fin du contrat
                    if fin_contrat is None:
                        fin_contrat = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_fin_contrat_find))

                    fin_contrat = fin_contrat.find_parent().find_next_sibling().text
                    try:
                        fin_contrat = datetime.strptime(fin_contrat.strip(), '%d %b %Y')
                        date_fin_contrat = fin_contrat.date().isoformat()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la conversion de la date de "
                            f"fin du contrat actuel ({fin_contrat}) du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la date de "
                        f"fin du contrat actuel  du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                contrats = getContratsJoueur(joueur_to_scrapp, date_fin_contrat)
                joueur["contrats"] = contrats

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des informations "
                    f"personnelles du joueur {joueur_to_scrapp['id']} : {e} !")

            scrapp_func_global.all_joueurs.append(joueur)
            scrapp_func_global.all_joueurs_id.append(joueur["id_transfermarkt"])
        else:
            try:
                # Récupération du joueur correspondant à l'id_transfermarkt
                joueur = next((x for x in scrapp_func_global.all_joueurs if x["id_transfermarkt"] == id_transfermarkt),
                              None)

                # Indiquer dans le log le joueur que l'on est en train de traiter
                logging.info(f"[INFO] - {joueur['nom_complet']} : En cours")

                date_fin_contrat = None
                try :
                    # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
                    row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
                    # Récupération du tableau contenant les informations personnelles du joueur
                    info_table = row.find("div", {"class": "info-table"})

                    # Récupération de la taille du joueur
                    try:
                        taille = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_taille_joueur_find))
                        joueur["taille"] = re.sub('\D', '', taille.find_parent().find_next_sibling().text)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la taille "
                            f"du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                    # Récupération de l'équipementier actuel du joueur
                    try:
                        equipementier = info_table.find(
                            text=re.compile(scrapp_func_global.transfermarkt_equipementier_joueur_find))
                        joueur["equipementier"] = equipementier.find_parent().find_next_sibling().text
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de "
                            f"l'équipementier actuel du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                    # Récupérations des positions du joueur
                    try:
                        # Récupération de la div contenant les différentes positions du joueur (point sur le terrain)
                        box_positions = soup.find("div", {"class": "detail-position__matchfield"})

                        # Récupération des spans correspondants aux positions principales du joueur
                        span_positions_principales = box_positions.findAll("span", {"class": "position__primary"})

                        positions_principales = []
                        for span_position_principale in span_positions_principales:
                            try:
                                position = [class_type for class_type in span_position_principale["class"]
                                            if scrapp_func_global.class_css_position_principale_start in class_type
                                            ][0].replace(scrapp_func_global.class_css_position_principale_start, "")
                                if position.isdigit():
                                    positions_principales.append(int(position))
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logging.error(
                                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                    f"position principale du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) "
                                    f": {e} !")

                        joueur["positions_principales"] = positions_principales

                        # Récupération des spans correspondants aux positions secondaires du joueur
                        span_positions_secondaires = box_positions.findAll("span", {"class": "position__secondary"})

                        positions_secondaires = []

                        for span_position_secondaire in span_positions_secondaires:
                            try:
                                position = [class_type for class_type in span_position_secondaire["class"]
                                            if scrapp_func_global.class_css_position_secondaire_start in class_type
                                            ][0].replace(scrapp_func_global.class_css_position_secondaire_start, "")
                                if position.isdigit():
                                    positions_secondaires.append(int(position))
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logging.error(
                                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                    f"position secondaire du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) "
                                    f": {e} !")

                        joueur["positions_secondaires"] = positions_secondaires
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des positions "
                            f"du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")

                    # Récupération date de fin du dernier contrat du joueur (çàd celui actuel normalement)
                    try:
                        # Récupère la date de fin du contrat avec le club qui prête le joueur (si prêté)
                        fin_contrat = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_fin_contrat_pret_find))
                        # Si le joueur n'est pas prêté, récupère la date de fin du contrat
                        if fin_contrat is None:
                            fin_contrat = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_fin_contrat_find))

                        fin_contrat = fin_contrat.find_parent().find_next_sibling().text
                        try:
                            fin_contrat = datetime.strptime(fin_contrat.strip(), '%d %b %Y')
                            date_fin_contrat = fin_contrat.date().isoformat()
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la conversion de la date de "
                                f"fin du contrat actuel ({fin_contrat}) du joueur {joueur['nom_complet']} ({joueur_to_scrapp['id']}) : {e} !")
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la date de "
                            f"fin du contrat actuel  du joueur ({joueur_to_scrapp['id']}) : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la màj des informations "
                        f"personnelles  du joueur ({joueur_to_scrapp['id']}) : {e} !")

                # Si le joueur n'a pas de contrat on les récupère sinon on les mets à jour
                if "contrats" not in joueur or joueur["contrats"] is None or len(joueur["contrats"]) == 0:
                    contrats = getContratsJoueur(joueur_to_scrapp, date_fin_contrat)
                    joueur["contrats"] = contrats
                else:
                    majContratsJoueur(joueur, joueur_to_scrapp, date_fin_contrat)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la màj des informations "
                    f"personnelles du joueur {joueur_to_scrapp['id']} : {e} !")
                return
        joueur["date_maj"] = datetime.now().isoformat()
        logging.info(f"[INFO] - {joueur['nom_complet']} : Terminé")
        logging.info("-------------------------------------------------------------------------------------------------")


def getContratsJoueur(joueur_to_scrapp, date_fin_contrat):
    # "Création" du lien du joueur où sont les transfert de ce dernier
    link = joueur_to_scrapp["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                            scrapp_func_global.transfermarkt_transferts_joueur)
    result = requests.get(link, headers=scrapp_func_global.headers)
    if result.ok:
        soup = BeautifulSoup(result.text, "html.parser")
        try:
            # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
            row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
            # Récupération du tableau contenant les différents transferts du joueur
            titre_tableau_transferts = row.find("h2",
                                                text=re.compile(scrapp_func_global.transfermarkt_historique_transfert_find))
            tableau_transferts = titre_tableau_transferts.find_parent()

            # Récupération des lignes du tableau correspondant à un 'transfert' (une seule classe)
            lignes = tableau_transferts.findAll("div", {"class": scrapp_func_global.transfermarkt_class_transfert_ligne})
            lignes = [ligne for ligne in lignes if len(ligne["class"]) == 1]
            # Inverse le tableau afin d'avoir les contrats dans un ordre croissant de date
            lignes = lignes[::-1]

            index_ligne_transfert = 0
            contrats = []

            while index_ligne_transfert < len(lignes):
                # Récupération de la ligne de transfert que l'on traite
                ligne_transfert = lignes[index_ligne_transfert]

                if index_ligne_transfert == len(lignes) - 1:
                    index_ligne_transfert += 1


                montant_transfert = getMontantTransfertLigne(ligne_transfert)

                montant_transfert_ligne = montant_transfert

                date_transfert = getDateTransfertLigne(ligne_transfert)

                club_partant = getClubPartantLigne(ligne_transfert)
                club_entrant = getClubEntrantLigne(ligne_transfert)
                club_partant_nom = club_partant["nom"]
                club_partant_id = club_partant["id"]
                club_entrant_nom = club_entrant["nom"]
                club_entrant_id = club_entrant["id"]

                contrat = copy.deepcopy(scrapp_func_global.contrat_vide)
                contrat["debut"] = date_transfert

                if montant_transfert == "Transfert libre":
                    contrat["libre"] = True
                else:
                    contrat["transfert"] = True
                    contrat["montant"] = montantToInt(montant_transfert)

                # S'il s'agit du premier contrat du joueur et qu'il s'agit de son club formateur
                if index_ligne_transfert == 0 and montant_transfert == "-" \
                        and club_partant_nom != "Fin de carrière" and club_partant_nom != "Pause carrière":
                    contrat["formation"] = True


                # Récupération de la dernière ligne de son départ définitif ou non si toujours au club (s'il ne s'agit pas de la dernière)
                if index_ligne_transfert < len(lignes) - 1:
                    # Tant qu'il s'agit de la même ligne ou qu'il s'agit d'une ligne correspondant à un prêt
                    while index_ligne_transfert < len(lignes) and \
                            ((date_transfert == contrat["debut"] and montant_transfert == montant_transfert_ligne)
                             or (montant_transfert == "-" or re.search("prêt", montant_transfert, re.IGNORECASE))):
                        ligne_transfert = lignes[index_ligne_transfert]

                        montant_transfert = getMontantTransfertLigne(ligne_transfert)

                        pret = getContratPret(lignes, index_ligne_transfert, ligne_transfert, row)

                        club_entrant = getClubEntrantLigne(ligne_transfert)
                        club_entrant_nom = club_entrant["nom"]
                        club_entrant_id = club_entrant["id"]
                        if pret is not None:
                            contrats.append(pret)
                            logging.info(f"[INFO] -- {pret['club']} : Prêt")
                        else:
                            if club_entrant_nom == "Fin de carrière":
                                montant_transfert = "retraite"
                                contrat["retraite_fin"] = True
                            elif club_entrant_nom == "Pause carrière":
                                montant_transfert = "pause"
                        index_ligne_transfert += 1
                    index_ligne_transfert -= 1

                club_entrant = getClubEntrantLigne(ligne_transfert)
                club_partant = getClubPartantLigne(ligne_transfert)

                # Si le joueur est toujours au club
                if montant_transfert == 'Fin du prêt':
                    contrat["club"] = club_entrant["id"]
                    contrat["fin"] = date_fin_contrat
                    if index_ligne_transfert == len(lignes) - 1:
                        index_ligne_transfert += 1
                elif montant_transfert == "-" or re.search("prêt", montant_transfert,
                                                           re.IGNORECASE) or index_ligne_transfert == len(lignes):
                    contrat["club"] = club_entrant["id"]
                    contrat["fin"] = date_fin_contrat
                    if index_ligne_transfert == len(lignes) - 1:
                        index_ligne_transfert += 1
                else:
                    contrat["club"] = club_partant["id"]
                    contrat["fin"] = getDateTransfertLigne(ligne_transfert)
                contrats.append(contrat)
                logging.info(f"[INFO] -- {contrat['club']} : Transfert")
                if club_entrant_nom == "Pause carrière" or club_entrant_nom == "Fin de carrière":
                    index_ligne_transfert += 1
            contrats.sort(key=lambda x: x["debut"], reverse=True)
            return contrats
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des contrats "
                f"du joueur {joueur_to_scrapp['id']} : {e} !")

    return None


def majContratsJoueur(joueur, joueur_to_scrapp, date_fin_contrat):
    contrats = joueur["contrats"]
    contrats.sort(key=lambda x: x["debut"], reverse=True)
    dernier_contrat = contrats[0]
    contrats.sort(key=lambda x: x["fin"], reverse=True)
    contrat_actuel = contrats[0]
    # "Création" du lien du joueur où sont les transfert de ce dernier
    link = joueur_to_scrapp["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                            scrapp_func_global.transfermarkt_transferts_joueur)
    result = requests.get(link, headers=scrapp_func_global.headers)
    if result.ok:
        soup = BeautifulSoup(result.text, "html.parser")
        try:
            # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
            row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})

            # Récupération du tableau contenant les différents transferts du joueur
            titre_tableau_transferts = row.find("h2",
                                                text=re.compile(scrapp_func_global.transfermarkt_historique_transfert_find))
            tableau_transferts = titre_tableau_transferts.find_parent()

            # Récupération des lignes du tableau correspondant à un 'transfert' (une seule classe)
            lignes = tableau_transferts.findAll("div", {"class": scrapp_func_global.transfermarkt_class_transfert_ligne})
            lignes = [ligne for ligne in lignes if len(ligne["class"]) == 1]
            # Inverse le tableau afin d'avoir les contrats dans un ordre croissant de date
            lignes = lignes[::-1]

            index_ligne_transfert = 0

            while index_ligne_transfert < len(lignes):
                # Récupération de la ligne de transfert que l'on traite
                ligne_transfert = lignes[index_ligne_transfert]

                date_transfert = getDateTransfertLigne(ligne_transfert)
                club_entrant = getClubEntrantLigne(ligne_transfert)

                # S'il s'agit de la ligne représentant le transfert du dernier contrat sauvegardé
                if dernier_contrat["debut"] == date_transfert and dernier_contrat["club"] == club_entrant["id"]:
                    # Si le dernier contrat est un prêt on va chercher la date de fin de ce prêt
                    if dernier_contrat["pret"]:
                        montant_transfert = ""
                        while index_ligne_transfert < len(lignes) and montant_transfert != "Fin du prêt":
                            ligne_transfert = lignes[index_ligne_transfert]
                            montant_transfert = getMontantTransfertLigne(ligne_transfert)
                            index_ligne_transfert += 1
                        index_ligne_transfert -= 1
                        if montant_transfert == "Fin de prêt":
                            dernier_contrat["fin"] = getDateTransfertLigne(ligne_transfert)

                        montant_transfert_ligne = montant_transfert
                        while index_ligne_transfert < len(lignes) and \
                                ((date_transfert == contrat_actuel[
                                    "debut"] and montant_transfert == montant_transfert_ligne)
                                 or (montant_transfert == "-" or re.search("prêt", montant_transfert, re.IGNORECASE))):
                            ligne_transfert = lignes[index_ligne_transfert]
                            montant_transfert = getMontantTransfertLigne(ligne_transfert)
                            pret = getContratPret(lignes, index_ligne_transfert, ligne_transfert, row)

                            club_entrant = getClubEntrantLigne(ligne_transfert)
                            club_entrant_nom = club_entrant["nom"]
                            club_entrant_id = club_entrant["id"]
                            if pret is not None:
                                contrats.append(pret)
                                logging.info(f"[INFO] -- {pret['club']} : Prêt")
                            else:
                                if club_entrant_nom == "Fin de carrière":
                                    montant_transfert = "retraite"
                                    contrat_actuel["retraite_fin"] = True
                                elif club_entrant_nom == "Pause carrière":
                                    montant_transfert = "pause"
                            index_ligne_transfert += 1
                        index_ligne_transfert -= 1
                        club_entrant = getClubEntrantLigne(ligne_transfert)
                        club_entrant_nom = club_entrant["nom"]
                        club_partant = getClubPartantLigne(ligne_transfert)
                        # Si le joueur est toujours au club
                        if montant_transfert == "-":
                            contrat_actuel["fin"] = date_fin_contrat
                        else:
                            contrat_actuel["fin"] = getDateTransfertLigne(ligne_transfert)

                        if club_entrant_nom == "Pause carrière" or club_entrant_nom == "Fin de carrière":
                            index_ligne_transfert += 1
                    # Si le dernier est contrat est un transfer sec
                    else:
                        # Si le dernier contrat enregistré est le dernier des transferts on change la fin du contrat
                        if index_ligne_transfert == len(lignes) - 1:
                            dernier_contrat["fin"] = date_fin_contrat
                            index_ligne_transfert += 1
                        # Si le joueur a eu d'autres transferts d'ici la dernière sauvegarde
                        else:
                            montant_transfert = getMontantTransfertLigne(ligne_transfert)
                            montant_transfert_ligne = montant_transfert
                            while index_ligne_transfert < len(lignes) and \
                                    ((date_transfert == dernier_contrat[
                                        "debut"] and montant_transfert == montant_transfert_ligne)
                                     or (montant_transfert == "-" or re.search("prêt", montant_transfert, re.IGNORECASE))):
                                ligne_transfert = lignes[index_ligne_transfert]
                                montant_transfert = getMontantTransfertLigne(ligne_transfert)
                                pret = getContratPret(lignes, index_ligne_transfert, ligne_transfert, row)

                                club_entrant = getClubEntrantLigne(ligne_transfert)
                                club_entrant_nom = club_entrant["nom"]
                                club_entrant_id = club_entrant["id"]
                                if pret is not None:
                                    contrats.append(pret)
                                    logging.info(f"[INFO] -- {pret['club']} : Prêt")
                                else:
                                    if club_entrant_nom == "Fin de carrière":
                                        montant_transfert = "retraite"
                                        dernier_contrat["retraite_fin"] = True
                                    elif club_entrant_nom == "Pause carrière":
                                        montant_transfert = "pause"
                                index_ligne_transfert += 1
                            index_ligne_transfert -= 1
                            club_entrant = getClubEntrantLigne(ligne_transfert)
                            club_entrant_nom = club_entrant["nom"]
                            club_partant = getClubPartantLigne(ligne_transfert)
                            # Si le joueur est toujours au club
                            if montant_transfert == "-":
                                dernier_contrat["fin"] = date_fin_contrat
                            else:
                                dernier_contrat["fin"] = getDateTransfertLigne(ligne_transfert)
                            if club_entrant_nom == "Pause carrière" or club_entrant_nom == "Fin de carrière":
                                index_ligne_transfert += 1
                else:
                    if date_transfert > dernier_contrat["debut"]:
                        montant_transfert = getMontantTransfertLigne(ligne_transfert)
                        montant_transfert_ligne = montant_transfert
                        club_partant = getClubPartantLigne(ligne_transfert)
                        club_partant_nom = club_partant["nom"]
                        club_partant_id = club_partant["id"]
                        club_entrant_nom = club_entrant["nom"]
                        club_entrant_id = club_entrant["id"]

                        contrat = copy.deepcopy(scrapp_func_global.contrat_vide)
                        contrat["debut"] = date_transfert

                        if montant_transfert == "Transfert libre":
                            contrat["libre"] = True
                        else:
                            contrat["transfert"] = True
                            contrat["montant"] = montantToInt(montant_transfert)

                        # S'il s'agit du premier contrat du joueur et qu'il s'agit de son club formateur
                        if index_ligne_transfert == 0 and montant_transfert == "-" \
                                and club_partant_nom != "Fin de carrière" and club_partant_nom != "Pause carrière":
                            contrat["formation"] = True

                        if index_ligne_transfert == len(lignes) - 1:
                            index_ligne_transfert += 1
                        if index_ligne_transfert < len(lignes) - 1:
                            # Récupération de la dernière ligne de son départ définitif ou non si toujours au club
                            while index_ligne_transfert < len(lignes) and \
                                    ((date_transfert == contrat["debut"] and montant_transfert == montant_transfert_ligne)
                                     or (montant_transfert == "-" or re.search("prêt", montant_transfert, re.IGNORECASE))):
                                ligne_transfert = lignes[index_ligne_transfert]
                                montant_transfert = getMontantTransfertLigne(ligne_transfert)
                                pret = getContratPret(lignes, index_ligne_transfert, ligne_transfert, row)

                                club_entrant = getClubEntrantLigne(ligne_transfert)
                                club_entrant_nom = club_entrant["nom"]
                                club_entrant_id = club_entrant["id"]
                                if pret is not None:
                                    contrats.append(pret)
                                    logging.info(f"[INFO] -- {pret['club']} : Prêt")
                                else:
                                    if club_entrant_nom == "Fin de carrière":
                                        montant_transfert = "retraite"
                                        contrat["retraite_fin"] = True
                                    elif club_entrant_nom == "Pause carrière":
                                        montant_transfert = "pause"
                                index_ligne_transfert += 1
                            index_ligne_transfert -= 1
                        club_entrant = getClubEntrantLigne(ligne_transfert)
                        club_partant = getClubPartantLigne(ligne_transfert)
                        # Si le joueur est toujours au club
                        if montant_transfert == 'Fin du prêt':
                            contrat["club"] = club_entrant["id"]
                            contrat["fin"] = date_fin_contrat
                            if index_ligne_transfert == len(lignes) - 1:
                                index_ligne_transfert += 1
                        elif montant_transfert == "-" or re.search("prêt", montant_transfert,
                                                                   re.IGNORECASE) or index_ligne_transfert == len(
                            lignes) or index_ligne_transfert == len(lignes):
                            contrat["club"] = club_entrant["id"]
                            contrat["fin"] = date_fin_contrat
                            if index_ligne_transfert == len(lignes) - 1:
                                index_ligne_transfert += 1
                        else:
                            contrat["club"] = club_partant["id"]
                            contrat["fin"] = getDateTransfertLigne(ligne_transfert)
                        contrats.append(contrat)
                        logging.info(f"[INFO] -- {contrat['club']} : Transfert")
                        if club_entrant_nom == "Pause carrière" or club_entrant_nom == "Fin de carrière":
                            index_ligne_transfert += 1
                    else:
                        index_ligne_transfert += 1
            contrats.sort(key=lambda x: x["debut"], reverse=True)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la màj des contrats du joueur "
                f"{joueur['nom_complet']} : {e} !")
        return contrats


def getMontantTransfertLigne(ligne):
    montant = 0
    try :
        montant_transfert = ligne.find("div", {"class": scrapp_func_global.transfermarkt_class_transfert_ligne + "__fee"})
        if montant_transfert is not None:
            montant = montant_transfert.text.strip()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(
            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du montant d'un transfert : {e} !")
    return montant


def getDateTransfertLigne(ligne):
    date = ""
    try:
        date_transfert = ligne.find("div", {"class": scrapp_func_global.transfermarkt_class_transfert_ligne + "__date"})
        date_transfert = date_transfert.text.strip()
        date_transfert = datetime.strptime(date_transfert, "%d %b %Y")
        date = date_transfert.date().isoformat()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(
            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la date d'un transfert"
            f" : {e} !")
    return date


def getClubEntrantLigne(ligne):
    club = {"id": -1, "nom": ""}
    try:
        club_entrant_div = ligne.find("div",
                                      {"class": scrapp_func_global.transfermarkt_class_transfert_ligne + "__new-club"})
        if club_entrant_div is not None:
            club["nom"] = club_entrant_div.text.strip()
        if club["nom"] != "Fin de carrière" and club["nom"] != "Pause carrière" and club["nom"] != "":
            link_club = club_entrant_div.find("a")
            link_club = link_club["href"]
            link_club = link_club[:link_club.find("/saison_id/")]
            match = (re.search("/verein/", link_club))
            id = link_club[match.end():]
            club["id"] = id
            link_club = link_club.replace(scrapp_func_global.transfermarkt_transferts_joueur,
                                              scrapp_func_global.transfermarkt_url_replace)
            getInfoClub({"id": id, "nom": club["nom"], "link": scrapp_func_global.transfermarkt_base_url + link_club})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(
            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'un club entrant d'un transfert"
            f" : {e} !")
    return club


def getClubPartantLigne(ligne):
    club = {"id": -1, "nom": ""}
    try:
        club_sortant_div = ligne.find("div",
                                      {"class": scrapp_func_global.transfermarkt_class_transfert_ligne + "__old-club"})
        if club_sortant_div is not None:
            club["nom"] = club_sortant_div.text.strip()
        if club["nom"] != "Fin de carrière" and club["nom"] != "Pause carrière" and club["nom"] != "":
            link_club = club_sortant_div.find("a")
            if link_club is not None:
                link_club = link_club["href"]
                link_club = link_club[:link_club.find("/saison_id/")]
                match = (re.search("/verein/", link_club))
                id = link_club[match.end():]
                club["id"] = id
                link_club = link_club.replace(scrapp_func_global.transfermarkt_transferts_joueur,
                                              scrapp_func_global.transfermarkt_url_replace)
                getInfoClub({"id": id, "nom": club["nom"], "link": scrapp_func_global.transfermarkt_base_url + link_club})
        return club
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(
            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'un club partant d'un "
            f"transfert : {e} !")


def getContratPret(lignes, index_ligne, ligne, page):
    try:
        montant = getMontantTransfertLigne(ligne)
        # S'il s'agit du début d'un prêt
        if re.search("prêt", montant, re.IGNORECASE) and montant != "Fin du prêt":
            contrat = copy.deepcopy(scrapp_func_global.contrat_vide)
            club_entrant = getClubEntrantLigne(ligne)
            contrat["club"] = club_entrant["id"]
            contrat["debut"] = getDateTransfertLigne(ligne)
            contrat["pret"] = True
            club_partant = getClubPartantLigne(ligne)
            # Récupération de la ligne correspondant à la fin du prêt
            while index_ligne < len(lignes) and (montant != "Fin du prêt" and club_partant != club_entrant):
                ligne = lignes[index_ligne]
                montant = getMontantTransfertLigne(ligne)
                club_partant = getClubPartantLigne(ligne)
                index_ligne += 1
            index_ligne -= 1
            contrat["fin"] = getDateTransfertLigne(ligne)
            return contrat
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(
            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du contrat (prêt) pour la "
            f"ligne avec comme index {index_ligne} : {e} !")
    return None


def montantToInt(montant):
    montant = montant.replace("€", "").strip()
    abrev = re.sub("[^A-z.]", "", montant)
    try:
        montant = re.sub("[^0-9,]", "", montant).replace(",", ".")
        montant = float(montant)
        if abrev in scrapp_func_global.montant_abrev_valeur:
            facteur = scrapp_func_global.montant_abrev_valeur[abrev]
            montant = montant * facteur
            montant = int(montant)
            return montant
        return int(montant)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(
            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la tentative de passage du montant d'un "
            f"transfert en int : {e} !")
    return 0


def triNation(pays):
    if pays is not None:
        if pays == 'Angleterre':
            return 'Royaume-Uni'
    return pays
