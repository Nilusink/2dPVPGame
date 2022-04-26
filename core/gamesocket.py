"""
Author:
melektron

class that handles receiving and sending packets
"""

from ast import match_case
import socket
import json


class GameSocket(socket.socket):
    
    input_buffer: bytes
    store_bytes: bool = False
    msg_body: str = ""

    def send_packet(self, packet: dict) -> None:
        spacket = f"\x01{json.dumps(packet)}\x04"
        self.send(spacket.encode("ASCII"))

    def recv_packet(self) -> dict:
        while True:
            msg: bytes = []
            # include unused bytes from last receive
            current_buffer = self.input_buffer + msg
            for index, byte in enumerate(current_buffer):
                match byte:
                    case 0x01:  # start marker
                        self.store_bytes = True
                    case 0x04:  # end marker
                        self.store_bytes = False
                        # store rest of bytes for next call
                        self.input_buffer = current_buffer[index:]
                        # parse msg_body as json and return
                        return json.loads(self.msg_body)
                    case _: # content
                        if self.store_bytes:    # only store bytes between start and end marker
                            self.msg_body.append([byte].decode("ASCII"))
                        pass
            msg = self.recv(1024)


        
