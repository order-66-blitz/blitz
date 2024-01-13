from actions import StationAction
from game_message import GameMessage
from task import Task


class Strategy:
    def reset(self) -> None:
        raise NotImplementedError

    def get_tasks(self, game: GameMessage) -> list[Task]:
        """
        Get station actions for a station.
        """
        raise NotImplementedError

    def get_score(self, game: GameMessage) -> float:
        """
        Get strategy score for a station
        """
        raise NotImplementedError
