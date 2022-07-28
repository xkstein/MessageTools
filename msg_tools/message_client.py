'''
The client queries, so this exits on read
'''
from .message import Message
import selectors
import socket
import struct
import pickle

class ClientMessage(Message):
    def __init__(self, selector, sock, addr, request=None):
        super().__init__(selector, sock, addr)
        self.logger.debug(f'Instance Created with request: {request}')
        self.response = request
    
    def write(self):
        if not self._response_queued:
            self._queue_response()
        if not self.outb:
            return

        self._write()

        if not self.outb:
            self.logger.debug(f'Writing Complete')
            self._response_queued = False

    def read(self):
        '''This reads and unpacks data from the socket'''
        self._read()

        if self._data_length is None:
            self.inb, self._data_length = self.get_data_length(self.inb)
            self.logger.debug(f'Package Length: {self._data_length}')

        if self._data_length is not None:
            self.logger.debug(f'Data Recieved {len(self.inb)}')
            if len(self.inb) >= self._data_length:
                self.in_data = self.decode(self.inb[:self._data_length])

        if self.in_data is not None:
            self.logger.debug(f'Decoded Package: {self.in_data}')
            self.logger.debug('Processing Response')
            self.process_response()
            self._close()
