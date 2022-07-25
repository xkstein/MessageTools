from message_server import ServerMessage

class CompressorMonitorServer(ServerMessage):
    def __init__(self, selector, sock, addr, com_port=None):
        self.com_port = com_port
        super().__init__(selector, sock, addr)

    def process_response(self):
        print(self.in_data)
        f70_querys = []
        for query in self.in_data:
            if self._checkattr(SHICryoF70, query):
                f70_querys.append(query)

        responses = []
        if self.com_port is not None:
            try:
                with SHICryoF70(com_port=self.com_port) as f70:
                    for query in f70_querys:
                        response = self._query(f70, query)
                        responses.append(response)
            except F70Exception:
                pass
        self.response = responses
        print(responses)
        return super().process_response()

'''
def unpack_img(data):
    pdb.set_trace()
    payload_size = struct.calcsize(">L")
    packed_msg_size = data[:payload_size]

    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]
    print("msg_size: {}".format(msg_size))

    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    cv2.imshow('ImageWindow',frame)
    cv2.waitKey(10)
'''
