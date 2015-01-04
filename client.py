import socket, sys, json
from threading import Thread


class Client:
    def __init__(self, addr):
        self.conn = socket.socket()
        self.conn.connect(addr)

        self.running = True
        self.listener = Thread(target=self.listen)
        self.listener.start()

        self.send()

    def listen(self):
        while self.running:
            data = self.conn.recv(1024)
            if data:
                data = json.loads(data.decode())
                print('{} is at ({}, {})'.format(data['client'], data['x'], data['y']))
            else:
                self.terminate()

    def send(self):
        try:
            while True:
                try:
                    dx, dy = input('(dx dy)> ').split()
                    data = json.dumps({'action': 'move', 'dx': int(dx), 'dy': int(dy)})
                    self.conn.send(data.encode())
                except ValueError:
                    pass

        except KeyboardInterrupt:
            self.terminate()

    def terminate(self):
        print('terminating')
        self.running = False

        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except socket.error:
            pass


def main():
    c = Client(('192.168.43.8', 1338))


if __name__ == '__main__':
    main()
