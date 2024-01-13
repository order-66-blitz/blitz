from actions import StationAction
from game_message import GameMessage
from task import Task


class RadarTask(Task):
    def is_usable(self, game: GameMessage) -> bool:
        return len(game.get_own_ship().stations.radars) > 0

    def is_station_exclusive(self) -> bool:
        return True  # No reason to use radar with multiple users

    def get_station_id(self, game: GameMessage) -> str:
        ship = game.get_own_ship()
        radars = ship.stations.radars
        # TODO choose nearest radar
        return radars[0].id

    def get_actions(self, game: GameMessage) -> list[StationAction]:
        return []

    def get_score(self, game: GameMessage) -> float:
        # TODO
        return 30
