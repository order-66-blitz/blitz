from typing import Optional

from actions import StationAction
from game_message import GameMessage
from task import Task, TaskActions


class ShieldTask(Task):
    def get_actions(self, game: GameMessage) -> Optional[TaskActions]:
        ship = game.get_own_ship()
        shields = ship.stations.shields

        if not shields:
            return None

        station_id = shields[0].id
        return TaskActions(station_id, [])

    def get_score(self, game: GameMessage) -> float:
        # TODO
        return 100
