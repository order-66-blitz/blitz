import math
from dataclasses import dataclass
from typing import Optional

from actions import TurretShootAction, TurretRotateAction, StationAction
from game_message import GameMessage, TurretType, DebrisType, Vector, Debris, TurretStation
from task import Task


def newton(f, x0, h=1e-5, tol=1e-6, nmax=20) -> float:
    df = lambda x: (f(x + h) - f(x - h)) / (2 * h)
    xn = x0
    for i in range(nmax):
        xn1 = xn - f(xn) / df(xn)
        if abs(xn1 - xn) < tol:
            return xn1
        xn = xn1
    return xn


@dataclass
class DebrisChoice:
    debris: Debris
    score: float
    angle: float
    intersection: Vector
    time_to_hit: float


class DebrisProtectionTask(Task):
    handled_ids: dict[str, int]
    last_operator: Optional[str]

    HANDLED_ID_TIMEOUT = 20  # ticks

    SCORE_DISTANCE = 1

    METEOR_SIZE_MULTIPLIER = {
        DebrisType.Small: 10.0,
        DebrisType.Medium: 50.0,
        DebrisType.Large: 20000.0,
    }

    TURRET_TYPE_PRIORITY = [
        TurretType.Normal,
        TurretType.EMP,
    ]

    def __init__(self) -> None:
        self.handled_ids = {}
        self.last_operator = None

    def reset(self) -> None:
        self.handled_ids = {}
        self.last_operator = None

    def get_turret(self, game: GameMessage) -> Optional[TurretStation]:
        turrets = game.get_own_ship().stations.turrets
        for ttype in self.TURRET_TYPE_PRIORITY:
            turret = next((t for t in turrets if t.turretType == ttype), None)
            if turret.operator is not None and turret.operator != self.last_operator:
                # Turret already in use
                continue
            if turret:
                return turret
        return None

    def is_usable(self, game: GameMessage) -> bool:
        return self.get_turret(game) is not None

    def is_station_exclusive(self) -> bool:
        return True

    def get_station_id(self, game: GameMessage) -> str:
        return self.get_turret(game).id

    @staticmethod
    def find_projectile_debris_intersection(cannon_pos: Vector, meteor_pos: Vector, meteor_speed: Vector,
                                            rocket_speed: float) -> tuple[float, float, Vector]:
        p1x = cannon_pos.x
        p1y = cannon_pos.y
        p2x = meteor_pos.x
        p2y = meteor_pos.y
        v2x = meteor_speed.x
        v2y = meteor_speed.y
        v1 = rocket_speed

        x0 = math.atan2(p2y - p1y, p2x - p1x)
        angle = newton(lambda t: (v1 * math.cos(t) - v2x) / (v1 * math.sin(t) - v2y) - (p2x - p1x) / (p2y - p1y), x0)
        t = (p2x - p1x) / (v1 * math.cos(angle) - v2x)
        intersection = cannon_pos + Vector(math.cos(angle), math.sin(angle)) * v1 * t
        return math.degrees(angle), t, intersection

    @staticmethod
    def does_debris_intersect_ship(game: GameMessage, ship_pos: Vector, debris: Debris) -> bool:
        a = debris.velocity.y / debris.velocity.x
        b = debris.position.y - debris.position.x * a
        dist = abs(a * ship_pos.x - ship_pos.y + b) / math.sqrt(a**2 + 1)
        return dist < debris.radius + game.constants.ship.stations.shield.shieldRadius

    def get_actions(self, game: GameMessage) -> list[StationAction]:
        ship = game.get_own_ship()
        turret = self.get_turret(game)

        if turret.charge < 0:
            # Cannot shoot yet
            return []

        if turret.operator is None:
            # Not arrived yet
            return []

        self.last_operator = turret.operator

        cannon_pos = turret.worldPosition
        rocket_speed = game.constants.ship.stations.turretInfos[turret.turretType].rocketSpeed

        # Remove old handled IDs
        for id, timeout in list(self.handled_ids.items()):
            if timeout <= game.tick:
                del self.handled_ids[id]

        # Find the nearest meteor
        choices: list[DebrisChoice] = []
        for debris in game.debris:
            if debris.id in self.handled_ids:
                # Debris already shot at recently.
                continue

            # Find the cannon angle required to hit meteor
            angle, time_to_hit, intersection_bullet = DebrisProtectionTask.find_projectile_debris_intersection(
                cannon_pos, debris.position, debris.velocity, rocket_speed)

            # Find debris--ship intersection
            _, _, intersection_ship = DebrisProtectionTask.find_projectile_debris_intersection(
                ship.worldPosition, debris.position, debris.velocity, 1)

            if not self.does_debris_intersect_ship(game, ship.worldPosition, debris):
                # Projectile would not hit ship
                continue

            score = 1 / time_to_hit
            score *= DebrisProtectionTask.METEOR_SIZE_MULTIPLIER[debris.debrisType]  # Choose bigger meteors

            choices.append(DebrisChoice(debris, score, angle, intersection_bullet, time_to_hit))

        if not choices:
            # No meteor could be chosen
            return []

        chosen = max(choices, key=lambda c: c.score)

        # Mark meteor as handled until it is destroyed
        self.handled_ids[chosen.debris.id] = math.ceil(game.tick + chosen.time_to_hit)

        # Find the new cannon angle to rotate
        curr_angle = turret.orientationDegrees
        if curr_angle > 180:
            curr_angle -= 360

        return [
            # TurretRotateAction(turret.id, angle=10),
            TurretRotateAction(turret.id, angle=(chosen.angle - curr_angle)),
            TurretShootAction(turret.id),
        ]

    def get_score(self, game: GameMessage) -> float:
        # TODO
        return 200
