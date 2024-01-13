from actions import StationAction
from game_message import GameMessage
from strategy import Strategy
from task import Task
from task_shield import ShieldTask


class DefaultStrategy(Strategy):
    def get_tasks(self, game: GameMessage) -> list[Task]:
        """
        Get station actions for a station.
        """
        # TODO
        return [
            ShieldTask()
        ]

    def get_score(self, game: GameMessage) -> float:
        """
        Get strategy score for a station
        """
        # TODO
        return 0
