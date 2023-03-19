from scrapp_func_global import *

# TODO vérifier date de fin contrat club qui prête actuellement un joueur

"""
    Fonction permettant de récupérer les clubs présent en Ligue 1 cette saison.
    Entrée :
    Sortie :
        - clubs, tableau contenant les clubs de Ligue 1 avec leur id transfermarkt ("id"), leur lien transfermarkt ("lien") ainsi que leur nom ("nom")
"""
def getClubsLigue1():
    # Lien vers la page TransferMarkt du classement de Ligue 1.
    url_classement_transfermarkt_ligue_1 = transfermarkt_base_url + link_classement_ligue_1

    # Résultat de la requête HTTP vers la page TransferMarkt du classement de Ligue 1.
    result = requests.get(url=url_classement_transfermarkt_ligue_1,
                          headers=headers)

    # Tableau allant contenir les clubs de Ligue 1.
    clubs = []

    # Si on a réussi à accéder à la page
    if (result.ok):
        # Transformation du code HTML de la page en objet BeautifulSoup
        soup = BeautifulSoup(result.text, "html.parser")

        try:
            
            # Table HTML correspondant au classement
            classement = soup.find("div", {"id": "yw1"}).find("table")
            
            # Tableau des lignes du classement correspondant aux différents clubs de ligue 1
            clubs_tds = classement.find("tbody").findAll("tr")

            # On traite chaque club
            for club_td in clubs_tds:
                
                try:
                    
                    # Récupération du href correspondant au lien vers la page TransferMarkt du club
                    href = club_td.find("a")['href']
                    # Création du lien complet vers la page TransferMarkt du club à
                    lien_club = transfermarkt_base_url + href
                    # Formattage du lien, afin de pouvoir accéder à n'importe quel page d'information lié au club en remplaçant 'transfermarkt_url_replace' par le mot clé correspondant à l'information que l'on souhaite
                    lien_club = lien_club.replace(transfermarkt_accueil_club,
                                        transfermarkt_url_replace)

                    # Récupération du nom du club présent dans le lien
                    nom_club = href[href.find("/") + 1: href.find("/" + transfermarkt_accueil_club)]

                    # Récupération de la fin du lien contenant l'id
                    fin_lien_club = lien_club[lien_club.find("/verein/") + len("/verein/"):]
                    
                    # Récupération de l'index dans 'fin_lien_club' correspondant au caractère suivant l'id du club
                    char_apres_id = fin_lien_club.find("/") if fin_lien_club.find("/") else len(fin_lien_club)
                    id_club = fin_lien_club[:char_apres_id]

                    # Création du club avec les informations récupérées
                    club = {"id": id_club, "lien": lien_club, "nom": nom_club}
                    
                    # Ajout du club récupéré dans le tableau des clubs de Ligue 1
                    clubs.append(club)
                
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Problème au niveau de la récupération de l'id, nom et lien du club : {e} !")
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Le classement de la ligue 1 n'a pu être récupéré dans le DOM : {e} !")
    
    return clubs


"""
    Fonction permettant de scrapper divers informations du club en entrée de la fonction, si on ne les a pas déjà scrappées dans le passé
    Entrée:
        - club_transfermarkt, objet contenant les informations "d'identification" TransferMarkt du club dont on veut scrapp ("id", "lien" et "nom")
    Sortie:
        - club, informations scrapp du club
"""
def getInfoClub(club_transfermarkt):
    # Récupération de l'identifiant du club dont on veut scrapp ces informations
    id_club_transfermarkt = club_transfermarkt["id"]
    # On vérifie si les informations du club n'ont pas déjà été scrapp
    if id_club_transfermarkt not in id_transfermarkt_clubs_deja_scrapp:
        # "Création" du lien du club où sont les infos de ce dernier
        link = club_transfermarkt["lien"].replace(transfermarkt_url_replace,
                                              transfermarkt_info_club)
        # Résultat de la requête HTTP vers la page TransferMarkt des informations du club
        result = requests.get(link, headers=headers)

        # Vérification que la requête HTTP s'est bien passée
        if result.ok:         
            # Initialisation de l'objet allant contenir les informations du club
            club = {
                "id_transfermarkt": id_club_transfermarkt,
                "nom": '',
                "pays": '',
                "site": '',
                "creation": '',
                "couleurs": [],
                "logo_principal": '',
                "logos": [],
                "stade": {}
            }

            # Transformation du code HTML de la page en objet BeautifulSoup
            soup = BeautifulSoup(result.text, "html.parser")
            try:
                # Récupération du bandeau bleu de navigation du club
                subnavi = soup.find("div", {"id": "subnavi"})

                # Récupération de la div contenant toutes les informations que l'on souhaite
                row = subnavi.find_next_sibling("div", {"class": "row"})
                
                # Récupération des informations générales du club
                try:
                    # Récupération de la div contenant les informations du club
                    h2_box_info = row.find("h2", text=re.compile(transfermarkt_box_info_club_find))
                    box_info = h2_box_info.find_parent("div", {"class": "box"}).find("div", {"class": "content"})

                    # Récupération du nom du club
                    try:
                        # Récupération de la ligne contenant le nom du club
                        ligne_nom_club = box_info.find("th", text=re.compile(transfermarkt_nom_club_find)).find_parent("tr")
                        # Récupération du nom du club
                        nom_club = ligne_nom_club.find("td").text.strip()
                        club["nom"] = nom_club
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du nom "
                            f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) dans le DOM : {e} !")

                    # Récupération du pays où le club est
                    try:
                        # Récupération de la ligne où l'adresse du club est
                        ligne_adresse_club = box_info.find("th",
                                                  text=re.compile(transfermarkt_adresse_club_find)).find_parent("tr")
                        # Récupération de la ligne où le pays est, en déduisant qu'il s'agit de la troisième ligne de l'adresse donc deux tr plus loin que le premier de l'adresse
                        ligne_pays_club = ligne_adresse_club.find_next_sibling().find_next_sibling()
                        # On déduit que le pays du club est au troisième tr de l'adresse
                        pays_club = ligne_pays_club.find("td").text

                        club["pays"] = triNation(pays_club)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du pays "
                            f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) dans le DOM : {e} !")

                    # Récupération du site du club
                    try:
                        # Récupération de la ligne où est présent le site du club
                        ligne_site_club = box_info.find("th",
                                                  text=re.compile(transfermarkt_site_club_find)).find_parent("tr")
                        # Récupération du lien vers le site du club
                        site_club = ligne_site_club.find("a")["href"]

                        club["site"] = site_club
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du site "
                            f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) dans le DOM : {e} !")

                    # Récupération de la date de création du club
                    try:
                        # Récupération de la ligne contenant la date de création du club
                        ligne_creation_club = box_info.find("th",
                                                      text=re.compile(transfermarkt_annee_club_find)).find_parent("tr")
                        # Récupération de la chaîne de caractère de la création du club
                        str_creation_club = ligne_creation_club.find("td").text
                        # Format de la date de création
                        format_datetime_creation_club = "%d %b %Y"
                        # Création de la datetime correspondant à la date de création du club
                        datetime_creation_club = datetime.strptime(str_creation_club.strip(), format_datetime_creation_club)
                        # Date de la création du club au format ISO 8601 
                        iso_date_creation_club = datetime_creation_club.date().isoformat()
                        
                        club["creation"] = iso_date_creation_club
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de de la "
                            f"date de création du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) dans le DOM : {e} !")

                    # Récupération des couleurs du club
                    couleurs_club = []
                    try:
                        # Récupération de la ligne contenant les couleurs du clubs
                        ligne_couleurs_clubs = box_info.find("th",
                                                 text=re.compile(transfermarkt_couleurs_club_find)).find_parent("tr")
                        # Récupération des "blocs" ayant comme background-color, les couleurs du clubs
                        blocs_couleurs_club = ligne_couleurs_clubs.find("td").find("p").find_all("span")

                        # Traitement de chaque bloc pour récupérer la couleur du club
                        for couleur in blocs_couleurs_club:
                            try:
                                # Récupération de l'index où est normalement la couleur 
                                index_couleur_style = (re.search("background-color:", couleur["style"])).end()
                                # Récupération de la couleur du bloc 
                                couleur = couleur["style"][index_couleur_style:-1]
                                # On ajoute la couleur à celles du club si cette dernière existe
                                if couleur != '':
                                    couleurs_club.append(couleur)
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logging.error(
                                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une couleur "
                                    f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) dans le DOM : {e} !")
                        club["couleurs"] = couleurs_club
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des couleurs  "
                            f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) dans le DOM : {e} !")

                    # Récupération du logo actuel du club
                    try:
                        # Récupération de la div contenant l'image
                        div_logo = box_info.find("div", {"class" : "datenfakten-wappen"})
                        # Récupération du logo 
                        logo = div_logo.find("img")["src"]
                        # Vérification que l'url vers le logo est valide
                        if validators.url(logo):
                            club["logo_principal"] = logo
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du logo actuel "
                            f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) dans le DOM : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des "
                        f"informations du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")

                # Récupération des anciens logos du club
                logos_club = []
                try:
                    # Récupération du titre indiquant les anciens logos
                    h2_anciens_logos = soup.find("h2", text=re.compile(transfermarkt_logo_club_find))
                    # Récupération du bloc contenant les anciens logos 
                    bloc_anciens_logos = h2_anciens_logos.find_parent("div", {"class": "box"})
                    # Récupération de tous les anciens logos
                    logos = bloc_anciens_logos.findAll("img")
                    # Vérificatiopn de la validité des logos
                    for logo in logos:
                        try:
                            # Vérification que src soit bien un lien afin de ne pas récupérer uniquement un chemin sur un serv par ex.
                            if validators.url(logo["src"]):
                                logos_club.append(logo["src"])
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'un ancien logo "
                                f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des anciens logos "
                        f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")

                club["logos"] = logos_club
                
                club["stade"] = getInfoStadeClub(club_transfermarkt)
                
                clubs_scrapp.append(club)
                
                id_transfermarkt_clubs_deja_scrapp.append(club["id_transfermarkt"])

                return club
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des informations "
                    f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")
    else:
        frameinfo = getframeinfo(currentframe())
        logging.info(
            f"[INFO] {frameinfo.lineno} Le club {club_transfermarkt['nom']} est déjà récupéré !")

"""
    Fonction permettant de scrapper divers informations sur le stade du club en entrée de la fonction
    Entree :
        - club, objet contenant les informations "d'identification" ("id", "lien" et "nom") TransferMarkt du club dont on veut scrapp les informations de son stade        
    Sortie :
        - stade, informations scrapp du stade
"""
def getInfoStadeClub(club_transfermarkt):

    link = club_transfermarkt["lien"].replace(transfermarkt_url_replace,
                                transfermarkt_info_stade)
    result = requests.get(link, headers=headers)
    if result.ok:
        # Initialisation de l'objet allant contenir les informations du club
        stade = {
            'nom': '',
            'capacite': 0,
            'construction': 0000,
            'adresse': '',
            'images': []
        }
        # Transformation du code HTML de la page en objet BeautifulSoup
        soup = BeautifulSoup(result.text, "html.parser")

        # Récupération de la div contenant ces infos
        try:
            # Récupération du bandeau bleu de navigation du club
            subnavi = soup.find("div", {"id": "subnavi"})

            # Récupération de la div contenant toutes les informations que l'on souhaite
            row = subnavi.find_next_sibling("div", {"class": "row"})
            
            # Récupération du nom du stade
            try:
                # Récupération de la ligne contenant le nom du stade
                ligne_nom_stade = row.find("th", text=re.compile(transfermarkt_nom_stade_find)).find_parent("tr")
                # Récupération du nom du stade
                nom_stade = ligne_nom_stade.find("td").text
                stade["nom"] = nom_stade
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du nom du stade "
                    f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")

            # Récupération de la div contenant les informations du stade via le nom de ce dernier
            h1_box_info = row.find("h2", text=re.compile(stade["nom"]))
            box_info = h1_box_info.find_parent("div", {"class": "box"})

            # Récupération de la capacité du stade
            try:
                # Récupération de la ligne correspondant à la capacité du stade
                ligne_capacite_stade = box_info.find("th", text=re.compile(transfermarkt_capacite_stade_find)).find_parent("tr")
                # Récupération de la capacité du stade
                capacite = ligne_capacite_stade.find("td").text
                 
                stade["capacite"] = int(capacite.replace('.', ''))
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la capacité du stade "
                    f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")

            # Récupération de l'année de construction du stade
            try:
                # Récupération de la ligne contenant l'année de construction du stade
                ligne_construction_stade = box_info.find("th", text=re.compile(
                    transfermarkt_construction_stade_find)).find_parent("tr")
                # Récupérationd de l'année de construction du stade
                construction = ligne_construction_stade.find("td").text
                stade["construction"] = int(construction)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de l'année de "
                    f"construction du stade du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")

            # Tableau allant contenir les image du stade
            images_stade = []
            try:
                # Récupération de toutes les images du stade
                images = box_info.findAll("img")
                # Récupération de chaque url 
                for logo in images:
                    try:
                        # Vérification que l'url vers l'image est valide
                        if validators.url(logo["src"]):
                            images_stade.append(logo["src"])
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une image du "
                            f"stade du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des images du "
                    f"stade du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")

            stade["images"] = images_stade

            # Récupération de l'adresse du stade
            try:
                # Récupération du 'h2' de la box stockant l'adresse du stade
                h2_box_adresse = row.find("h2", text=re.compile(transfermarkt_box_adresse_stade_find))
                # Récupération de la box stockant l'adresse du stade
                box_adresse = h2_box_adresse.find_parent("div", {
                    "class": "box"})
                # Récupération de la première ligne où est stocké l'adresse
                ligne_adresse = box_adresse.find("th",
                                              text=re.compile(
                                                  transfermarkt_adresse_stade_find)).find_parent(
                    "tr")
                # Récupération du début de l'adresse
                adresse = ligne_adresse.find("td").text.strip()
                # Récupération de la prochaine ligne stockant la suite de l'adresse 
                ligne_adresse = ligne_adresse.find_next_sibling("tr")
                # Récupération du texte de cette ligne correspondant à la suite de l'adresse
                th_text = ligne_adresse.find("th").text
                # On complète l'adresse tant la ligne suivante existe et son texte n'est pas null
                while th_text == "" and ligne_adresse is not None:
                    # On ajoute le texte à l'adresse afin de compléter cette dernière
                    adresse += ", " + ligne_adresse.find("td").text.strip()
                    # Récupération de la ligne suivante
                    ligne_adresse = ligne_adresse.find_next_sibling("tr")
                    # Si cette ligne existe, on récupère son texte
                    if ligne_adresse is not None:
                        th_text = ligne_adresse.find("th").text
                stade["adresse"] = adresse
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de l'adresse du "
                    f"stade du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")

    return stade

"""
    Fonction permettant de récupérer les joueurs du club en entrée de cette saison.
    Entrée :
        - club_transfermarkt, objet contenant les informations "d'identification" TransferMarkt du club dont on veut les joueurs ("id", "lien" et "nom")
    Sortie :
        - joueurs, tableau contenant les joueurs du club en entrée avec leur id transfermarkt ("id") ainsi que leur lien transfermarkt ("lien")
"""
def getJoueursClub(club_transfermarkt):
    # Tableaux allant contenir les joueurs du club
    joueurs = []
    # "Création" du lien du club où sont les joueurs de ce dernier
    lien = club_transfermarkt["lien"].replace(transfermarkt_url_replace,
                                          transfermarkt_joueurs_club)
    # Résultat de la requête HTTP vers la page link
    result = requests.get(lien, headers=headers)
    # Vérification que la reqête s'est bien passée
    if result.ok:
        # Transformation du code HTML de la requête en objet BeautifulSoup
        soup = BeautifulSoup(result.text, "html.parser")
        # Récupération de la table contenant l'effectif du club
        table_effectif = soup.find("div", {"id": "yw1"}).find("table")
        try:
            # Récupération des lignes de l'effectif correspondant à un joueur chacune
            ligne_joueurs = table_effectif.find("tbody").findAll("td", {"class": "posrela"})
            # Traitement de chaque ligne 
            for ligne_joueur in ligne_joueurs:
                try:
                    # Récupération de l'href vers la page TransferMarkt du joueur
                    href_link = ligne_joueur.find("table").find("a")["href"]
                    # Création du lien vers la page du joueur en remplaçant l'élèment indiquant la page TransferMarkt du joueur que l'on consulte par un élément générique 
                    lien = href_link.replace(transfermarkt_info_joueur,
                                        transfermarkt_url_replace)
                    # Index où est normalenemt l'identifiant du joueur
                    index_id_joueur = (re.search("/spieler/", lien)).end()
                    # Récupération de la fin du lien uniquement qui commence normalement par l'identifiant
                    fin_lien = lien[index_id_joueur:]
                    # Récupération de l'index juste après l'identifiant s'il n'est pas le dernière élément du lien 
                    index_char_apres_id = fin_lien.find("/") if fin_lien.find("/") else len(fin_lien)
                    # Récupération de l'identifiant dans le lien
                    id = fin_lien[:index_char_apres_id]
                    # Création du joueur  
                    joueur = {"id": id, "lien": transfermarkt_base_url + lien}
                    # Ajout du joueur dans la liste des joueurs
                    joueurs.append(joueur)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de l'id et du "
                        f"lien d'un joueur du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(
                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la liste des joueurs "
                f"du club {club_transfermarkt['nom']} ({club_transfermarkt['id']}) : {e} !")

    return joueurs
