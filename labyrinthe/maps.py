import glob
import os

# Repertoire des cartes
MAPS_DIR = os.path.join(os.path.dirname(__file__), '../cartes/')
# Extension des fichiers de cartes
FILE_EXT = '.txt'
# Saved Game Tag
SGT = '[UNFINISHED]'

# Cette ligne prends tout les fichiers de cartes et garde leurs noms
# (sans l'extension) dans une liste
maps = [os.path.splitext(os.path.basename(x))[0] for
        x in glob.glob(MAPS_DIR + '*' + FILE_EXT)]


def show_maps():
    """Affiche la liste des cartes disponibles"""

    print('Available maps :')
    for i, name in enumerate(maps):
        print(str(i) + '- ' + name)


def get_list_of_names():
    """
    :return: list of available maps names
    """
    return maps


def get_number_of_maps():
    return len(maps)


def get_map_name(map_index):
    return maps[map_index]


def load_map(map_index):
    """Renvoie la carte choisie sous forme d'une liste de String."""

    if isinstance(map_index, int) and map_index < len(maps):
        with open(MAPS_DIR + maps[map_index] + FILE_EXT) as mapFile:
            current_map = mapFile.readlines()
        # Si on reprend une carte non finie, il faut enlever le tag
        if SGT in maps[map_index]:
            maps[map_index] = maps[map_index].replace(SGT, '')
    else:
        raise ValueError(("Wrong map_index. map_index should be an integer and "
                          "should be smaller than the number of maps"))

    return current_map


def save_map(map_index, current_map):
    """
    Sauvegarde l'état d'une carte en lui ajoutant un tag dans le nom de fichier.
    """

    with open(MAPS_DIR + maps[map_index] + SGT + FILE_EXT, 'w') as mapFile:
        mapFile.writelines(current_map)


def delete_finished_map(map_index):
    """Supprime le fichier d'une carte qui s'est terminée."""

    os.remove(MAPS_DIR + maps[map_index] + SGT + FILE_EXT)


def print_map(current_map):
    """Affiche la carte."""

    print(''.join(current_map))
