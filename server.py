from traceback import format_exc
from threading import Thread
import socket


class Server(socket.socket):
    running: bool = True
    default_timeout: float = .2
    __clients: list[socket.socket]

    def __init__(self, port: int) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(("0.0.0.0", port))
        self.listen()

        # later used variables
        self.__clients = []

    @property
    def clients(self) -> list[socket.socket]:
        return self.__clients

    def accept_clients(self) -> None:
        self.settimeout(self.default_timeout)
        while self.running:
            try:
                cl, address = self.accept()
                print(f"New user: {address}")
                Thread(target=self.handle_client, args=[cl]).start()

            except TimeoutError:
                continue

            except (Exception,):
                print(f"Error in thread (accept_clients): {format_exc()}")

    def handle_client(self, client: socket.socket) -> None:
        self.__clients.append(client)

        client.settimeout(self.default_timeout)
        while self.running:
            try:
                msg = client.recv(2048)
                if msg == b"":
                    self.__clients.remove(client)
                    client.close()
                    print("disconnected after receiving nothing")
                    return

                self.send_all(msg, [client])

            except TimeoutError:
                continue

            except (Exception,):
                print(f"Error in thread(handle_client, {client}): {format_exc()}")

    def send_all(self, message: bytes, exclude: list[socket.socket] = []) -> None:
        for client in self.clients:
            if client not in exclude:
                client.sendall(message)

    def end(self) -> None:
        self.running = False

    def __del__(self) -> None:
        self.end()


def main() -> None:
    s = Server(port=12345)
    s.accept_clients()


if __name__ == "__main__":
    main()
