import socket, sys, json
from threading import Thread
import nbinput

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
                self.clients.handler[data.action](data)
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
        self.players[data['client']]['x'] = data['x']
        self.players[data['client']]['y'] = data['y']


def main():
    try:
        addr = (sys.argv[1], int(sys.argv[2]))
    except IndexError:
        print('Usage: {} host port'.format(sys.argv[0]))
        sys.exit()

    players = Players()
    client = Client(addr, players)
    
    W, H = 20, 20
    player = {
        'action': 'move',
        'x': 0,
        'y': 0
    }
        
    with nbinput.NonBlockingInput() as nbi:
        while True:
            c = nbi.char()
            if c:
                c = c.lower()
                if c == 'w':
                    player['y'] += 1
                elif c == 'a':
                    player['x'] -= 1
                elif c == 's':
                    player['y'] -= 1
                elif c == 'd':
                    player['x'] += 1
                
                client.send(player)
            
            out = [[' ' for x in range(W)] for y in range(H)]
            for player in players.players:
                out[player['y']][player['x']] = '#'
            print('\n'.join(' '.join(row) for row in out))


if __name__ == '__main__':
    main()
