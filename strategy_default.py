import math

from actions import StationAction
from game_message import GameMessage, TurretType
from strategy import Strategy
from task import Task
from task_debris_protection import DebrisProtectionTask
from task_radar import RadarTask
from task_shield import ShieldTask


class DefaultStrategy(Strategy):
    def get_tasks(self, game: GameMessage) -> list[Task]:
        """
        Get station actions for a station.
        """
        # TODO
        return [
            ShieldTask(),
            ShieldTask(),
            RadarTask(),
            DebrisProtectionTask(hit_radius=50),
        ]

    def get_score(self, game: GameMessage) -> float:
        """
        Get strategy score for a station
        """
        # TODO
        return 0
