import socket
from threading import Thread


class Server:
  def __init__(self):
    self.conn = socket.socket()
    self.conn.bind(('0.0.0.0', 1339))
    self.conn.listen(5)
    
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
    print('Sending data')
    for other_client in self.clients:
      if other_client is not client:
        try:
          other_client.conn.send(data)
        except socket.error:
          self.term_client(other_client)
          
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


def main():
  server = Server()


if __name__ == '__main__':
  main()
