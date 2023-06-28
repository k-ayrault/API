"""
    Fonction permettant de renommer certains pays afin de ne pas foutre le zbeul côté enregistrement dans la BD
    TODO : D'ailleurs voir si cette fonction n'a pas plus de sens d'être du côté du PHP ! 
    Entrée :
        - pays, nom du pays scrapp
    Sortie : 
        - pays, nom du pays scrapp normalement présent dans la bd
"""
def triNation(pays):
    if pays is not None:
        if pays == 'Angleterre':
            return 'Royaume-Uni'
        elif pays == 'RD Congo':
            return 'République Démocratique Du Congo'
        elif pays == 'Russie':
            return 'Fédération De Russie'
    return pays
