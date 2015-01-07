import socket
import json
import sys
from threading import Thread


class Server:

    def __init__(self, game, port):
        self.conn = socket.socket()
        self.conn.bind(('0.0.0.0', port))
        self.conn.listen(5)

        self.game = game
        self.clients = []
        self.running = True

        self.listener = Thread(target=self.listen)
        self.listener.start()

        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.terminate()

    def terminate(self):
        print('Terminating')
        self.running = False
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        for client in self.clients:
            self.term_client(client)

    def listen(self):
        while self.running:
            try:
                client = Client(self, *self.conn.accept())
                self.clients.append(client)
            except socket.error as err:
                if self.running:
                    raise err

    def handle(self, client, data):
        data = json.loads(data.decode())
        clients, data = self.game.handler[
            data['action']](client, data, self.clients)
        self.send(clients, json.dumps(data).encode())

    def send(self, clients, data):
        print('Sending data')
        for client in clients:
            try:
                client.conn.send(data)
            except socket.error:
                self.term_client(client)

    def term_client(self, client):
        try:
            client.terminate()
        except socket.error:
            print('Exception during client termination')
        finally:
            print('Removing client from list')
            self.clients.remove(client)


class Client:

    def __init__(self, server, conn, addr):
        print('New client connected')
        self.server = server
        self.conn = conn
        self.addr = addr
        self.data = {
            'x': 0,
            'y': 0
        }
        self.id = 0

        self.listener = Thread(target=self.listen)
        self.listener.start()

    def listen(self):
        while self.server.running:
            try:
                data = self.conn.recv(1024)
                if len(data):
                    self.server.handle(self, data)
                else:
                    self.terminate()
                    break
            except socket.error as err:
                if self.server.running:
                    raise err

    def terminate(self):
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        print('Terminated client')


class Game:

    def __init__(self):
        self.handler = {
            'move': self.move
        }

    def move(self, client, data, clients):
        client.data['x'] += data['x']
        client.data['y'] += data['y']
        return clients, {
            'action': 'move',
            'client': client.id,
            'x': client.data['x'],
            'y': client.data['y']
        }


def main():
    try:
        port = int(sys.argv[1])
    except IndexError:
        print('Usage: python {} port'.format(sys.argv[0]))
        sys.exit()

    game = Game()
    server = Server(game, port)


if __name__ == '__main__':
    main()
