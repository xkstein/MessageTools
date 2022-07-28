'''
This is a little utility package to help with client server commications

Packet Structure
Header: (big-endian 4 byte long) length of package
Body: Fewer than 2**31 bytes of pickled data
'''
import selectors
import socket
import struct
import pickle
import logging

class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.reading = False

        self._data_length = None

        self.inb = b""
        self.in_data = None
        self.outb = b""
        self.response = None

        self._response_queued = False

        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def encode(data):
        packed_data = pickle.dumps(data, 0)
        assert len(packed_data) > 0, 'Packed has 0 length!'
        packed_data_length = struct.pack(">L", len(packed_data))
        return packed_data_length + packed_data

    @staticmethod
    def decode(data):
        return pickle.loads(data)

    @staticmethod
    def get_data_length(data):
        '''This reads and trims off the message header'''
        pre_header_size = struct.calcsize(">L")
        if len(data) < pre_header_size: return data, None

        packed_data_length = data[:pre_header_size]
        data = data[pre_header_size:]
        data_length = struct.unpack(">L", packed_data_length)[0]
        return data, data_length

    def handle_connection(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def _query(self, obj, query):
        '''Not used in communication flow
        Utility for querying OUTSIDE objects'''
        if isinstance(query, tuple):
            return getattr(obj, query[0])(*query[1:])
        if isinstance(query, str):
            return getattr(obj, query)()

    def _checkattr(self, obj, query):
        '''Not used in communication flow
        Utility for checking if obj has attribute (str or first el of tuple)'''
        arg = query
        if isinstance(query, tuple):
            arg = query[0]
        return hasattr(obj, arg)

    def _read(self):
        '''This reads raw data from the socket'''
        recv_data = self.sock.recv(4096)

        if recv_data:
            self.logger.info(f'Data recieved: {recv_data}')
            self.inb += recv_data
            self.reading = True

    def process_response(self):
        '''This just resets the register, specify action from subclass'''
        self._data_length = None
        self.inb = b""
        self.in_data = None
        self.logger.info(f'Input buffers cleared')

    def _queue_response(self):
        if self.response:
            self.logger.info(f'Response Queued: {self.response}')
            self.outb = self.encode(self.response)
            self._response_queued = True
            self.response = None
        elif self.response is not None:
            self.logger.info(f'No response found, sending return character')
            self.response = '\n'

    def _write(self):
        '''Writes data to socket'''
        try:
            sent = self.sock.send(self.outb)
        except BlockingIOError:
            pass
        else:
            self.logger.info(f'Data Written: {self.outb[:sent]}')
            self.outb = self.outb[sent:]
            if not self.outb:
                self._response_queued = False

    def _close(self):
        self.logger.debug(f'Closing socket at {self.addr}')
        self.selector.unregister(self.sock)
        self.sock.close()
