import requests
import scrapp_func_global
from bs4 import BeautifulSoup
from datetime import datetime
import locale
import re
import numpy as np
import unidecode
import json
from pathlib import Path
import logging
from inspect import currentframe, getframeinfo
import sys, os

date_str_filename = datetime.now().strftime("%d_%m_%Y_%H_%M_%f")
log_filename = "log_scrapp_matchs_" + date_str_filename

log_file_path = Path("log/" + log_filename)

logging.basicConfig(filename=log_file_path, level=logging.INFO, encoding="UTF-8")

json_matchs = Path("donnees/matchs.json")

lien_calendrier = 'https://www.ligue1.com/fixtures-results'
nbre_journees = 38

replace_num_journee = '{numero_journee}'
lien_journee = lien_calendrier + '?matchDay=' + replace_num_journee

replace_num_match = '{id_match}'
lien_match = 'https://www.ligue1.com/match?matchId=' + replace_num_match

# Tentative de récupération de la liste des matchs déjà enregistrés sinon nouvelle liste
try:
    with open(json_matchs, "r") as m_json:
        liste_matchs = json.load(m_json)
except Exception as e:
    liste_matchs = {}


def scrappMatchsLigue1():
    num_journee = 1
    # Pour chaque journée de ligue 1 va scrapper les matchs de cette dernière
    while num_journee <= nbre_journees:
        scrappJournee(num_journee)
        num_journee = num_journee + 1


def scrappJournee(num_journee):
    lien = lien_journee.replace(replace_num_journee, str(num_journee))
    result = requests.get(lien, headers=scrapp_func_global.headers)

    if result.ok:
        soup = BeautifulSoup(result.text, "html.parser")

        div_matchs = soup.find("div", {"class": "calendar-widget"})

        if div_matchs is None:
            frameinfo = getframeinfo(currentframe())
            logging.error(
                f"[ERROR] {frameinfo.lineno} Problème au niveau de la structure HTML de la journée n°{num_journee} : Aucune 'div' avec la classe 'calendar-widget' !")
            return

        # Récupération chaque match de la journée (présent dans la 'div' avec la classe 'calendar-widget')
        matchs = div_matchs.findAll("li")

        for match in matchs:
            clubs_container_match = match.find("div", {"class", "Calendar-clubResult"})
            if clubs_container_match is None:
                frameinfo = getframeinfo(currentframe())
                logging.error(
                    f"[ERROR] {frameinfo.lineno} Problème au niveau de la structure HTML de la journée n°{num_journee} : Aucune 'div' avec la classe 'Calendar-clubResult' pour le match que l'on veut scrapp !")
                break
            # Id du match sur le site officiel de la Ligue 1
            id_match = clubs_container_match["id"]

            # Récupération des infos autour de ce match
            match = scrappMatch(id_match, num_journee)

            # Ajout du match dans la liste des matchs
            liste_matchs[id_match] = match

    # Sauvegarde des matchs scrappés pour cette journée dans le json adéquat
    try:
        with open(json_matchs, "w") as m_json:
            json.dump(liste_matchs, m_json, indent=4, sort_keys=True, default=str)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(
            f"[ERROR] {exc_tb.tb_lineno} Problème au niveau de la sauvegarde des match de la journée n°{num_journee} : {e} !")


def scrappMatch(id_match, num_journee):
    # Récupération des données du match avec l'id {id_match} si déjà enregistré sinon création d'un nouvel objet match vide
    try:
        match = liste_matchs[id_match]
    except:
        match = {
            "id_match": id_match,
            "termine": False,
            "journee": num_journee,
            "date_heure": None,
            "diffuseur": None,
            "domicile": {
                "club": None,
                "buts": None,
                "statistiques": None,
                "compositions": None,
                "remplacants": None,
            },
            "exterieur": {
                "club": None,
                "buts": None,
                "statistiques": None,
                "compositions": None,
                "remplacants": None,
            },
            "arbitres": {
                "principal": None,
                "var": None,
            }
        }

    # Si le match que l'on a récupéré n'est pas désigné comme terminé alors on va récupérer les infos au cas où de
    # nouvelles soient apparu depuis la dernière fois (ex: arbitre, compo, etc.)
    if not match["termine"]:
        lien = lien_match.replace(replace_num_match, str(id_match))
        result = requests.get(lien, headers=scrapp_func_global.headers)

        if result.ok:
            soup = BeautifulSoup(result.text, "html.parser")

            # Récupération de la date et heure ainsi que le diffuseur du match
            match_header_infos = soup.find("div", {"class": "MatchHeader-infos"})
            if match_header_infos is not None:
                date_heure_text = match_header_infos.find("p", {"class": "MatchHeader-text"})
                if date_heure_text is not None:
                    date_heure = None
                    # Split de la date_heure car format date - heure (ex: LUN. 26 SEPTEMBRE 2022 - 21:00)
                    # 'date_heure_split[0]' va donc normalement contenir le string de la date et 'date_heure_split[1]' le string de l'heure
                    date_heure_split = date_heure_text.text.split('-')
                    # 'Strip' les chaînes de caractères de la date et de l'heure afin de supprimer les espaces inutiles qu'il pourrait y avoir
                    date_heure_split = [s.strip() for s in date_heure_split]

                    # Conversion de la chaîne de caractère de la date pour avoir un format datetime
                    try:
                        date = datetime.strptime(date_heure_split[0], '%a %d %B %Y')
                    except:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Problème lors de la tentative de conversion de la date : {date_heure_split[0]} !")
                        date = None

                    # Conversion de la chaîne de caractère de l'heure pour l'ajouter à la date précédemment récupérer (si réussi)
                    if date is not None:
                        try:
                            heure_split = date_heure_split[1].split(':')
                            heure = int(heure_split[0])
                            minute = int(heure_split[1])
                            date_heure = date.replace(hour=heure, minute=minute)
                            date_heure = date_heure.isoformat()
                        except Exception as e:
                            date_heure = date
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Problème lors de la tentative de conversion de l'heure : {date_heure_split[1]} ({e}) !")

                    match["date_heure"] = date_heure

                if match["date_heure"] is None:
                    frameinfo = getframeinfo(currentframe())
                    logging.info(
                        f"[INFO] {frameinfo.lineno} Aucune heure de préciser dans le header du match n°{id_match} !")

                diffuseur_div = match_header_infos.find("div", {"class": "MatchHeader-broadcaster"})
                if diffuseur_div is not None:
                    diffuseur_img = diffuseur_div.find("img")
                    if diffuseur_img is not None:
                        try:
                            match["diffuseur"] = diffuseur_img["alt"]
                        except:
                            match["diffuseur"] = None

                if match["diffuseur"] is None:
                    frameinfo = getframeinfo(currentframe())
                    logging.info(
                        f"[INFO] {frameinfo.lineno} Aucun diffuseur de préciser dans le header du match n°{id_match} !")
            else:
                frameinfo = getframeinfo(currentframe())
                logging.error(
                    f"[ERROR] {frameinfo.lineno} Problème au niveau de la structure HTML du match n°{id_match} : Aucune infos dans le header du match (aucune 'div' avec la classe 'MatchHeader-infos') !")

            # Récupération des clubs concernés (domicile et extérieur) par le match ainsi que le score de ce dernier
            match_header_clubs = soup.find("div", {"class": "MatchHeader-clubs"})
            if match_header_clubs is not None:
                # Récupération de l'équipe à domicile
                domicile_infos = match_header_clubs.find("div", {"class": "MatchHeader-club team home"})
                if domicile_infos is not None:
                    # Récupération du nom du club à domicile dans l'alt de son logo (en enlevant le mot 'logo' de ce dernier)
                    domicile_img = domicile_infos.find("img", {"class": "MatchHeader-clubLogo"})
                    try:
                        domicile_nom = domicile_img["alt"].replace("logo", "").strip()
                        match["domicile"]["club"] = domicile_nom.strip()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Aucun club à domicile de désigné pour le match n°{id_match} : {e} !")
                        match["domicile"]["club"] = None
                else:
                    frameinfo = getframeinfo(currentframe())
                    logging.error(
                        f"[ERROR] {frameinfo.lineno} Aucun club à domicile de désigné pour le match n°{id_match} !")

                # Récupération de l'équipe à l'extérieur
                exterieur_infos = match_header_clubs.find("div", {"class": "MatchHeader-club team away"})
                if exterieur_infos is not None:
                    # Récupération du nom du club à domicile dans l'alt de son logo (en enlevant le mot 'logo' de ce dernier)
                    exterieur_img = exterieur_infos.find("img", {"class": "MatchHeader-clubLogo"})
                    try:
                        exterieur_nom = exterieur_img["alt"].replace("logo", "").strip()
                        match["exterieur"]["club"] = exterieur_nom.strip()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Aucun club à l'extérieur de désigné pour le match n°{id_match} : {e} !")
                        match["exterieur"]["club"] = None
                else:
                    frameinfo = getframeinfo(currentframe())
                    logging.error(
                        f"[ERROR] {frameinfo.lineno} Aucun club à l'extérieur de désigné pour le match n°{id_match} !")

                # Récupération du score du match
                score_infos = match_header_clubs.find("div", {"class": "MatchHeader-score"})
                if score_infos is not None:
                    # Récupération des buts de chaque équipe
                    try:
                        score_str = score_infos.find("p", {"class": "MatchHeader-scoreResult"})
                        score = score_str.text.split("-")
                        score = [s.strip() for s in score]
                        match["domicile"]["buts"] = int(score[0])
                        match["exterieur"]["buts"] = int(score[1])
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.info(
                            f"[INFO] {exc_tb.tb_lineno} Le score n'a pas pu être récupéré pour le match n°{id_match} : {e} !")

                    # Contrôle si le match est terminé
                    try:
                        termine_str = score_infos.find("p", {"class": "MatchHeader-scoreMinutes"})
                        if termine_str.text.lower() == "finished".lower():
                            match["termine"] = True
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.info(
                            f"[INFO] {exc_tb.tb_lineno} Le contrôle pour savoir si le match n°{id_match} est terminé n'a pas pu se faire : {e} !")
            else:
                frameinfo = getframeinfo(currentframe())
                logging.error(
                    f"[ERROR] {frameinfo.lineno} Problème au niveau de la structure HTML du match n°{id_match} : Aucune infos sur les clubs et résultat dans le header du match (aucune 'div' avec la classe 'MatchHeader-clubs') !")

            # Récupération des différents acteurs officiels de la rencotre
            match_personnes_officielles = soup.find("div", {"id": "keyPlayers-Officials"})
            try:
                # Récupération de la liste de ces acteurs
                liste_personnes_officielles = match_personnes_officielles.find("ul", "Officials-list")

                # Récupération de l'arbitre principal de la rencontre
                try:
                    arbitre_principal = liste_personnes_officielles.find("span", text=re.compile("^referee$",
                                                                                                 re.I)).findParent()
                    arbitre_infos = arbitre_principal.find("span", {"class": "Officials-name"}).text
                    nom_arbitre = arbitre_infos[arbitre_infos.index(
                        re.findall(r'\b[A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)*\b', arbitre_infos)[0]):].strip()
                    prenom_arbitre = arbitre_infos.replace(nom_arbitre, '').strip()
                    match["arbitres"]["principal"] = {
                        "prenom": prenom_arbitre,
                        "nom": nom_arbitre
                    }
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.info(
                        f"[INFO] {exc_tb.tb_lineno} L'arbitre principal n'a pas pu être récupéré pour le match n°{id_match} : {e} !")

                # Récupération de l'arbitre assistant vidéo de la rencontre
                try:
                    arbitre_var = liste_personnes_officielles.find("span", text=re.compile("^video referee assistant$",
                                                                                           re.I)).findParent()
                    arbitre_infos = arbitre_var.find("span", {"class": "Officials-name"}).text
                    nom_arbitre = ''.join(re.findall(r'\b[A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)*\b', arbitre_infos)[0]).strip()
                    prenom_arbitre = arbitre_infos.replace(nom_arbitre, '').strip()
                    match["arbitres"]["var"] = {
                        "prenom": prenom_arbitre,
                        "nom": nom_arbitre
                    }
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.info(
                        f"[INFO] {exc_tb.tb_lineno} L'arbitre assistant vidéo n'a pas pu être récupéré pour le match n°{id_match} : {e} !")
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.info(
                    f"[INFO] {exc_tb.tb_lineno} La récupération des acteurs officiels n'a pas pu être récupéré pour le match n°{id_match} : {e} !")

            # Récupération des compositions et remplaçants des équipes (domicile & extérieur)
            match["domicile"]["compositions"] = scrappCompositions(soup, True, id_match)
            match["exterieur"]["compositions"] = scrappCompositions(soup, False, id_match)

            match["domicile"]["remplacants"] = scrappRemplacants(soup, True, id_match)
            match["exterieur"]["remplacants"] = scrappRemplacants(soup, False, id_match)

            # Récupération des informations des évenements du match (buts, cartons, remplacements)
            scrappEvenements(soup, match)

            frameinfo = getframeinfo(currentframe())
            logging.info(
                f"[INFO] {frameinfo.lineno} Match {id_match} pour le compte la journée n°{num_journee} a bien était scrappé !")
            return match

    else:
        frameinfo = getframeinfo(currentframe())
        logging.info(
            f"[INFO] {frameinfo.lineno} Match {id_match} pour le compte la journée n°{num_journee} déjà enregistré !")


def scrappCompositions(soup, domicile, id_match):
    titulaires = []
    if domicile:
        composition = soup.find("div", {"id": "match-teamcomposition-home"})
        text_domicile = "domicile"
    else:
        composition = soup.find("div", {"id": "match-teamcomposition-away"})
        text_domicile = "exterieur"

    if composition is not None:
        try:
            # Récupération de la liste des titulaires
            titulaires_li = composition.find("span", text=re.compile("lineups", re.I)).findNext().findAll("li")
            # Récupération des informations de chaque joueur titulaire
            for joueur in titulaires_li:
                try:
                    nom_prenom = joueur.find("span", {"class": "MatchTeamComposition-itemName"}).text.strip()
                    nombre_mots_nom_prenom = nom_prenom.split(' ')
                    if len(nombre_mots_nom_prenom) <= 1:
                        nom = nom_prenom
                        prenom = ""
                    else:
                        index = nom_prenom.find(".")
                        if index == -1:
                            try:
                                index = nom_prenom.find(re.findall(r'\b[A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)*\b', nom_prenom)[0])
                            except:
                                index = 0
                        else:
                            index = index + 1

                        nom = nom_prenom[index:].strip()
                        prenom = nom_prenom.replace(nom, '').replace('.', '').strip()

                    numero = int(joueur.find("span", {"class": "MatchTeamComposition-itemPoints"}).text.strip())
                    if numero is not None:
                        j = {
                            "nom": unidecode.unidecode(nom),
                            "prenom": unidecode.unidecode(prenom),
                            "numero": int(numero)
                        }
                        titulaires.append(j)

                        if nom == '':
                            frameinfo = getframeinfo(currentframe())
                            logging.info(
                                f"[DANGER] {frameinfo.lineno} Le joueur {j['numero']} titulaire pour l'équpe ({text_domicile}) pour le match n°{id_match} n'a pas de nom")

                        frameinfo = getframeinfo(currentframe())
                        logging.info(
                            f"[INFO] {frameinfo.lineno} Le joueur {j['nom']} {j['prenom']} ({j['numero']}) a bien été ajouté comme titulaire pour l'équpe ({text_domicile}) pour le match n°{id_match}")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des informations d'un titulaire pour l'équipe ({text_domicile}) pour le match n°{id_match} : {e}")

            frameinfo = getframeinfo(currentframe())
            logging.info(
                f"[INFO] {frameinfo.lineno} La composition pour l'équipe ({text_domicile}) pour le match n°{id_match} a bien été récupérée !")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Aucune liste de titulaires pour l'équipe ({text_domicile}) pour le match n°{id_match} n'a pû être récupéré : {e}")

    else:
        frameinfo = getframeinfo(currentframe())
        logging.info(
            f"[INFO] {frameinfo.lineno} La composition de l'équipe ({text_domicile}) pour le match n°{id_match} n'a pas pû être récupérée !")

    return titulaires


def scrappRemplacants(soup, domicile, id_match):
    remplacants = []
    if domicile:
        composition = soup.find("div", {"id": "match-teamcomposition-home"})
        text_domicile = "domicile"
    else:
        composition = soup.find("div", {"id": "match-teamcomposition-away"})
        text_domicile = "exterieur"

    if composition is not None:
        try:
            # Récupération de la liste des remplacants
            remplacants_li = composition.find("span", text=re.compile("substitutions", re.I)).findNext().findAll("li")
            # Récupération des informations de chaque joueur remplaçant
            for joueur in remplacants_li:
                try:
                    nom_prenom = joueur.find("span", {"class": "MatchTeamComposition-itemName"}).text.strip()
                    nombre_mots_nom_prenom = nom_prenom.split(' ')
                    if len(nombre_mots_nom_prenom) <= 1:
                        nom = nom_prenom
                        prenom = ""
                    else:
                        index = nom_prenom.find(".")
                        if index == -1:
                            try:
                                index = nom_prenom.find(re.findall(r'\b[A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)*\b', nom_prenom)[0])
                            except:
                                index = 0
                        else:
                            index = index + 1

                        nom = nom_prenom[index:].strip()
                        prenom = nom_prenom.replace(nom, '').replace('.', '').strip()
                    numero = int(joueur.find("span", {"class": "MatchTeamComposition-itemPoints"}).text.strip())
                    if numero is not None:
                        j = {
                            "nom": unidecode.unidecode(nom),
                            "prenom": unidecode.unidecode(prenom),
                            "numero": int(numero)
                        }
                        remplacants.append(j)

                        if nom == '':
                            frameinfo = getframeinfo(currentframe())
                            logging.info(
                                f"[INFO] {frameinfo.lineno} Le joueur {j['numero']} remplaçant pour l'équpe ({text_domicile}) pour le match n°{id_match} n'a pas de nom")

                        frameinfo = getframeinfo(currentframe())
                        logging.info(
                            f"[INFO] {frameinfo.lineno} Le joueur {j['nom']} {j['prenom']} ({j['numero']}) a bien été ajouté comme remplaçant pour l'équpe ({text_domicile}) pour le match n°{id_match}")

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des informations d'un remplaçant pour l'équipe ({text_domicile}) pour le match n°{id_match} : {e}")

            frameinfo = getframeinfo(currentframe())
            logging.info(
                f"[INFO] {frameinfo.lineno} Les remplaçants pour l'équipe ({text_domicile}) pour le match n°{id_match} ont bien été récupérés !")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Aucune liste de remplaçant pour l'équipe ({text_domicile}) pour le match n°{id_match} n'a pû être récupéré : {e}")

    else:
        frameinfo = getframeinfo(currentframe())
        logging.info(
            f"[INFO] {frameinfo.lineno} Les remplaçants de l'équipe ({text_domicile}) pour le match n°{id_match} n'ont pas pû être récupérées !")

    return remplacants


def scrappEvenements(soup, match):
    evenements = {
        "remplacements": [],
        "buts": [],
        "cartons": []
    }

    try:
        # Récupération de la liste des évènements du match
        liste_evenements = soup.find("div", {"class": "MatchHeader-timeline"}).findAll("div", {
            "class": "MatchHeader-timelineItem"})
        for evenement in liste_evenements:
            try:
                event = {}
                # Booléen pour savoir si le club concerné est celui à domicile ou non (donc à l'extérieur)
                domicile = "MatchHeader-timelineItem--right" not in evenement["class"]

                # Texte selon l'équipe pour afficher dans les logs
                if domicile:
                    texte_domicile = "domicile"
                else:
                    texte_domicile = "extérieur"

                # Type de l'évenement (remplacement, carton, but)
                type_evenement = None
                # Récupération des classes de l'évenement car contient la class qui va indiquer le type d'évenement
                type_event_icon = evenement.find("div", {"class": "MatchHeader-timelineIconWrapper"}).find("i")["class"]
                # Récupération du type d'évenement en venant récupérer la classe qui indique ce dernier et le supprime
                # une partie du nom de la classe pour récupérer uniquement le nom de l'évènement
                type_icon = [class_type for class_type in type_event_icon if "Icon-" in class_type][0].replace("Icon-",
                                                                                                               "")
                # Récupère les 'p' contenant le nom du ou des joueur(s) concernés par l'évenèment selon le type de ce dernier
                joueurs_concernes = evenement.find("div", {"class": "MatchHeader-timelinePlayer"}).findAll("p")
                # Récupération de la minute de l'évènement
                minute_texte = evenement.find("span", {"class": "MatchHeader-timelineMinutes"}).text
                minute_split = minute_texte.split('+')
                minute = 0
                try:
                    for m in minute_split:
                        minute = minute + int(re.sub('\D', '', m))
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Problème lors de la récupération de la minute d'un évènement du match n°{match['id_match']} !")

                # Selon le type d'évènement
                match type_icon:
                    case "remplacement":
                        type_evenement = "remplacements"
                        joueur_entrant = None
                        joueur_sortant = None
                        for joueur in joueurs_concernes:
                            # Si le joueur est le joueur qui sort
                            if "MatchHeader-timelinePlayerName--sub" in joueur["class"]:
                                try:
                                    # Récupération du nom et prénom
                                    nom_prenom = unidecode.unidecode(joueur.text)
                                    nombre_mots_nom_prenom = nom_prenom.split(' ');
                                    if len(nombre_mots_nom_prenom) <= 1:
                                        joueur_sortant_nom = nom_prenom
                                        joueur_sortant_prenom = ""
                                    else:
                                        index = nom_prenom.find(".")
                                        if index == -1:
                                            try:
                                                index = nom_prenom.find(
                                                    re.findall(r'\b[A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)*\b', nom_prenom)[0])
                                            except:
                                                index = 0
                                        else:
                                            index = index + 1
                                        joueur_sortant_nom = nom_prenom[index:].strip()
                                        joueur_sortant_prenom = nom_prenom.replace(joueur_sortant_nom, '').replace('.', '').strip()

                                    # Récupération des titulaires
                                    if domicile:
                                        titus = match["domicile"]["compositions"]
                                    else:
                                        titus = match["exterieur"]["compositions"]

                                    # Récupération du numéro du joueur correspondant aux informations que l'on a récupérées
                                    try:
                                        joueur_sortant = [j for j in titus if
                                                          j["nom"].lower() == joueur_sortant_nom.lower() and
                                                          ((len(joueur_sortant_prenom) == 1 and j["prenom"][
                                                                                                :1].lower() == joueur_sortant_prenom.lower())
                                                           or (
                                                                   len(joueur_sortant_prenom) > 1 and joueur_sortant_prenom.lower() in
                                                                   j["prenom"].lower())
                                                           or len(joueur_sortant_prenom) == 0)][0]["numero"]
                                    except Exception as e:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        logging.error(
                                            f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la recherche du joueur ({joueur_sortant_nom.upper()} {joueur_sortant_prenom}) sortant à la {minute}e minute pour l'équipe ({texte_domicile}) : {e} !")
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logging.error(
                                        f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la récupération des informations du joueur sortant à la {minute}e minute pour l'équipe ({texte_domicile}) : {e} !")
                            # Si le joueur est le joueur qui rentre
                            else:
                                try:
                                    # Récupération du nom et prénom
                                    nom_prenom = unidecode.unidecode(joueur.text)
                                    nombre_mots_nom_prenom = nom_prenom.split(' ');
                                    if len(nombre_mots_nom_prenom) <= 1:
                                        joueur_entrant_nom = nom_prenom
                                        joueur_entrant_prenom = ""
                                    else:
                                        index = nom_prenom.find(".")
                                        if index == -1:
                                            try:
                                                index = nom_prenom.find(
                                                    re.findall(r'\b[A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)*\b', nom_prenom)[0])
                                            except:
                                                index = 0
                                        else:
                                            index = index + 1

                                        joueur_entrant_nom = nom_prenom[index:].strip()
                                        joueur_entrant_prenom = nom_prenom.replace(joueur_entrant_nom, '').replace('.',
                                                                                                                   '').strip()

                                    # Récupération des remplaçants
                                    if domicile:
                                        remplacants = match["domicile"]["remplacants"]
                                    else:
                                        remplacants = match["exterieur"]["remplacants"]

                                    # Récupération du numéro du joueur correspondant aux informations que l'on a récupérées
                                    try:
                                        joueur_entrant = [j for j in remplacants if
                                                          j["nom"].lower() == joueur_entrant_nom.lower() and
                                                          ((len(joueur_entrant_prenom) == 1 and j["prenom"][
                                                                                                :1].lower() == joueur_entrant_prenom.lower())
                                                           or (
                                                                   len(joueur_entrant_prenom) > 1 and joueur_entrant_prenom.lower() in
                                                                   j["prenom"].lower())
                                                           or len(joueur_entrant_prenom) == 0)][0]["numero"]
                                    except Exception as e:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        logging.error(
                                            f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la recherche du joueur ({joueur_entrant_nom.upper()} {joueur_entrant_prenom}) entrant à la {minute}e minute pour l'équipe ({texte_domicile}) : {e} !")
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logging.error(
                                        f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la récupération des informations du joueur entrant à la {minute}e minute pour l'équipe ({texte_domicile}) : {e} !")
                        # Création de l'évènement
                        event = {
                            "minute": minute,
                            "domicile": domicile,
                            "joueur_sortant": joueur_sortant,
                            "joueur_entrant": joueur_entrant
                        }
                    case "buts":
                        type_evenement = "buts"
                        buteur_num = None
                        penalty = False
                        csc = False
                        # Récupère le type de but pour savoir s'il s'agit d'un pénalty ou csc
                        type_but = evenement.find("span", {"class": "MatchHeader-timelineGoalType"})
                        if type_but is not None:
                            nom_prenom = joueurs_concernes[0].text.replace(type_but.text, '').strip()
                            type_but = type_but.text.strip()
                            match type_but:
                                case "(sp)":
                                    penalty = True
                                case "(og)":
                                    csc = True
                        else:
                            nom_prenom = joueurs_concernes[0].text.strip()

                        try:
                            # Récupération du nom et prénom
                            nom_prenom = unidecode.unidecode(nom_prenom)
                            nombre_mots_nom_prenom = nom_prenom.split(' ')
                            if len(nombre_mots_nom_prenom) <= 1:
                                nom_buteur = nom_prenom
                                prenom_buteur = ""
                            else:
                                index = nom_prenom.find(".")
                                if index == -1:
                                    try:
                                        index = nom_prenom.find(
                                            re.findall(r'\b[A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)*\b', nom_prenom)[0])
                                    except:
                                        index = 0
                                else:
                                    index = index + 1
                                nom_buteur = nom_prenom[index:].strip()
                                prenom_buteur = nom_prenom.replace(nom_buteur, '').replace('.', '').strip()

                            # Récupère les joueurs succeptibles d'avoir marquer (en prenant en compte les csc)
                            joueurs = {}

                            if (domicile and not csc) or (csc and not domicile):
                                joueurs = match["domicile"]["compositions"] + match["domicile"]["remplacants"]
                            elif (not domicile and not csc) or (csc and domicile):
                                joueurs = match["exterieur"]["compositions"] + match["exterieur"]["remplacants"]

                            try:
                                buteur_num = [j for j in joueurs if nom_buteur.lower() in j["nom"].lower() and
                                              ((len(prenom_buteur) == 1 and j["prenom"][
                                                                            :1].lower() == prenom_buteur.lower())
                                               or (len(prenom_buteur) > 1 and prenom_buteur.lower() in j["prenom"].lower())
                                               or len(prenom_buteur) == 0)][0]["numero"]
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logging.error(
                                    f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la recherche du joueur ({nom_buteur.upper()} {prenom_buteur}) marquant à la {minute}e minute pour l'équipe ({texte_domicile}) : {e} !")
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la récupération des informations du joueur marquant à la {minute}e minute pour l'équipe ({texte_domicile}) : {e} !")

                        # Création de l'évènement
                        event = {
                            "minute": minute,
                            "domicile": domicile,
                            "penalty": penalty,
                            "csc": csc,
                            "buteur": buteur_num,
                            "passeur": None
                        }
                    case "card":
                        type_evenement = "cartons"
                        # Récupération la couleur du carton
                        couleur_carton = \
                            [class_type for class_type in type_event_icon if "Icon-card--" in class_type][
                                0].replace(
                                "Icon-card--", "")
                        joueur_num = None
                        try:
                            # Récupération du nom et prénom du joueur qui s'est mangé un carton
                            nom_prenom = unidecode.unidecode(joueurs_concernes[0].text)
                            nombre_mots_nom_prenom = nom_prenom.split(' ');
                            if len(nombre_mots_nom_prenom) <= 1:
                                nom_joueur = nom_prenom
                                prenom_joueur = ""
                            else:
                                index = nom_prenom.find(".")
                                if index == -1:
                                    try:
                                        index = nom_prenom.find(
                                            re.findall(r'\b[A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)*\b', nom_prenom)[0])
                                    except:
                                        index = 0
                                else:
                                    index = index + 1

                                nom_joueur = nom_prenom[index:].strip()
                                prenom_joueur = nom_prenom.replace(nom_joueur, '').replace('.', '').strip()

                            # Récupération des joueurs succeptibles d'être concernés par ce carton
                            if domicile:
                                joueurs = match["domicile"]["compositions"] + match["domicile"]["remplacants"]
                            else:
                                joueurs = match["exterieur"]["compositions"] + match["exterieur"]["remplacants"]

                            try:
                                joueur_num = [j for j in joueurs if
                                              j["nom"].lower() == nom_joueur.lower() and
                                              ((len(prenom_joueur) == 1 and j["prenom"][
                                                                            :1].lower() == prenom_joueur.lower())
                                               or (len(prenom_joueur) > 1 and prenom_joueur.lower() in j["prenom"].lower() or len(
                                                          prenom_joueur) == 0))][
                                    0]["numero"]
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logging.error(
                                    f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la recherche du joueur ({nom_joueur.upper()} {prenom_joueur}) qui s'est mangé un carton à la {minute}e minute pour l'équipe ({texte_domicile}) : {e} !")
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la récupération des informations du joueur qui s'est mangé un carton à la {minute}e minute pour l'équipe ({texte_domicile}) : {e} !")

                        match couleur_carton:
                            case "yellow":
                                couleur_carton = "jaune"
                            case "red":
                                couleur_carton = "rouge"

                        # Création de l'évènement
                        event = {
                            "minute": minute,
                            "domicile": domicile,
                            "joueur": joueur_num,
                            "couleur": couleur_carton
                        }
                # Ajout de l'évènement à la liste de ces derniers
                evenements[type_evenement].append(event)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la récupération des évènements du match n°{match['id_match']} : {e} !")

        # Récupération des passeurs pour les buts
        scrappNumPasseur(soup=soup, evenements=evenements, match=match)

        match["evenements"] = evenements
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(
            f"[ERROR] {exc_tb.tb_lineno} Une erreur s'est produite lors de la récupération des évènements du match n°{match['id_match']} : {e} !")


def scrappNumPasseur(soup, evenements, match):
    try:
        container_live = soup.find("div", {"id": "test"}).find("div").find("div")
        # Trie dans l'ordre décroissant des buts inscrits dans le match
        evenements["buts"].sort(key=lambda but: but["minute"], reverse=True)

        # Liste des évènements détaillés (Texte pour chaque gros évènements)
        evenements_container = soup.find("div", {"class": "event-item"}).findParent()

        # Joueurs des équipes domicile et extérieur (titus et remplaçants)
        domicile_joueurs = match["domicile"]["compositions"] + match["domicile"]["remplacants"]
        exterieur_joueurs = match["exterieur"]["compositions"] + match["exterieur"]["remplacants"]

        # Récupération des imgs dans la liste d'évènement correspondants à un but
        liste_event_buts = evenements_container.findAll("img", {
            "src": "/-/media/Project/LFP/Site-factory/Global-icons/Timeline/But.png"})

        events = []

        # Récupération, pour chaque évènement correspondant à un but dans la liste d'évènement, de la minute ainsi que le
        # texte correspondant au passeur (phrase commençant par Assisted By) (Pitié ne changez pas ça @Ligue1)
        j = 0;
        for event in liste_event_buts:
            j = j + 1
            minute_item = None
            texte = None
            try:
                event_item = event.findParent("div", {"class": "event-item"})
                try:
                    minute_item = int(event_item.find("div", {"class": "minute"}).text.strip())
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Problème lors de la tentative de récupération de la minute d'un but du match {match['id_match']} ({j}) : {e} !")

                try:
                    texte = event_item.find("p").text
                    texte = texte[texte.index("Assisted by") + len("Assisted by"):]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Problème lors de la tentative de récupération du texte du passeur  d'un but du match {match['id_match']} ({j}, min : {minute_item}) : {e} !")

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Problème lors de la tentative de récupération de la div de l'event d'un but du match {match['id_match']} ({j}) : {e} !")

            events.append({
                "minute": minute_item,
                "texte": texte
            })

        # Trie dans l'ordre décroissant des buts inscrits dans le match
        events.sort(key=lambda ev: ev["minute"], reverse=True)

        i = 0

        for ev in events:
            # Récupération du ième dernier but récupéré précédemment, qui normalement, correspond à l''ev' que l'on est
            # entrain de traiter
            but = evenements["buts"][i]
            t = ev["texte"]
            # Vérification que les deux évènements correspondent au même (Une minute de différence entre le détails des
            # évènements et celui affiché dans le header donc on met 2 minutes pour être un peu plus large)
            if abs(but["minute"] - ev["minute"]) <= 2 and not but["penalty"] and not but["csc"]:
                mots = t.split()
                passeur = None
                prenom = None
                nom = None
                j = 0
                while passeur is None and j < len(mots):
                    mot = mots[j]
                    # Si le mot à une majuscule (on déduit qu'il s'agit du prénom ou nom)
                    if mot[0].isupper():
                        # Récupération des joueurs succeptibles de correspondre
                        if but["domicile"]:
                            joueurs = domicile_joueurs
                        else:
                            joueurs = exterieur_joueurs

                        # Si aucun prénom n'a été récupéré
                        if prenom is None:
                            prenom = unidecode.unidecode(mot)

                            # Récupération des joueurs correspondants au prénom
                            joueurs_correspondants = [j for j in joueurs if prenom.lower() in j["prenom"].lower()]

                            # Si un seul joueur correspond, on part du principe qu'il s'agit du passeur
                            if len(joueurs_correspondants) == 1:
                                passeur = joueurs_correspondants[0]["numero"]
                            # Si aucun joueur ne correspond, il se peut qu'il s'agit de son nom (ex: Gerson)
                            elif len(joueurs_correspondants) == 0:
                                nom = prenom
                                # Récupération des joueurs correspondants au nom
                                joueurs_correspondants = [j for j in joueurs if nom.lower() in j["nom"].lower()]
                                # Si un seul joueur correspond, on part du principe qu'il s'agit du passeur
                                if len(joueurs_correspondants) == 1:
                                    passeur = joueurs_correspondants[0]["numero"]
                        else:
                            nom = unidecode.unidecode(mot)

                            # Récupération des joueurs correspondants au nom
                            joueurs_correspondants = [j for j in joueurs if nom.lower() in j["nom"].lower()]
                            # Si un seul joueur correspond, on part du principe qu'il s'agit du passeur
                            if len(joueurs_correspondants) == 1:
                                passeur = joueurs_correspondants[0]["numero"]
                    j = j + 1
                if passeur is None:
                    frameinfo = getframeinfo(currentframe())
                    logging.info(
                        f"[INFO] {frameinfo.lineno} Aucun passeur pour le but à la {but['minute']} du match n°{match['id_match']} !")

                # Ajout du passeur au but que l'on vient de traité
                evenements["buts"][i]["passeur"] = passeur
            else:
                frameinfo = getframeinfo(currentframe())
                if but["penalty"] or but["csc"]:
                    logging.info(
                        f"[INFO] {frameinfo.lineno} Aucun passeur pour ce but {but['minute']}, puisqu'il s'agit d'un pénalty ({but['penalty']}) ou d'un csc ({but['csc']}) !")
                else:
                    logging.error(
                        f"[ERROR] {frameinfo.lineno} Les deux évènements ont plus de 2 minutes d'écart (Détail : {ev['minute']}; Header: {but['minute']}) !")

            i = i + 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(
            f"[ERROR] {exc_tb.tb_lineno} Problème lors de la tentative de récupération des passeurs  des buts du match {match['id_match']} : {e} !")


scrappMatchsLigue1()
