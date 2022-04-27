from core.gamesocket import GameSocket, recv_packet, send_packet
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
import socket


class Server(GameSocket):
    running: bool = True
    default_timeout: float = .2
    __clients: list[socket.socket]
    __Pool: ThreadPoolExecutor

    def __init__(self, port: int) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(("0.0.0.0", port))
        self.listen()

        # later used variables
        self.__clients = []
        self.__Pool = ThreadPoolExecutor(max_workers=100)

        self.__msg_pool: list[tuple[dict, socket.socket]] = []

    @property
    def clients(self) -> list[socket.socket]:
        return self.__clients

    def accept_clients(self) -> None:
        self.settimeout(self.default_timeout)
        while self.running:
            try:
                cl, address = self.accept()
                print(f"New user: {address}")

                self.__Pool.submit(self.handle_client, cl)

            except TimeoutError:
                continue

            except (Exception,):
                print(f"Error in thread (accept_clients): {format_exc()}")

    def handle_client(self, client: socket.socket) -> None:
        self.__clients.append(client)

        client.settimeout(self.default_timeout)
        while self.running:
            try:
                msg = recv_packet(client)

                self.__msg_pool.append((msg, client))

            except TimeoutError:
                continue

            except (Exception,):
                print(f"Error in thread(handle_client, {client}): {format_exc()}")
                client.close()
                self.__clients.remove(client)
                return

    def send_all(self) -> None:
        while self.running:
            for msg, cl in self.__msg_pool:
                for client in self.clients:
                    if client is not cl:
                        send_packet(client, msg)

    def end(self) -> None:
        self.running = False

    def __del__(self) -> None:
        self.end()


def main() -> None:
    s = Server(port=12345)
    s.accept_clients()


if __name__ == "__main__":
    main()
