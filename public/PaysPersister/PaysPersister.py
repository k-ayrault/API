import json

from lib.ApiChourmOlympique import ApiChourmOlympique
from lib.Classes.Pays import Pays
import os

pathData = os.getcwd() + "/data/countries.json"
urlFlags = "https://flagcdn.com/256x192/{code}.png"

api = ApiChourmOlympique()

with open(pathData) as file:
    jsonPays = json.loads(file.read())
    
for code in jsonPays:
    nomsPays = jsonPays[code]
    pays = Pays()
    pays.code = code
    pays.nom = nomsPays["nom"]
    pays.nomFR = nomsPays["nom_fr"]
    pays.drapeau = urlFlags.replace("{code}", code.lower())
    
    api.postPays(pays=pays)
    