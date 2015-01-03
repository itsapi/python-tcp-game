import socket
from threading import Thread


class Server:
  def __init__(self):
    self.conn = socket.socket()
    self.conn.bind(('0.0.0.0', 1337))
    self.conn.listen(5)
    
    self.clients = []
    self.running = True
    
    self.listener = Thread(target=self.listen)
    self.listener.start()
    
    try:
      while True:
        pass
    except KeyboardInterrupt:
      self.running = False
      self.conn.shutdown(socket.SHUT_RDWR)
      self.conn.close()

  def listen(self):
    while self.running:
      try:
        client = Client(self, *self.conn.accept())
        self.clients.append(client)
      except socket.error as err:
        if self.running:
          raise err

  def handle(self, client, data):
    for other_client in self.clients:
      if other_client is not client:
        other_client.conn.send(data)
        try:
          pass
        except:
          self.clients.remove(other_client)


class Client:
  def __init__(self, server, conn, addr):
    self.server = server
    self.conn = conn
    self.addr = addr
    
  def listen(self):
    while self.server.running:
      data = self.conn.recv(1024)
      self.server.handle(self, data)


def main():
  server = Server()


if __name__ == '__main__':
  main()
