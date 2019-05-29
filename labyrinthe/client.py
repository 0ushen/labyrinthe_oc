import socket
import json
import threading
from maps import print_map

HOST = 'localhost'
PORT = 12800
PACKET_SIZE = 1024


def send_data_json(data, sock):
    send_json = json.dumps(data)
    sock.send(bytes(send_json, 'utf8'))


def recv_data_json(sock):
    recv_json = sock.recv(PACKET_SIZE).decode()
    return json.loads(recv_json)


def connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print('Client connected to server\nHost : {}\nPort : {}'.format(HOST, PORT))

    return sock


def wait_for_ready(sock):
    while not input("Type 'c' when you are ready\n") == 'c':
        pass
    data = {"action": "ready"}
    send_data_json(data, sock)


def ask_input(sock, msg, data_type):
    action = input(msg)
    data = {data_type: action}
    send_data_json(data, sock)


def start_game(sock):
    t = threading.Thread(target=wait_for_ready, args=[sock])
    t.start()

    end = False
    while not end:
        data = recv_data_json(sock)

        if "end" in data:
            end = data["end"]

        if "map" in data:
            print_map(data["map"])

        if "action" in data:
            t = threading.Thread(target=ask_input,
                                 args=[sock, data["msg"], data["action"]])
            t.start()
            continue

        if "msg" in data:
            print(data["msg"] + '\n')


if __name__ == '__main__':
    server_sock = connect()
    start_game(server_sock)
