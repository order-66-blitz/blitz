from typing import Optional

from actions import TurretShootAction
from game_message import GameMessage, TurretType, TurretStation
from task import Task, TaskActions


class AttackTask(Task):
    def get_turret(self, game: GameMessage) -> Optional[TurretStation]:
        turrets = game.get_own_ship().stations.turrets
        return next((t for t in turrets if t.turretType == TurretType.Fast), None)

    def is_usable(self, game: GameMessage) -> bool:
        return self.get_turret(game) is not None

    def get_actions(self, game: GameMessage) -> TaskActions:
        turret = self.get_turret(game)
        if turret.charge < 0:
            # Cannot shoot yet
            return TaskActions(turret.id, [])

        # Shoot straight
        return TaskActions(turret.id, [
            TurretShootAction(turret.id),
        ])

    def get_score(self, game: GameMessage) -> float:
        return 80
