"""
Author:
melektron

class that handles receiving and sending packets
"""

import socket
import json


class GameSocket(socket.socket):
    
    input_buffer: bytes = b""

    def send_packet(self, packet: dict) -> None:
        spacket = f"\x01{json.dumps(packet)}\x04"
        self.send(spacket.encode("ASCII"))

    def recv_packet(self) -> dict:
        store_bytes: bool = False
        msg_body: str = ""
        msg: bytes = b""
        while True:
            # include unused bytes from last receive
            current_buffer = self.input_buffer + msg
            for index, byte in enumerate(current_buffer):
                match byte:
                    case 0x01:  # start marker
                        store_bytes = True

                    case 0x04:  # end marker
                        if index == 0:
                            continue

                        # store rest of bytes for next call
                        self.input_buffer = current_buffer[index:]
                        # parse msg_body as json and return
                        print(f"{msg_body=}")
                        return json.loads(msg_body)

                    case _:  # content
                        if store_bytes:    # only store bytes between start and end marker
                            msg_body += current_buffer[index:index+1].decode("ASCII")
            # read new bytes if end of message has not been reached
            msg: bytes = self.recv(1024)
            if msg == b"":
                raise ValueError
