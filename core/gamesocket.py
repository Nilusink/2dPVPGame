"""
Author:
melektron

class that handles receiving and sending packets
"""

import socket
import json


class GameSocket(socket.socket):
    
    input_buffer: bytes = b""
    store_bytes: bool = False
    msg_body: str = ""

    def send_packet(self, packet: dict) -> None:
        spacket = f"\x01{json.dumps(packet)}\x04"
        self.send(spacket.encode("ASCII"))

    def recv_packet(self) -> dict:
        msg: bytes = b""
        while True:
            # include unused bytes from last receive
            current_buffer = self.input_buffer + msg
            for index, byte in enumerate(current_buffer):
                match byte:
                    case 0x01:  # start marker
                        self.store_bytes = True
                        self.msg_body = ""

                    case 0x04:  # end marker
                        if index == 0:
                            continue

                        self.store_bytes = False
                        # store rest of bytes for next call
                        self.input_buffer = current_buffer[index:]
                        # parse msg_body as json and return
                        return json.loads(self.msg_body)

                    case _:  # content
                        if self.store_bytes:    # only store bytes between start and end marker
                            self.msg_body += current_buffer[index:index+1].decode("ASCII")
                        pass

            msg: bytes = self.recv(1024)
