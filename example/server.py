import socket
import selectors
import logging
from msg_tools import ServerMessage

class FakeServerMessage(ServerMessage):
    def __init__(self, selector, sock, addr):
        super().__init__(selector, sock, addr)
        logging.basicConfig(filename='example.log', 
                filemode='w', level=logging.DEBUG)

    def process_response(self):
        self.response = "howdy"
        return super().process_response()

def accept_connection(sock):
    '''Adds connection to selector'''
    conn, addr = sock.accept()
    print(f'Connected to {addr}')
    conn.setblocking(False)
    event_type = selectors.EVENT_READ | selectors.EVENT_WRITE
    mesg = FakeServerMessage(sel, conn, addr)
    sel.register(conn, event_type, data=mesg)

sel = selectors.DefaultSelector()

HOST=''
PORT=8485

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')
sock.bind((HOST,PORT))
print('Socket bind complete')
sock.listen(10)
print('Socket now listening')
sock.setblocking(False)
print(sock)
event_type = selectors.EVENT_READ | selectors.EVENT_WRITE

sel.register(sock, event_type, data=None)

counter = 0
try:
    while True:
        counter += 1
        print(f'counter {counter}', end='\r')
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                key.data.handle_connection(mask)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    sel.close()
