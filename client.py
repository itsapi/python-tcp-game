import socket
import sys
import json
import nbinput
import time
import console
from threading import Thread


class Client:

    def __init__(self, addr, clients):
        self.conn = socket.socket()
        self.conn.connect(addr)

        self.clients = clients
        self.running = True
        self.listener = Thread(target=self.listen)
        self.listener.start()

    def listen(self):
        while self.running:
            data = self.conn.recv(1024)
            if data:
                data = json.loads(data.decode())
                self.clients.handler[data['action']](data)
            else:
                self.terminate()

    def send(self, data):
        data = json.dumps(data)
        self.conn.send(data.encode())

    def terminate(self):
        print('terminating')
        self.running = False

        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except socket.error:
            pass


class Players:

    def __init__(self):
        self.handler = {
            'move': self.move
        }

        self.players = {}

    def move(self, data):
        try:
            self.players[data['client']]
        except KeyError:
            self.players[data['client']] = {}

        self.players[data['client']]['x'] = data['x']
        self.players[data['client']]['y'] = data['y']


def main():
    try:
        addr = (sys.argv[1], int(sys.argv[2]))
    except IndexError:
        print('Usage: python {} host port'.format(sys.argv[0]))
        sys.exit()

    players = Players()
    client = Client(addr, players)

    W, H = console.WIDTH, console.HEIGHT
    player = {
        'action': 'move',
        'x': int(W / 2),
        'y': int(H / 2)
    }

    try:
        with nbinput.NonBlockingInput() as nbi:
            while True:
                time.sleep(0.1)

                c = nbi.char()
                if not c:
                    continue

                c = c.lower()
                if c == 'w':
                    player['y'] = (player['y'] - 1) % H
                elif c == 'a':
                    player['x'] = (player['x'] - 1) % W
                elif c == 's':
                    player['y'] = (player['y'] + 1) % H
                elif c == 'd':
                    player['x'] = (player['x'] + 1) % W

                client.send(player)

                out = [[' ' for x in range(W)] for y in range(H)]
                for player in players.players.values():
                    out[player['y']][player['x']] = '#'
                print('\n'.join(' '.join(row) for row in out))

    except KeyboardInterrupt:
        client.terminate()


if __name__ == '__main__':
    main()
