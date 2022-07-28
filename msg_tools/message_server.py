'''
So the server is meant to be queried, so it exits on write
'''
from .message import Message
import selectors
import socket
import struct
import pickle

class ServerMessage(Message):
    def write(self):
        if not self._response_queued:
            self._queue_response()
        if not self.outb:
            return

        self._write()

        if not self.outb:
            self.logger.debug(f'Writing Complete')
            self.sock.close()
            self._close()
            self._response_queued = False

    def read(self):
        '''This reads and unpacks data from the socket'''
        self._read()

        if self._data_length is None:
            self.inb, self._data_length = self.get_data_length(self.inb)
            self.logger.debug(f'Package Length: {self._data_length}')

        if self._data_length is not None:
            self.logger.debug(f'Data Recieved: {len(self.inb)}')
            if len(self.inb) >= self._data_length:
                self.in_data = self.decode(self.inb[:self._data_length])

        if self.in_data is not None:
            self.logger.debug(f'Decoded Package: {self.in_data}')
            self.logger.debug(f'Processing Response')
            self.process_response()
