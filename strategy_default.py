import math
from typing import Optional

from actions import StationAction
from game_message import GameMessage, TurretType
from strategy import Strategy
from task import Task
from task_attack import AttackTask
from task_debris_protection import DebrisProtectionTask
from task_radar import RadarTask
from task_shield import ShieldTask


class DefaultStrategy(Strategy):
    tasks: Optional[list[Task]]

    def __init__(self):
        self.tasks = None

    def reset(self) -> None:
        self.tasks = None

    def get_tasks(self, game: GameMessage) -> list[Task]:
        """
        Get station actions for a station.
        """
        if self.tasks is None:
            self.tasks = [
                ShieldTask(),
                ShieldTask(),
                ShieldTask(),
                ShieldTask(),
                RadarTask(),
                DebrisProtectionTask(),
                # AttackTask(),
            ]
        return self.tasks

    def get_score(self, game: GameMessage) -> float:
        """
        Get strategy score for a station
        """
        # TODO
        return 0
