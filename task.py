from dataclasses import dataclass

from actions import StationAction
from game_message import GameMessage


@dataclass
class TaskActions:
    station_id: str
    actions: list[StationAction]


class Task:
    def is_usable(self, game: GameMessage) -> bool:
        return True

    def get_actions(self, game: GameMessage) -> TaskActions:
        """
        Get station actions for a task.
        All actions must be for the same station.
        """
        raise NotImplementedError

    def get_score(self, game: GameMessage) -> float:
        """
        Get task score.
        """
        raise NotImplementedError
