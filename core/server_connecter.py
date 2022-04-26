from core import Player, Bullet, AK47, Sniper, Rocket
from core.groups import Players
from core.new_types import Vec2
from threading import Thread
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
                try:
                    data: dict[str, tp.Any] = json.loads(msg.decode())

                except:
                    continue

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
            "events": player.events
        }

        if msg["events"]:
            print(f"{msg['events']=}")

        self.sendall(json.dumps(msg).encode())

    @staticmethod
    def update_player(player: Player, update_from: dict) -> None:
        player.position = Vec2.from_cartesian(update_from["pos"]["x"], update_from["pos"]["y"])
        player.velocity = Vec2.from_cartesian(update_from["vel"]["x"], update_from["vel"]["y"])
        player.hp = update_from["hp"]

        # handle events
        for event in update_from["events"]:
            print(f"caught event: {event}")
            match event["type"]:
                case "shot":
                    weapon: tp.Type[Bullet] = eval(event["weapon"])
                    direction = Vec2.from_polar(angle=event["angle"], length=1)
                    pos = Vec2.from_cartesian(event["pos"]["x"], event["pos"]["y"])
                    weapon(
                        position=pos,
                        direction=direction,
                        parent=player
                    )
                    print(f"shot with weapon {weapon}")
