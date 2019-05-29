import random
import socket
import json
import select
import maps
import playstyle


class Player(socket.socket):
    """
    Classe représentant un joueur.
    Hérite de socket.socket.

    Attributes:
        addr (tuple(ip, port)): addresse ip et port du joueur
        name (string): pseudo du joueur
        is_ready (bool): indique si le joueur est prêt à lancer une partie
        is_winner (bool): indique si le joueur a gagné la partie
        robot (string): le robot du joueur (ex: 'X')
        map_voted (int): l'index de la carte pour lequel le joueur a voté
    """

    def __init__(self, *args, **kwargs):
        socket.socket.__init__(self, *args, **kwargs)
        self.addr = ''
        self.name = ''
        self.robot = ''
        self.is_ready = False
        self.is_winner = False
        self.map_voted = None

    @classmethod
    def copy(cls, sock):
        """
        Crée un objet Player a partir d'un socket
        :param sock: le socket a copié
        :return: l'objet Player généré
        """

        fd = socket.dup(sock.fileno())
        copy = cls(sock.family, sock.type, sock.proto, fileno=fd)
        copy.settimeout(sock.gettimeout())
        sock.close()

        return copy


class Server:
    """
    Cette classe représente le serveur du jeu labyrinthe.

    Attributes:
        host: l'addresse ip de l'hôte
        port: le port sur lequel hébergé la partie
        packet_size: la taille des packets à recevoir
        min_player: le nombre de joueurs minimum pour commencer une partie
        max_player: le nombre de joueurs maximum à accepter
        players: liste des joueurs connectés
        map: la carte sur laquelle la partie se déroule actuellement
        map_voted : liste contenant les index des cartes votées
        available_robots: liste des robots disponibles
        rules: les règles du jeu
    """

    def __init__(self, host, port):
        self.host = ''
        self.port = 12800
        self.packet_size = 1024
        self.min_player = 2
        self.max_player = 5
        self.players = []
        self.map = []
        self.map_voted = []
        self.available_robots = ['X', 'Y', 'Z', 'M', 'H']
        self.rules = ("RULES:\n"
                      "1.To move your robot: first letter you type represents"
                      " the direction you want your robot to go in ('n' for "
                      "North, 'e' for East, 's' for South, 'w' for West) and"
                      "the second letter represents the number of steps (must"
                      "be a number from 1 to 9).\n"
                      "2.To build: first letter must be 'm' to build a wall or"
                      " 'd' to build a door and the second letter represents a"
                      "direction ('n', 'e', 's', 'w').\n")

        # Le serveur est démarré
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        print('socket binded to port {} on {}'.format(port, host))
        self.sock.listen(self.max_player)
        print('socket listening')

    def wait_for_players(self):
        """
        Cette fonction gère l'attente des joueurs. Un select s'occupe de
        lire dans le socket du serveur et accepte les connexions de joueurs
        arrivant. Ces joueurs sont ajoutés à la liste de socket à lire et
        lorsque l'on lit dans un socket joueur on vérifie si le joueur à
        préciser qu'il est pr^t à lancer une partie. La fonction retourne
        une fois qu'assez de joueurs sont prêt pour lancer une partie.
        """

        read_list = [self.sock]
        players_ready = [p for p in self.players if p.is_ready]
        while (len(players_ready) < self.min_player
               or len(players_ready) < len(self.players)):
            readable, _, _ = select.select(read_list, [], [])
            for s in readable:
                # Si le socket dans lequel on lit est celui du serveur
                if s is self.sock:
                    conn, addr = self.sock.accept()
                    p = Player.copy(conn)
                    p.addr = addr
                    self.players.append(p)
                    read_list.append(p)
                    self.send_data_json({"msg": self.rules}, p)
                    print(f"Player {p.addr} has connected.")
                # Sinon c'est celui d'un joueur
                else:
                    data = self.recv_data_json(s)
                    if "action" in data:
                        if data["action"] == "ready":
                            s.ready = True
                            players_ready.append(s)
                            msg = f"Player {p.addr} is ready to start the game"
                            print(msg)
                            self.send_all({"msg": msg})
        print("Enough players are ready to start a game.")

    def vote_map(self):
        """
        Cette fonction demande aux joueurs de voter pour la carte sur laquelle
        ils désirent jouer. Un select est utilisé pour lire dans la liste des
        joueurs connectés et vérifier si ils ont voter.
        :return: (int) l'index de la carte la plus votée
        """

        # Envoi un message demandant de voter pour une carte à chaque joueurs
        msg = "Please vote for a map : \n"
        for i, name in enumerate(maps.get_list_of_names()):
            msg += f"{i}. {name}\n"
        self.send_all({"action": "votemap", "msg": msg})

        # Tant que tout les joueurs prêt n'ont pas voté on lit dans les sockets
        p_who_voted = []
        while len(p_who_voted) < len(self.players):
            readable, _, _ = select.select(self.players, [], [])
            for p in self.players:
                data = self.recv_data_json(p)
                if "votemap" not in data:
                    continue
                elif not data["votemap"].isnumeric():
                    msg = "Error: Your input must be a number"
                    self.send_data_json({"action": "votemap", "msg": msg}, p)
                elif not 0 <= int(data["votemap"]) < maps.get_number_of_maps():
                    msg = "Error: input not an index of an existing map"
                    self.send_data_json({"action": "votemap", "msg": msg}, p)
                else:
                    p.map_voted = int(data["votemap"])
                    self.map_voted.append(p.map_voted)
                    p_who_voted.append(p)
                    msg = "Player {} voted for {}"
                    msg = msg.format(p.addr, maps.get_map_name(p.map_voted))
                    print(msg)
                    self.send_all({"msg": msg})

        return max(set(self.map_voted), key=self.map_voted.count)

    def place_robots(self):
        """
        Choisi un robot au hasard pour chaque joueur puis le place sur la
        carte
        """

        for p in self.players:
            # Choisi un robot au hasard dans la liste des robots disponible
            # puis l'enlève de celle ci
            random_index = random.randrange(0, len(self.available_robots))
            robot = self.available_robots.pop(random_index)

            p.robot = robot
            playstyle.place_robot_random(self.map, p.robot)
            self.send_data_json({"msg": f"Your robot is {p.robot}"}, p)

    @staticmethod
    def send_data_json(data, conn):
        """
        Converti un dictionnaire en json et l'envoie dans un socket
        :param data: dictionnaire de données
        :param conn: socket dans lequel on envoie les données
        """

        send_json = json.dumps(data)
        conn.send(bytes(send_json, 'utf8'))

    def recv_data_json(self, conn):
        """
        Accepte les données d'un socket et les renvoie sous format json
        :param conn: sicket dans lequel on lit les données
        :return: (str) données au format json
        """

        recv_json = conn.recv(self.packet_size).decode()
        return json.loads(recv_json)

    def send_all(self, data, exception=[]):
        """
        Envoie des données (json) à tout les joueurs connectés
        :param data: les données sous forme d'un dictionnaire
        :param exception: liste des joueurs à qui l'on envoie pas les données
        """

        for p in self.players:
            if p not in exception:
                self.send_data_json(data, p)

    def start_game(self):
        """
        Une fois qu'assez de joueurs sont prêt on lance une partie via cette
        fonction.
        """

        # Charge la carte pour laquelle les joueurs ont voté dans la partie
        self.map = maps.load_map(self.vote_map())

        # Enlève les robots qui pourraient être présent par défaut sur la carte
        playstyle.remove_robots(self.map)

        # Choisi un robot et une position au hasard pour chaque joueur
        self.place_robots()

        # Boucle dans laquelle on demande aux joueurs leur action à effectué.
        # La boucle ne s'arrête que lorsqu'un joueur a trouvé la sortie.
        end = False
        while not end:
            for p in self.players:
                data = {"map": self.map,
                        "msg": f"Awaiting {p.robot} move..."}
                self.send_all(data, [p])

                msg = "Your turn to play : "
                valid_turn = False
                while not valid_turn:
                    data = {"map": self.map,
                            "end": end,
                            "action": "makemove",
                            "msg": msg}
                    self.send_data_json(data, p)
                    data = self.recv_data_json(p)
                    print(f"Object received from player {p.addr} : {data}")
                    end, valid_turn, msg = \
                        playstyle.play_turn(self.map, data["makemove"], p.robot)

                if end:
                    p.is_winner = True
                    break

        self.end_game()

    def end_game(self):
        """
        Fonction qui effectue les traitements nécéssaires une fois une partie
        terminée.
        """

        # Envoie la carte et un message de fin à tout les joueurs
        for p in self.players:
            data = {"map": self.map,
                    "end": True}
            if p.is_winner:
                data["msg"] = "Congrats you won!"
            else:
                data["msg"] = "Sorry you lost :("
            self.send_data_json(data, p)


if __name__ == '__main__':
    host = 'localhost'
    port = 12800

    serv = Server(host, port)
    serv.wait_for_players()
    serv.start_game()
