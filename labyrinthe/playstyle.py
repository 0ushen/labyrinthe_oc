import random


class Obj:
    """
    Classe représentant les types d'objets possibles sur une carte. Créé pour
    simplifier l'écriture
    """

    default_robot = 'X'
    robots = ['X', 'Y', 'Z', 'M', 'H']
    wall = 'O'
    door = '.'
    escape = 'U'
    empty = ' '


class Coord:
    """
    Classe représentant une coordonnée. Elle est créée à partir d'un tuple.
    Créé pour simplifier l'écriture.
    """

    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def __str__(self):
        return str((self.x, self.y))

    __repr__ = __str__

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)


# Les prochaines fonctions testent si une variable est un objet spécifique
def is_wall(obj):
    return obj == Obj.wall


def is_robot(obj):
    return obj in Obj.robots


def is_door(obj):
    return obj == Obj.door


def is_escape(obj):
    return obj == Obj.escape


def is_empty(obj):
    return obj == Obj.empty


def is_outer_wall(current_map, pos):
    return pos.x == 0 or pos.y == 0 or \
           pos.x == len(current_map[0]) - 1 or pos.y == len(current_map) - 1


# Les prochaines fonctions renvoient une position calculée par rapport à
# une autre position en tenant compte d'une direction et d'un nombre
# représentant le déplacement
def north(current_pos, number):
    return Coord((current_pos.x, current_pos.y - number))


def east(current_pos, number):
    return Coord((current_pos.x + number, current_pos.y))


def south(current_pos, number):
    return Coord((current_pos.x, current_pos.y + number))


def west(current_pos, number):
    return Coord((current_pos.x - number, current_pos.y))


def build_door(current_map, current_pos, direction):
    """
    Construit une porte sur un mur si cela est possible.
    :param current_map: la carte sur laquelle construire
    :param current_pos: la position à partir de laquelle on construit
    :param direction: sens dans lequel on construit ('n', 'e', 's', 'w')
    :return: tuple(valid, msg)
        valid: True si le mur a été construit
        msg: message à afficher
    """

    pos = options_first_char[direction](current_pos, 1)
    obj = current_map[pos.y][pos.x]
    if is_wall(obj) and not is_outer_wall(current_map, pos):
        change_obj(current_map, pos, Obj.door)
        return True, "Door built."
    else:
        return False, ("You can only build a door on a wall that is not on "
                       "the limit of the map.")


def build_wall(current_map, current_pos, direction):
    """
    Construit un mur sur une porte si cela est possible.
    :param current_map: la carte sur laquelle construire
    :param current_pos: la position à partir de laquelle on construit
    :param direction: sens dans lequel on construit ('n', 'e', 's', 'w')
    :return: tuple(valid, msg)
        valid: True si le mur a été construit
        msg: message à afficher
    """

    pos = options_first_char[direction](current_pos, 1)
    obj = current_map[pos.y][pos.x]
    if is_door(obj):
        change_obj(current_map, pos, Obj.wall)
        return True, "Wall built."
    else:
        return False, "You can only build a wall on a door."


# Dictionnaire associant une lettre à une fonction
# Les clés sont toute les options valables pour le premier caractère
options_first_char = {'n': north,
                      'e': east,
                      's': south,
                      'w': west,
                      'd': build_door,
                      'm': build_wall}

# Liste définissant les options valable pour le 1er caractère lorsque l'action
# est un déplacement
move_valid_first_char = ['n', 'e', 's', 'w']

# Liste définissant les options valable pour le 2e caractère lorsque l'action
# est un déplacement
move_valid_second_char = [str(i) for i in range(10)]

# Liste définissant les options valable pour le 1er caractère lorsque l'action
# est un déplacement
build_valid_first_char = ['d', 'm']

# Liste définissant les options valable pour le 2e caractère lorsque l'action
# est un déplacement
build_valid_second_char = move_valid_first_char


def current_position(current_map, robot=Obj.default_robot):
    """
    Analyse la carte (donc une liste de String) et renvoie la position
    du robot si il est présent.
    :param current_map: la carte a analyser
    :param robot: le robot dont on doit trouver la position ('X' par ex)
    """

    for y, row in enumerate(current_map):
        for x, char in enumerate(row):
            if char == robot:
                return Coord((x, y))


def place_robot_random(current_map, robot):
    """
    Place un robot au hasard sur une case libre de la carte.
    :param current_map: la carte sur laquelle placer le robot
    :param robot: le robot ('X' par ex)
    """

    available_pos = []
    for y, row in enumerate(current_map):
        for x, char in enumerate(row):
            if is_empty(char):
                available_pos.append(Coord((x, y)))
    random_pos = random.choice(available_pos)
    change_obj(current_map, random_pos, robot)


def remove_robots(current_map):
    """
    Enlève les robots de la carte passée en paramètre si il y en a.
    :param current_map: la carte sur laquelle enlever les robots
    """

    for y, row in enumerate(current_map):
        for x, char in enumerate(row):
            if char in Obj.robots:
                change_obj(current_map, Coord((x, y)), Obj.empty)


def change_obj(current_map, pos, obj):
    """
    Place un objet sur une position de la carte
    :param current_map: la carte actuelle
    :param pos: la position sur laquelle placer l'objet
    :param obj: le type d'objet a placer
    """
    # Les String étant immutable en python je fais en sorte de transformer
    # une string en liste puis je change une lettre de cette liste et puis
    # je retransforme cette liste en string :s

    temp_list = list(current_map[pos.y])
    temp_list[pos.x] = obj
    current_map[pos.y] = ''.join(temp_list)


def detect_collision(current_map, pos1, pos2):
    """
    Détecte si il y a une collision avec un mur.
    :param current_map: la carte actuelle
    :param pos1: la position de départ
    :param pos2: la position finale
    :return: True si il y a une collision
    """

    x1, y1 = (pos1.x, pos1.y)
    x2, y2 = (pos2.x, pos2.y)
    # Si les deux coordonnées sont sur le même axe X
    if y1 == y2:
        # La rangée sur laquelle se trouve les deux positions est stockées
        # dans une String
        temp_string = current_map[y1]
        # On détermine qui de x1 et x2 a la plus petite valeur
        mi, ma = (x2, x1) if x1 > x2 else (x1, x2)
        # Si le caractère représentant un mur est présent dans la substring
        # entre les deux positions alors on renvoi True
        return Obj.wall in temp_string[mi:ma + 1]
    # Si les deux coordonnées sont sur le même axe Y
    elif x1 == x2:
        # On détermine qui de y1 et y2 a la plus petite valeur
        mi, ma = (y2, y1) if y1 > y2 else (y1, y2)
        # On boucle autant de fois qu'il y a de rangées entre y1 et y2 en
        # rajoutant 1
        for i in range(ma - mi + 1):
            # On test chaque String représentant une rangée pour voir si
            # il y a un mur
            if is_wall(current_map[mi + i][x1]):
                return True
    else:
        raise ValueError('pos1 and pos2 should be on the same Axis!')

    return False


def check_input(action):
    """
    Vérifie si l'input de l'utilisateur est correct.
    :param action: input de l'utilisateur
    :return: tuple (valid, msg)
        valid: True si l'input est correct
        msg: message à afficher
    """

    first_char = action[0]
    second_char = action[1]

    # Test si l'action est bien une string de 2 caractères
    if len(action) != 2:
        msg = ("Oups! you entered a wrong input! Only inputs with 2 characters "
               "are allowed")
        return False, msg

    # Test si la lettre représentant une action est présente dans le
    # dictionnaire options
    if first_char not in options_first_char.keys():
        msg = ("Oups! you entered a wrong letter! '{}' is not a valid "
               "character, pick one in {}")
        msg = msg.format(first_char, options_first_char.keys())
        return False, msg

    # Vérifie si le 2e caractère de l'input est correct selon que ce soit un
    # déplacement ou une construction
    if first_char in move_valid_first_char:
        if second_char not in move_valid_second_char:
            msg = ("Oups! you entered a wrong number '{}' is not a valid "
                   "character for a move pick one in {}")
            msg = msg.format(second_char, move_valid_second_char)
            return False, msg
    elif first_char in build_valid_first_char:
        if second_char not in build_valid_second_char:
            msg = ("You entered a wrong direction '{}', second character must "
                   "be a letter in {} if you want to build.")
            msg = msg.format(second_char, build_valid_second_char)
            return False, msg

    return True, ""


def make_move(direction, num_of_steps, current_map, current_pos, robot):
    """
    Effectue le déplacement d'un robot sur la carte
    :param direction: sens dans lquel le robot se déplace ('n', 'e', 's', 'w')
    :param num_of_steps: nombre de case à se déplacer
    :param current_map: carte sur laquelle effectuer le déplacement
    :param current_pos: la position actuelle du robot
    :param robot: le robot qui effectue le déplacement ('X' par ex)
    :return: tuple (end, valid, msg)
        end: True si la partie est terminée
        valid: True si l'action s'est effectuée sans problème
        msg: Message à afficher
    """

    # Une nouvelle position est calculée en fonction du déplacement voulu
    new_pos = options_first_char[direction](current_pos, int(num_of_steps))

    # Test si le déplacement voulu n'entraine pas le robot en dehors de la carte
    if (new_pos.x >= len(current_map[0]) or new_pos.y >= len(current_map)
            or new_pos.x < 0 or new_pos.y < 0):
        msg = "You can't go outside the map!, Try again!"
        return False, False, msg

    # Test si il y a un mur entre l'ancienne et la nouvelle position
    if detect_collision(current_map, current_pos, new_pos):
        msg = "Oups you hit a wall! Try again."
        return False, False, msg

    # Détermine quel type d'objet se trouve sur la nouvelle position
    obj = current_map[new_pos.y][new_pos.x]

    # Test si le robot d'un autre joueur se trouve sur la position finale
    if is_robot(obj):
        msg = "Oups you hit another player robot! Try again : "
        return False, False, msg

    # Si on arrive sur une sortie on remplace la position initiale du robot
    # par un espace vide et on remplace la sortie par le robot
    if is_escape(obj):
        change_obj(current_map, current_pos, Obj.empty)
        change_obj(current_map, new_pos, robot)
        msg = "Well played! You found the exit!"
        return True, True, msg

    # Si la position finale est une porte, on la traverse
    if is_door(obj):
        new_pos = options_first_char[direction](new_pos, 1)

    # La position initiale du robot est remplacée par un espace vide et
    # et on écrit le robot sur la position finale
    change_obj(current_map, current_pos, Obj.empty)
    change_obj(current_map, new_pos, robot)

    msg = "Good, waiting for the opponent to play..."
    return False, True, msg


def make_build(build_type, direction, current_map, current_pos):
    """
    Construit un objet sur la carte à une case du robot.
    :param build_type: type de construction (mur 'm' ou porte 'd')
    :param direction: sens dans lequel la construction doit être faite
    par rapport au robot ('n', 'w', 's', 'e')
    :param current_map: la carte sur laquelle effectuer cette action
    :param current_pos: la position actuelle du robot qui effectue l'action
    :return: tuple (valid, msg)
        valid: True si le mur est construit
        msg: Message à afficher
    """

    valid, msg = options_first_char[build_type](current_map, current_pos,
                                                direction)
    return valid, msg


def play_turn(current_map, action, robot=Obj.default_robot):
    """
    Effectue une action sur une carte.
    :param current_map: la carte sur laquelle effectuer une action
    :param action: input de l'utilisateur
    :param robot: le robot qui doit effectuer l'action ('X' par ex)
    :return: tuple (end, valid, msg)
        end: True si la partie est terminée
        valid: True si l'action s'est effectuée sans problème
        msg: Message à afficher
    """

    # On test si l'input de l'utilisateur est correct
    valid, msg = check_input(action)
    if not valid:
        return False, False, msg

    # Détermine la position actuelle du robot
    current_pos = current_position(current_map, robot)

    first_char = action[0]
    second_char = action[1]

    # Si l'action de l'utilisateur est un déplacement
    if first_char in move_valid_first_char:
        return make_move(first_char, second_char, current_map, current_pos,
                         robot)

    # Si l'action de l'utilisateur est une construction
    elif first_char in build_valid_first_char:
        is_valid, msg = make_build(first_char, second_char, current_map,
                                   current_pos)
        return False, is_valid, msg
