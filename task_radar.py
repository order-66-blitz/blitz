from game_message import GameMessage
from task import Task, TaskActions


class RadarTask(Task):
    def is_usable(self, game: GameMessage) -> bool:
        return len(game.get_own_ship().stations.radars) > 0

    def get_actions(self, game: GameMessage) -> TaskActions:
        ship = game.get_own_ship()
        radars = ship.stations.radars
        station_id = radars[0].id
        return TaskActions(station_id, [])

    def get_score(self, game: GameMessage) -> float:
        # TODO
        return 50
