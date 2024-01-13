from game_message import GameMessage
from task import Task, TaskActions


class ShieldTask(Task):
    def is_usable(self, game: GameMessage) -> bool:
        return len(game.get_own_ship().stations.shields) > 0

    def get_actions(self, game: GameMessage) -> TaskActions:
        ship = game.get_own_ship()
        shields = ship.stations.shields
        station_id = shields[0].id
        return TaskActions(station_id, [])

    def get_score(self, game: GameMessage) -> float:
        ship = game.get_own_ship()
        shield_percent = ship.currentShield / game.constants.ship.maxShield
        if shield_percent < 0.10:
            return 100
        elif shield_percent < 0.50:
            return 50
        else:
            return 10
