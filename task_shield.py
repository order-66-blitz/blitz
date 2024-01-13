from actions import StationAction
from game_message import GameMessage
from task import Task


class ShieldTask(Task):
    def is_usable(self, game: GameMessage) -> bool:
        return len(game.get_own_ship().stations.shields) > 0

    def is_station_exclusive(self) -> bool:
        # TODO better to use multiple shields?
        return False

    def get_station_id(self, game: GameMessage) -> str:
        ship = game.get_own_ship()
        shields = ship.stations.shields
        return shields[0].id

    def get_actions(self, game: GameMessage) -> list[StationAction]:
        return []

    def get_score(self, game: GameMessage) -> float:
        ship = game.get_own_ship()
        shield_percent = ship.currentShield / game.constants.ship.maxShield
        if shield_percent < 0.10:
            return 100
        elif shield_percent < 0.50:
            return 50
        else:
            return 10
