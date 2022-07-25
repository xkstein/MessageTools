'''
So the server is meant to be queried mainly, so it exits on write
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
            self.sock.close()
            self._close()
            self._response_queued = False

    def read(self):
        '''This reads and unpacks data from the socket'''
        self._read()

        if self._data_length is None:
            pre_header_size = struct.calcsize(">L")
            if len(self.inb) < pre_header_size: return

            packed_data_length = self.inb[:pre_header_size]
            self.inb = self.inb[pre_header_size:]
            self._data_length = struct.unpack(">L", packed_data_length)[0]

        if self._data_length is not None:
            if len(self.inb) >= self._data_length:
                self.in_data = self.decode(self.inb[:self._data_length])

        if self.in_data is not None:
            self.logger.debug(self.in_data)
            self.process_response()
