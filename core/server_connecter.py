from core.groups import Players
from core.new_types import Vec2
from threading import Thread
from core import Player
import typing as tp
import socket
import json


class Connection(socket.socket):
    running: bool = True
    __server_address: tuple[str, int]

    def __init__(self, server_address: tuple[str, int]) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(server_address)

        self.__server_address = server_address

        Thread(target=self.receive_player_data).start()

    @property
    def server_address(self) -> tuple[str, int]:
        return self.__server_address

    def receive_player_data(self) -> None:
        self.settimeout(.2)
        while self.running:
            try:
                msg = self.recv(2048)
                data: dict[str, tp.Any] = json.loads(msg.decode())

                selected_player: Player = ...
                for player in Players.sprites():
                    if player.name == data["name"]:
                        selected_player = player
                        break
                if selected_player is ...:
                    selected_player = Player(spawn_point=Vec2(), name=data["name"])

                self.update_player(selected_player, data)

            except TimeoutError:
                continue

    def send_update(self, player: Player) -> None:
        msg = {
            "name": player.name,
            "hp": player.hp,
            "pos": {
                "x": player.position.x,
                "y": player.position.y,
            },
            "vel": {
                "x": player.velocity.x,
                "y": player.velocity.y,
            },
        }

        self.sendall(json.dumps(msg).encode())

    @staticmethod
    def update_player(player: Player, update_from: dict) -> None:
        player.position = Vec2.from_cartesian(update_from["pos"]["x"], update_from["pos"]["y"])
        player.velocity = Vec2.from_cartesian(update_from["vel"]["x"], update_from["vel"]["y"])
        player.hp = update_from["hp"]
