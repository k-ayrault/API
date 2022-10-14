import json
import locale
from pathlib import Path
import scrapp_func_global
import scrapp_func_clubs
import logging
from datetime import datetime

date_str_filename = datetime.now().strftime("%d_%m_%Y_%H_%M_%f")
log_filename = "log_scrapp_joueurs_" + date_str_filename

log_file_path = Path("scrapp/log/" + log_filename)

logging.basicConfig(filename=log_file_path, level=logging.INFO, encoding="UTF-8")

locale.setlocale(locale.LC_ALL, 'fr_FR')

json_clubs = Path("scrapp/donnees/clubs.json").absolute()
json_id_clubs = Path("scrapp/donnees/id_clubs.json").absolute()
json_joueurs = Path("scrapp/donnees/joueurs.json").absolute()
json_id_joueurs = Path("scrapp/donnees/id_joueurs.json").absolute()


def save():
    with open(json_clubs, "w+") as clubs_json:
        json.dump(scrapp_func_global.all_clubs, clubs_json, indent=4, sort_keys=True, default=str)
    with open(json_id_clubs, "w+") as id_clubs_json:
        json.dump(scrapp_func_global.all_clubs_id, id_clubs_json, indent=4, sort_keys=True, default=str)
    with open(json_joueurs, "w+") as joueurs_json:
        json.dump(scrapp_func_global.all_joueurs, joueurs_json, indent=4, sort_keys=True, default=str)
    with open(json_id_joueurs, "w+") as id_joueurs_json:
        json.dump(scrapp_func_global.all_joueurs_id, id_joueurs_json, indent=4, sort_keys=True, default=str)


if json_clubs.exists():
    with open(json_clubs, "r") as clubs_json:
        scrapp_func_global.all_clubs = json.load(clubs_json)
if json_id_clubs.exists():
    with open(json_id_clubs, "r") as id_clubs_json:
        scrapp_func_global.all_clubs_id = json.load(id_clubs_json)
if json_joueurs.exists():
    with open(json_joueurs, "r") as joueurs_json:
        scrapp_func_global.all_joueurs = json.load(joueurs_json)
if json_id_joueurs.exists():
    with open(json_id_joueurs, "r") as id_joueurs_json:
        scrapp_func_global.all_joueurs_id = json.load(id_joueurs_json)

clubs = scrapp_func_clubs.getClubsLigue1()
for club in clubs:
    logging.info("-------------------------------------------------------------------------------------------------")
    logging.info(f"[INFO] {club['nom']} : En cours")
    scrapp_func_clubs.getInfoClub(club)
    scrapp_func_clubs.getJoueursClub(club)
    save()
    logging.info(f"[INFO] {club['nom']} : Terminé")
    logging.info("-------------------------------------------------------------------------------------------------")