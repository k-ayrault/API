import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import validators
import scrapp_func_global
import copy


def getIdClubsPresent():
    for club in scrapp_func_global.all_clubs:
        scrapp_func_global.all_clubs_id.append(club["id_transfermarkt"])


def getClubsLigue1():
    result = requests.get(scrapp_func_global.transfermarkt_base_url + scrapp_func_global.link_classement_ligue_1,
                          headers=scrapp_func_global.headers)
    clubs = []
    if (result.ok):
        soup = BeautifulSoup(result.text, "html.parser")
        classement = soup.find("div", {"id": "yw1"}).find("table")
        tds = classement.find("tbody").findAll("tr")
        for td in tds:
            href = td.find("a")['href']
            link = scrapp_func_global.transfermarkt_base_url + href
            link = link.replace(scrapp_func_global.transfermarkt_accueil_club,
                                scrapp_func_global.transfermarkt_url_replace)
            match = (re.search("/verein/", link))
            name = href[href.find("/") + 1 : href.find("/" + scrapp_func_global.transfermarkt_accueil_club)]
            id = link[match.end():]
            id = id[:id.find("/")]
            clubs.append({"id": id, "link": link, "name" : name})
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
            "logos": [],
            "stade": {}
        }
        if result.ok:
            soup = BeautifulSoup(result.text, "html.parser")
            # Récupération de la div contenant ces infos
            row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
            box_info = row.find(text=re.compile(scrapp_func_global.transfermarkt_box_info_club_find))
            if box_info is not None:
                box_info = box_info.find_parent("div", {
                    "class": "info-header"}).find_parent("div", {"class": "box"})

                nom_club = box_info.find("th", text=re.compile(scrapp_func_global.transfermarkt_nom_club_find))
                if nom_club is not None:
                    nom_club = nom_club.find_parent().find("td").text
                    if nom_club is not None:
                        club["nom"] = nom_club
                pays_club = box_info.find("th", text=re.compile(scrapp_func_global.transfermarkt_adresse_club_find))
                if pays_club is not None:
                    pays_club = pays_club.find_parent().find_next_sibling().find_next_sibling().find("td").text
                    if pays_club is not None:
                        club["pays"] = triNation(pays_club)

                site_club = box_info.find("th", text=re.compile(scrapp_func_global.transfermarkt_site_club_find))
                if site_club is not None:
                    site_club = site_club.find_parent().find("a")["href"]
                    if site_club is not None:
                        club["site"] = site_club

                creation_club = box_info.find("th", text=re.compile(scrapp_func_global.transfermarkt_annee_club_find))
                if creation_club is not None:
                    creation_club = creation_club.find_parent().find("td").text
                    if creation_club is not None:
                        creation_club = datetime.strptime(creation_club.strip(), '%d %b %Y')
                        if creation_club is not None:
                            club["creation"] = creation_club.date().isoformat()

                couleurs_club = []
                couleurs = box_info.find("th", text=re.compile(scrapp_func_global.transfermarkt_couleurs_club_find))
                if couleurs is not None:
                    couleurs = couleurs.find_parent().find("td").find("p")
                    for couleur in couleurs.findAll():
                        match = (re.search("background-color:", couleur["style"]))
                        couleur = couleur["style"][match.end():-1]
                        couleurs_club.append(couleur)
                    if couleurs_club is not None:
                        club["couleurs"] = couleurs_club

                logos_club = []
                logos = soup.find("h2", text=re.compile(scrapp_func_global.transfermarkt_logo_club_find))
                if logos is not None:
                    logos = logos.find_parent("div", {"class": "box"}).findAll("img")
                    for logo in logos:
                        if validators.url(logo["src"]):
                            logos_club.append(logo["src"])
                    if logos_club is not None:
                        club["logos"] = logos_club

                club["stade"] = getInfoStadeClub(club_to_scrapp)
                scrapp_func_global.all_clubs.append(club)
                scrapp_func_global.all_clubs_id.append(club["id_transfermarkt"])


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
        row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})

        nom_stade = row.find("th", text=re.compile(scrapp_func_global.transfermarkt_nom_stade_find))
        if nom_stade is not None:
            nom_stade = nom_stade.find_parent().find("td").text
            if nom_stade is not None:
                stade["nom"] = nom_stade

        box_info = row.find("h1", text=re.compile(stade["nom"]))
        if box_info is not None:
            box_info = box_info.find_parent("div", {"class": "box"})
            if box_info is not None:
                capacite = box_info.find("th", text=re.compile(scrapp_func_global.transfermarkt_capacite_stade_find))
                if capacite is not None:
                    capacite = capacite.find_parent().find("td").text
                    if capacite is not None:
                        stade["capacite"] = int(capacite.replace('.', ''))

                construction = box_info.find("th", text=re.compile(
                    scrapp_func_global.transfermarkt_construction_stade_find))
                if construction is not None:
                    construction = construction.find_parent().find("td").text
                    if construction is not None:
                        stade["construction"] = int(construction)

                images_stade = []
                images = box_info.findAll("img")
                if images is not None:
                    for logo in images:
                        if validators.url(logo["src"]):
                            images_stade.append(logo["src"])
                    if images_stade is not None:
                        stade["images"] = images_stade

        box_adresse = row.find("h2", text=re.compile(scrapp_func_global.transfermarkt_box_adresse_stade_find))
        if box_adresse is not None:
            box_adresse= box_adresse.find_parent("div", {
                "class": "box"})
            tr_adresse = box_adresse.find("th",
                                          text=re.compile(scrapp_func_global.transfermarkt_adresse_stade_find)).find_parent(
                "tr")
            adresse = tr_adresse.find("td").text.strip()
            tr_adresse = tr_adresse.find_next_sibling("tr")
            th_text = tr_adresse.find("th").text
            while th_text == "" and tr_adresse is not None:
                adresse += ", " + tr_adresse.find("td").text.strip()
                tr_adresse = tr_adresse.find_next_sibling("tr")
                if tr_adresse is not None:
                    th_text = tr_adresse.find("th").text
            if adresse is not None:
                stade["adresse"] = adresse

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
        tr_joueurs = table_effectif.find("tbody").findAll("td", {"class": "posrela"})
        for tr_joueur in tr_joueurs:
            link = tr_joueur.find("table").find("a")["href"]
            link = link.replace(scrapp_func_global.transfermarkt_info_joueur,
                                scrapp_func_global.transfermarkt_url_replace)
            match = (re.search("/spieler/", link))
            id = link[match.end():]
            joueur = {"id": id, "link": scrapp_func_global.transfermarkt_base_url + link}
            joueurs.append(joueur)
            getInfoJoueur(joueur)

    return joueurs

def getInfoJoueur(joueur_to_scrapp):
    id_transfermarkt = joueur_to_scrapp["id"]
    if id_transfermarkt not in scrapp_func_global.all_joueurs_id:
        # "Création" du lien du club où sont les infos de ce dernier
        link = joueur_to_scrapp["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                                scrapp_func_global.transfermarkt_info_joueur)
        result = requests.get(link, headers=scrapp_func_global.headers)
        joueur = {
            "id_transfermarkt": joueur_to_scrapp["id"],
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
            "contrats": []
        }
        if result.ok:
            soup = BeautifulSoup(result.text, "html.parser")
            # Récupération de la div contenant ces infos
            header = soup.find("main").find("header", {"class": "data-header"})

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

            row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
            info_table = row.find("div", {"class": "info-table"})

            nom_complet = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_nom_joueur_find))
            if nom_complet is not None:
                joueur["nom_complet"] = nom_complet.find_parent().find_next_sibling().text
            else:
                joueur["nom_complet"] = joueur["prenom"] + " " + joueur["nom"]

#             print(" - " + joueur["nom_complet"] + " : En cours")
            naissance = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_naissance_joueur_find))
            if naissance is not None:
                naissance = naissance.find_parent().find_next_sibling().find("a").text
                if naissance is not None:
                    naissance = datetime.strptime(naissance.strip(), '%d %b %Y')
                    if naissance is not None:
                        joueur["date_naissance"] = naissance.date().isoformat()

            nationalite = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_nationalite_joueur_find))
            if nationalite is not None:
                nationalite = nationalite.find_parent().find_next_sibling()
                if nationalite is not None:
                    for img in nationalite.findAll("img") :
                        img.decompose()
                    for pays in nationalite.contents:
                        if pays is not None and isinstance(pays, str):
                            if pays.strip() != '':
                                pays = triNation(pays.strip())
                                joueur["pays"].append(pays)

            pied = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_pied_joueur_find))
            if pied is not None:
                joueur["pied"] = pied.find_parent().find_next_sibling().text

            taille = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_taille_joueur_find))
            if taille is not None:
                joueur["taille"] = re.sub('\D', '', taille.find_parent().find_next_sibling().text)

            equipementier = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_equipementier_joueur_find))
            if equipementier is not None:
                joueur["equipementier"] = equipementier.find_parent().find_next_sibling().text

            box_positions = soup.find("div", {"class": "detail-position__matchfield"})
            if box_positions is not None:
                span_positions_principales = box_positions.findAll("span", {"class": "position__primary"})
                positions_principales = []
                if span_positions_principales is not None:
                    for span_position_principale in span_positions_principales:
                        position = -1
                        i = len(span_position_principale["class"]) - 1
                        while position == -1 and i > 0:
                            css_class = span_position_principale["class"][i]
                            if css_class.startswith(scrapp_func_global.class_css_position_principale_start):
                                position = css_class.replace(scrapp_func_global.class_css_position_principale_start, '')
                                if not position.isdigit():
                                    position = -1
                                else:
                                    positions_principales.append(int(position))
                            i -= 1
                joueur["positions_principales"] = positions_principales

                span_positions_secondaires = box_positions.findAll("span", {"class": "position__secondary"})
                positions_secondaires = []
                if span_positions_secondaires is not None:
                    for span_position_secondaire in span_positions_secondaires:
                        position = -1
                        i = len(span_position_secondaire["class"]) - 1
                        while position == -1 and i > 0:
                            css_class = span_position_secondaire["class"][i]
                            if css_class.startswith(scrapp_func_global.class_css_position_secondaire_start):
                                position = css_class.replace(scrapp_func_global.class_css_position_secondaire_start, '')
                                if not position.isdigit():
                                    position = -1
                                else:
                                    positions_secondaires.append(int(position))
                            i -= 1
                joueur["positions_secondaires"] = positions_secondaires

            fin_contrat = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_fin_contrat_pret_find))
            date_fin_contrat = None
            if fin_contrat is None:
                fin_contrat = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_fin_contrat_find))
            if fin_contrat is not None:
                fin_contrat = fin_contrat.find_parent().find_next_sibling().text
                if fin_contrat is not None:
                    fin_contrat = datetime.strptime(fin_contrat.strip(), '%d %b %Y')
                    if fin_contrat is not None:
                        date_fin_contrat = fin_contrat.date().isoformat()

            contrats = getContratsJoueur(joueur_to_scrapp, date_fin_contrat)
            if contrats is not None:
                joueur["contrats"] = contrats

            scrapp_func_global.all_joueurs.append(joueur)
            scrapp_func_global.all_joueurs_id.append(joueur["id_transfermarkt"])
    else:
        # "Création" du lien du club où sont les infos de ce dernier
        link = joueur_to_scrapp["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                                scrapp_func_global.transfermarkt_info_joueur)
        result = requests.get(link, headers=scrapp_func_global.headers)
        if result.ok:
            soup = BeautifulSoup(result.text, "html.parser")
            row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
            info_table = row.find("div", {"class": "info-table"})

            fin_contrat = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_fin_contrat_pret_find))
            date_fin_contrat = None
            if fin_contrat is None:
                fin_contrat = info_table.find(text=re.compile(scrapp_func_global.transfermarkt_fin_contrat_find))
            if fin_contrat is not None:
                fin_contrat = fin_contrat.find_parent().find_next_sibling().text
                if fin_contrat is not None and bool(re.match('^[0-9]{1,2} [A-zÀ-ÿ.]{4,5} [0-9]{4}$', fin_contrat)):
                    fin_contrat = datetime.strptime(fin_contrat.strip(), '%d %b %Y')
                    if fin_contrat is not None:
                        date_fin_contrat = fin_contrat.date().isoformat()
            joueur = next((x for x in scrapp_func_global.all_joueurs if x["id_transfermarkt"] == id_transfermarkt),
                          None)
#             print(" - " + joueur["nom_complet"] + " : En cours")
            if "contrats" not in joueur or joueur["contrats"] is None or len(joueur["contrats"]) == 0:
                contrats = getContratsJoueur(joueur_to_scrapp, date_fin_contrat)
                joueur["contrats"] = contrats
            else:
                majContratsJoueur(joueur, joueur_to_scrapp, date_fin_contrat)
#     print(" - " + joueur["nom_complet"] + " : Save")

def getContratsJoueur(joueur_to_scrapp, date_fin_contrat):
    # "Création" du lien du joueur où sont les transfert de ce dernier
    link = joueur_to_scrapp["link"].replace(scrapp_func_global.transfermarkt_url_replace,
                                            scrapp_func_global.transfermarkt_transferts_joueur)
    result = requests.get(link, headers=scrapp_func_global.headers)
    if result.ok:
        soup = BeautifulSoup(result.text, "html.parser")
        row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
        titre_tableau_transferts = row.find("h2",
                                            text=re.compile(scrapp_func_global.transfermarkt_historique_transfert_find))
        tableau_transferts = titre_tableau_transferts.find_parent()

        lignes = tableau_transferts.findAll("div", {"class": scrapp_func_global.transfermarkt_class_transfert_ligne})
        lignes = [ligne for ligne in lignes if len(ligne["class"]) == 1]
        lignes = lignes[::-1]

        index_ligne_transfert = 0
        contrats = []
        while index_ligne_transfert < len(lignes):
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
#                         print (" - - " + pret["club"] + " : Prêt")
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
#             print (" - - " + contrat["club"] + " : Transfert")
            if club_entrant_nom == "Pause carrière" or club_entrant_nom == "Fin de carrière":
                index_ligne_transfert += 1
        contrats.sort(key=lambda x: x["debut"], reverse=True)
        return contrats
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
        row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
        titre_tableau_transferts = row.find("h2",
                                            text=re.compile(scrapp_func_global.transfermarkt_historique_transfert_find))
        tableau_transferts = titre_tableau_transferts.find_parent()

        lignes = tableau_transferts.findAll("div", {"class": scrapp_func_global.transfermarkt_class_transfert_ligne})
        lignes = [ligne for ligne in lignes if len(ligne["class"]) == 1]
        lignes = lignes[::-1]

        index_ligne_transfert = 0
        while index_ligne_transfert < len(lignes):
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
#                             print (" - - " + pret["club"] + " : Prêt")
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
                        index_ligne_transfert+=1
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
#                                 print (" - - " + pret["club"] + " : Prêt")
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
#                                 print (" - - " + pret["club"] + " : Prêt")
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
#                     print (" - - " + contrat["club"] + " : Transfert")
                    if club_entrant_nom == "Pause carrière" or club_entrant_nom == "Fin de carrière":
                        index_ligne_transfert += 1
                else:
                    index_ligne_transfert += 1
        contrats.sort(key=lambda x: x["debut"], reverse=True)
        return contrats


def getMontantTransfertLigne(ligne):
    montant = 0
    montant_transfert = ligne.find("div", {"class": scrapp_func_global.transfermarkt_class_transfert_ligne + "__fee"})
    if montant_transfert is not None:
        montant = montant_transfert.text.strip()
    return montant


def getDateTransfertLigne(ligne):
    date = ""
    date_transfert = ligne.find("div", {"class": scrapp_func_global.transfermarkt_class_transfert_ligne + "__date"})
    if date_transfert is not None:
        date_transfert = date_transfert.text.strip()
        if date_transfert is not None:
            date_transfert = datetime.strptime(date_transfert, "%d %b %Y")
            if date_transfert is not None:
                date = date_transfert.date().isoformat()
    return date


def getClubEntrantLigne(ligne):
    club_entrant_div = ligne.find("div",
                                  {"class": scrapp_func_global.transfermarkt_class_transfert_ligne + "__new-club"})
    club = {"id": -1, "nom": ""}
    if club_entrant_div is not None:
        club["nom"] = club_entrant_div.text.strip()
    if club["nom"] != "Fin de carrière" and club["nom"] != "Pause carrière" and club["nom"] != "":
        link_club = club_entrant_div.find("a")
        if link_club is not None:
            link_club = link_club["href"]
            link_club = link_club[:link_club.find("/saison_id/")]
            match = (re.search("/verein/", link_club))
            id = link_club[match.end():]
            club["id"] = id
            link_club = link_club.replace(scrapp_func_global.transfermarkt_transferts_joueur,
                                          scrapp_func_global.transfermarkt_url_replace)
            getInfoClub({"id": id, "link": scrapp_func_global.transfermarkt_base_url + link_club})
    return club


def getClubPartantLigne(ligne):
    club_sortant_div = ligne.find("div",
                                  {"class": scrapp_func_global.transfermarkt_class_transfert_ligne + "__old-club"})
    club = {"id": -1, "nom": ""}
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
            getInfoClub({"id": id, "link": scrapp_func_global.transfermarkt_base_url + link_club})
    return club


def getContratPret(lignes, index_ligne, ligne, page):
    montant = getMontantTransfertLigne(ligne)
    # S'il s'agit du début d'un prêt
    if re.search("prêt", montant, re.IGNORECASE) and montant != "Fin du prêt":
        contrat = copy.deepcopy(scrapp_func_global.contrat_vide)
        club_entrant = getClubEntrantLigne(ligne)
        contrat["club"] = club_entrant["id"]
        contrat["debut"] = getDateTransfertLigne(ligne)
        contrat["pret"] = True
        club_partant = getClubPartantLigne(ligne)
        while index_ligne < len(lignes) and (montant != "Fin du prêt" and club_partant != club_entrant):
            ligne = lignes[index_ligne]
            montant = getMontantTransfertLigne(ligne)
            club_partant = getClubPartantLigne(ligne)
            index_ligne += 1
        index_ligne -= 1
        contrat["fin"] = getDateTransfertLigne(ligne)
        return contrat
    return None


def correctFormatDate(date):
    return bool(re.match('^[0-9]{1,2} [A-zÀ-ÿ.]{4,5} [0-9]{4}$', date))


def montantToInt(montant) :
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
    except ValueError:
        pass
    return 0

def triNation(pays) :
    if pays is not None:
        if pays == 'Angleterre':
            return 'Royaume-Uni'
    return pays