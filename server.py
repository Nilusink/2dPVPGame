from concurrent.futures import ThreadPoolExecutor
from core.gamesocket import GameSocket
from traceback import format_exc
import socket


def print_traceback(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)

        except Exception:
            print(f"\nexception in {func}\n")
            raise

    return wrapper


class Server(GameSocket):
    running: bool = True
    default_timeout: float = .2
    __clients: list[GameSocket]
    __Pool: ThreadPoolExecutor

    def __init__(self, port: int) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(("0.0.0.0", port))
        self.listen()

        # later used variables
        self.__clients = []
        self.__Pool = ThreadPoolExecutor(max_workers=100)

        # start sending thread
        self.__msg_pool: list[tuple[dict, GameSocket]] = []

        self.__Pool.submit(self.send_all)

    @property
    def clients(self) -> list[GameSocket]:
        return self.__clients

    @property
    def msg_pool(self) -> list[tuple[dict, GameSocket]]:
        tmp = self.__msg_pool.copy()
        self.__msg_pool.clear()
        return tmp

    def accept_clients(self) -> None:
        self.settimeout(self.default_timeout)
        while self.running:
            try:
                cl, address = self.accept()
                cl = GameSocket.from_socket(cl)

                cl.addr = address
                print(f"New user: {address}")

                self.__Pool.submit(self.handle_client, cl)

            except TimeoutError:
                continue

            except (Exception,):
                print(f"Error in thread (accept_clients): {format_exc()}")

    def handle_client(self, client: GameSocket) -> None:
        self.__clients.append(client)

        client.settimeout(self.default_timeout)
        while self.running:
            try:
                msg = client.recv_packet()
                self.__msg_pool.append((msg, client))

            except TimeoutError:
                continue

            except (Exception,):
                print(f"Error in thread(handle_client, {client}): {format_exc()}")
                client.close()
                self.__clients.remove(client)
                return

    @print_traceback
    def send_all(self) -> None:
        while self.running:
            tmp = self.msg_pool

            for msg, cl in tmp:
                for client in self.clients:
                    if client.addr != cl.addr:
                        client.send_packet(msg)

    def end(self) -> None:
        self.running = False

    def __del__(self) -> None:
        self.end()


def main() -> None:
    s = Server(port=12345)
    s.accept_clients()


if __name__ == "__main__":
    main()
