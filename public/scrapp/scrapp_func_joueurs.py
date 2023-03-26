from scrapp_func_global import *
from scrapp_func_joueurs_infos import *

"""
    Fonction permettant de récupérer les informations du joueur en entrée
    Entrée :
        - joueur_transfermarkt, objet contenant les informations "d'identification" TransferMarkt ("id" et "lien")
    Sortie :
        - joueur, informations scrapp du joueur
"""
def getInfoJoueur(joueur_transfermarkt):
    # Id TransferMarkt du joueur
    id_transfermarkt = joueur_transfermarkt["id"]
    # "Création" du lien du club où sont les infos de ce dernier
    link = joueur_transfermarkt["lien"].replace(transfermarkt_url_replace,
                                            transfermarkt_info_joueur)
    # Résultat de la requête HTTP
    result = requests.get(link, headers=headers)
    # Vérification que la requête c'est bien passé
    if result.ok:
        # Transformation de l'HTML en BeautifulSoup
        soup = BeautifulSoup(result.text, "html.parser")
        # Si le joueur n'est pas encore présent dans les données actuelles, récupération infos persos + carrière sinon
        # juste mise à jour de la carrière
        if id_transfermarkt not in all_joueurs_id:
            # Initialisation de l'objet comportant les informations d'une joueur
            joueur = {
                "id_transfermarkt": joueur_transfermarkt["id"],
                "lien_transfermarkt": joueur_transfermarkt["lien"],
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

                # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
                row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
                # Récupération du tableau contenant les informations personnelles du joueur
                info_table = row.find("div", {"class": "info-table"})

                # Récupération du nom et prénom du joueur
                # Récupération du nom/prénom du joueur
                try:
                    nom, prenom = getNomPrenom(header=header)
                    joueur["nom"] = nom
                    joueur["prenom"] = prenom
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du nom/prénom "
                        f"du joueur {joueur_transfermarkt['id']} via le header : {e} !")

                # Récupération du nom complet du joueur
                try:
                    nom_complet = getNomComplet(info_table=info_table)
                    nom_complet = nom_complet if nom_complet else f"{joueur['nom']} {joueur['prenom']}"
                    joueur["nom_complet"] = nom_complet 
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du nom complet "
                        f"du joueur {joueur_transfermarkt['id']} : {e} !")

                # Indiquer dans le log le joueur que l'on est en train de traiter
                logging.info(f"[INFO] - {joueur['nom_complet']} : En cours")

                # Récupération de la date de naissance du joueur
                try:
                    naissance = info_table.find(text=re.compile(TM_JOUEUR_NAISSANCE_LABEL_TEXT))
                    naissance = naissance.find_parent().find_next_sibling().find("a").text
                    naissance = datetime.strptime(naissance.strip(), '%d %b %Y')
                    joueur["date_naissance"] = naissance.date().isoformat()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la date "
                        f"de naissance du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

                # Récupération des nationalités du joueur
                try:
                    nationalite = info_table.find(
                        text=re.compile(TM_JOUEUR_NATIONALITES_LABEL_TEXT))
                    nationalite = nationalite.find_parent().find_next_sibling()
                    for img in nationalite.findAll("img"):
                        try:
                            pays = triNation(img["alt"])
                            joueur["pays"].append(pays)
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                f"nationalité du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des "
                        f"nationalités du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

                # Récupération du pied fort du joueur
                try:
                    pied = info_table.find(text=re.compile(TM_JOUEUR_PIED_FORT_LABEL_TEXT))
                    joueur["pied"] = pied.find_parent().find_next_sibling().text
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération du pied fort "
                        f"du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

                # Récupération de la taille du joueur
                try:
                    taille = info_table.find(text=re.compile(TM_JOUEUR_TAILLE_LABEL_TEXT))
                    joueur["taille"] = re.sub('\D', '', taille.find_parent().find_next_sibling().text)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la taille "
                        f"du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

                # Récupération de l'équipementier actuel du joueur
                try:
                    equipementier = info_table.find(
                        text=re.compile(TM_JOUEUR_EQUIPEMENTIER_LABEL_TEXT))
                    joueur["equipementier"] = equipementier.find_parent().find_next_sibling().text
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de "
                        f"l'équipementier actuel du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

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
                                        if class_css_position_principale_start in class_type
                                        ][0].replace(class_css_position_principale_start, "")
                            if position.isdigit():
                                positions_principales.append(int(position))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                f"position principale du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) "
                                f": {e} !")

                    joueur["positions_principales"] = positions_principales

                    # Récupération des spans correspondants aux positions secondaires du joueur
                    span_positions_secondaires = box_positions.findAll("span", {"class": "position__secondary"})

                    positions_secondaires = []

                    for span_position_secondaire in span_positions_secondaires:
                        try:
                            position = [class_type for class_type in span_position_secondaire["class"]
                                        if class_css_position_secondaire_start in class_type
                                        ][0].replace(class_css_position_secondaire_start, "")
                            if position.isdigit():
                                positions_secondaires.append(int(position))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                f"position secondaire du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) "
                                f": {e} !")

                    joueur["positions_secondaires"] = positions_secondaires
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des positions "
                        f"du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

                # Récupération date de fin du dernier contrat du joueur (çàd celui actuel normalement)
                date_fin_contrat = None
                try:
                    # Récupère la date de fin du contrat avec le club qui prête le joueur (si prêté)
                    fin_contrat = info_table.find(text=re.compile(TM_JOUEUR_PRETE_DATE_FIN_CONTRAT_ACTUEL_LABEL_TEXT))
                    # Si le joueur n'est pas prêté, récupère la date de fin du contrat
                    if fin_contrat is None:
                        fin_contrat = info_table.find(text=re.compile(TM_JOUEUR_DATE_FIN_CONTRAT_ACTUEL_LABEL_TEXT))

                    fin_contrat = fin_contrat.find_parent().find_next_sibling().text
                    try:
                        fin_contrat = datetime.strptime(fin_contrat.strip(), '%d %b %Y')
                        date_fin_contrat = fin_contrat.date().isoformat()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la conversion de la date de "
                            f"fin du contrat actuel ({fin_contrat}) du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la date de "
                        f"fin du contrat actuel  du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

                contrats = getContratsJoueur(joueur_transfermarkt, date_fin_contrat)
                joueur["contrats"] = contrats

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des informations "
                    f"personnelles du joueur {joueur_transfermarkt['id']} : {e} !")

            all_joueurs.append(joueur)
            all_joueurs_id.append(joueur["id_transfermarkt"])

            return joueur
        else:
            try:
                # Récupération du joueur correspondant à l'id_transfermarkt
                joueur = next((x for x in all_joueurs if x["id_transfermarkt"] == id_transfermarkt),
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
                        taille = info_table.find(text=re.compile(TM_JOUEUR_TAILLE_LABEL_TEXT))
                        joueur["taille"] = re.sub('\D', '', taille.find_parent().find_next_sibling().text)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la taille "
                            f"du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

                    # Récupération de l'équipementier actuel du joueur
                    try:
                        equipementier = info_table.find(
                            text=re.compile(TM_JOUEUR_EQUIPEMENTIER_LABEL_TEXT))
                        joueur["equipementier"] = equipementier.find_parent().find_next_sibling().text
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de "
                            f"l'équipementier actuel du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

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
                                            if class_css_position_principale_start in class_type
                                            ][0].replace(class_css_position_principale_start, "")
                                if position.isdigit():
                                    positions_principales.append(int(position))
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logging.error(
                                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                    f"position principale du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) "
                                    f": {e} !")

                        joueur["positions_principales"] = positions_principales

                        # Récupération des spans correspondants aux positions secondaires du joueur
                        span_positions_secondaires = box_positions.findAll("span", {"class": "position__secondary"})

                        positions_secondaires = []

                        for span_position_secondaire in span_positions_secondaires:
                            try:
                                position = [class_type for class_type in span_position_secondaire["class"]
                                            if class_css_position_secondaire_start in class_type
                                            ][0].replace(class_css_position_secondaire_start, "")
                                if position.isdigit():
                                    positions_secondaires.append(int(position))
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logging.error(
                                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération d'une "
                                    f"position secondaire du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) "
                                    f": {e} !")

                        joueur["positions_secondaires"] = positions_secondaires
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération des positions "
                            f"du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")

                    # Récupération date de fin du dernier contrat du joueur (çàd celui actuel normalement)
                    try:
                        # Récupère la date de fin du contrat avec le club qui prête le joueur (si prêté)
                        fin_contrat = info_table.find(text=re.compile(TM_JOUEUR_PRETE_DATE_FIN_CONTRAT_ACTUEL_LABEL_TEXT))
                        # Si le joueur n'est pas prêté, récupère la date de fin du contrat
                        if fin_contrat is None:
                            fin_contrat = info_table.find(text=re.compile(TM_JOUEUR_DATE_FIN_CONTRAT_ACTUEL_LABEL_TEXT))

                        fin_contrat = fin_contrat.find_parent().find_next_sibling().text
                        try:
                            fin_contrat = datetime.strptime(fin_contrat.strip(), '%d %b %Y')
                            date_fin_contrat = fin_contrat.date().isoformat()
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logging.error(
                                f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la conversion de la date de "
                                f"fin du contrat actuel ({fin_contrat}) du joueur {joueur['nom_complet']} ({joueur_transfermarkt['id']}) : {e} !")
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logging.error(
                            f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la récupération de la date de "
                            f"fin du contrat actuel  du joueur ({joueur_transfermarkt['id']}) : {e} !")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(
                        f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la màj des informations "
                        f"personnelles  du joueur ({joueur_transfermarkt['id']}) : {e} !")

                # Si le joueur n'a pas de contrat on les récupère sinon on les mets à jour
                if "contrats" not in joueur or joueur["contrats"] is None or len(joueur["contrats"]) == 0:
                    contrats = getContratsJoueur(joueur_transfermarkt, date_fin_contrat)
                    joueur["contrats"] = contrats
                else:
                    majContratsJoueur(joueur, joueur_transfermarkt, date_fin_contrat)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.error(
                    f"[ERROR] {exc_tb.tb_lineno} Un problème a été rencontré lors de la màj des informations "
                    f"personnelles du joueur {joueur_transfermarkt['id']} : {e} !")
                return
        joueur["date_maj"] = datetime.now().isoformat()
        logging.info(f"[INFO] - {joueur['nom_complet']} : Terminé")
        logging.info("-------------------------------------------------------------------------------------------------")


def getContratsJoueur(joueur_to_scrapp, date_fin_contrat):
    # "Création" du lien du joueur où sont les transfert de ce dernier
    link = joueur_to_scrapp["lien"].replace(transfermarkt_url_replace,
                                            transfermarkt_transferts_joueur)
    result = requests.get(link, headers=headers)
    if result.ok:
        soup = BeautifulSoup(result.text, "html.parser")
        try:
            # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
            row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})
            # Récupération du tableau contenant les différents transferts du joueur
            titre_tableau_transferts = row.find("h2",
                                                text=re.compile(transfermarkt_historique_transfert_find))
            tableau_transferts = titre_tableau_transferts.find_parent()

            # Récupération des lignes du tableau correspondant à un 'transfert' (une seule classe)
            lignes = tableau_transferts.findAll("div", {"class": transfermarkt_class_transfert_ligne})
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

                contrat = copy.deepcopy(contrat_vide)
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
    link = joueur_to_scrapp["lien"].replace(transfermarkt_url_replace,
                                            transfermarkt_transferts_joueur)
    result = requests.get(link, headers=headers)
    if result.ok:
        soup = BeautifulSoup(result.text, "html.parser")
        try:
            # Récupération de la div contenant les données du joueur (le body de la page du joueur en somme)
            row = soup.find("div", {"id": "subnavi"}).find_next_sibling("div", {"class": "row"})

            # Récupération du tableau contenant les différents transferts du joueur
            titre_tableau_transferts = row.find("h2",
                                                text=re.compile(transfermarkt_historique_transfert_find))
            tableau_transferts = titre_tableau_transferts.find_parent()

            # Récupération des lignes du tableau correspondant à un 'transfert' (une seule classe)
            lignes = tableau_transferts.findAll("div", {"class": transfermarkt_class_transfert_ligne})
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

                        contrat = copy.deepcopy(contrat_vide)
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
        montant_transfert = ligne.find("div", {"class": transfermarkt_class_transfert_ligne + "__fee"})
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
        date_transfert = ligne.find("div", {"class": transfermarkt_class_transfert_ligne + "__date"})
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
                                      {"class": transfermarkt_class_transfert_ligne + "__new-club"})
        if club_entrant_div is not None:
            club["nom"] = club_entrant_div.text.strip()
        if club["nom"] != "Fin de carrière" and club["nom"] != "Pause carrière" and club["nom"] != "":
            link_club = club_entrant_div.find("a")
            link_club = link_club["href"]
            link_club = link_club[:link_club.find("/saison_id/")]
            match = (re.search("/verein/", link_club))
            id = link_club[match.end():]
            club["id"] = id
            link_club = link_club.replace(transfermarkt_transferts_joueur,
                                              transfermarkt_url_replace)
            getInfoClub({"id": id, "nom": club["nom"], "lien": transfermarkt_base_url + link_club})
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
                                      {"class": transfermarkt_class_transfert_ligne + "__old-club"})
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
                link_club = link_club.replace(transfermarkt_transferts_joueur,
                                              transfermarkt_url_replace)
                getInfoClub({"id": id, "nom": club["nom"], "lien": transfermarkt_base_url + link_club})
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
            contrat = copy.deepcopy(contrat_vide)
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
        if abrev in montant_abrev_valeur:
            facteur = montant_abrev_valeur[abrev]
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
