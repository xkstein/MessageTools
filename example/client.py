import socket
import selectors
from msg_tools import ClientMessage

sel = selectors.DefaultSelector()

HOST=''
PORT=8485

addr = (HOST, PORT)
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setblocking(False)
sock.connect_ex(addr)

event_type = selectors.EVENT_READ | selectors.EVENT_WRITE
mesg = ClientMessage(sel, sock, addr, 'request')
sel.register(sock, event_type, data=mesg)

counter = 0
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            #pdb.set_trace()
            key.data.handle_connection(mask)
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Exiting...")
finally:
    sel.close()
