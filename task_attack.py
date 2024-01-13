from typing import Optional

from actions import TurretShootAction, StationAction
from game_message import GameMessage, TurretType, TurretStation
from task import Task


class AttackTask(Task):
    TURRET_TYPE_PRIORITY = [
        TurretType.Cannon,
        TurretType.Fast,
        TurretType.Sniper,
    ]

    def get_turret(self, game: GameMessage) -> Optional[TurretStation]:
        turrets = game.get_own_ship().stations.turrets
        for ttype in self.TURRET_TYPE_PRIORITY:
            turret = next((t for t in turrets if t.turretType == ttype), None)
            if turret:
                return turret

    def is_usable(self, game: GameMessage) -> bool:
        return self.get_turret(game) is not None

    def is_station_exclusive(self) -> bool:
        return True

    def get_station_id(self, game: GameMessage) -> str:
        return self.get_turret(game).id

    def get_actions(self, game: GameMessage) -> list[StationAction]:
        turret = self.get_turret(game)
        if turret.charge < 0:
            # Cannot shoot yet
            return []

        if turret.operator is None:
            # Not arrived yet
            return []

        # Shoot straight
        return [TurretShootAction(turret.id)]

    def get_score(self, game: GameMessage) -> float:
        return 80
