from dataclasses import dataclass
from typing import Optional

from actions import StationAction
from game_message import GameMessage

@dataclass
class TaskActions:
    station_id: str
    actions: list[StationAction]


class Task:
    def get_actions(self, game: GameMessage) -> Optional[TaskActions]:
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
