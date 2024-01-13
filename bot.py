import math

from strategy_default import DefaultStrategy
from game_message import *
from actions import *
import random

STRATEGIES = {
    "default": DefaultStrategy(),
}

class Bot:
    last_max_strategy_name: str

    def __init__(self):
        self.last_max_strategy_name = ""
        print("Bot start")

    def get_next_move(self, game: GameMessage):
        my_ship = game.get_own_ship()

        # Choose strategy to apply
        max_strategy_name = ""
        max_strategy_score = -math.inf
        for name, strategy in STRATEGIES.items():
            score = strategy.get_score(game)
            if score > max_strategy_score:
                max_strategy_name = name
                max_strategy_score = score

        if max_strategy_name != self.last_max_strategy_name:
            print(f"Using '{max_strategy_name}' strategy")

        strategy = STRATEGIES[max_strategy_name]
        self.last_max_strategy_name = max_strategy_name

        tasks = strategy.get_tasks(game)
        # Get best tasks
        tasks.sort(key=lambda t: t.get_score(game), reverse=True)

        tasks_actions = [t.get_actions(game) for t in tasks]
        # Discard tasks that can't be performed
        tasks_actions = [t for t in tasks_actions if t is not None]

        # Choose one task per crew member
        crew_count = len(my_ship.crew)
        chosen_tasks_actions = tasks_actions[:min(len(tasks_actions), crew_count)]

        # Find which crew is where
        crew_by_station = {}
        for crew in my_ship.crew:
            station = crew.currentStation
            if station not in crew_by_station:
                crew_by_station[station] = []
            crew_by_station[station].append(crew)

        actions = []

        # Use already stationed crew for tasks
        for i, task_actions in enumerate(reversed(chosen_tasks_actions)):
            task_station = task_actions.station_id
            if task_station in crew_by_station:
                # Someone is there already
                actions += task_actions.actions
                del crew_by_station[task_station][0]
                del chosen_tasks_actions[i]

        # Move remaining crew
        # TODO choose nearest
        remaining_crew = []
        for crews in crew_by_station.values():
            remaining_crew += crews
        for tasks in chosen_tasks_actions:
            crew = remaining_crew[0]
            del remaining_crew[0]

            all_crew_dist = (crew.distanceFromStations.shields + crew.distanceFromStations.turrets +
                                  crew.distanceFromStations.helms + crew.distanceFromStations.radars)
            station_id = tasks.station_id
            crew_dist = next((s.stationPosition for s in all_crew_dist if s.stationId == station_id), None)
            if not crew_dist:
                raise RuntimeError("Cannot go!")  # TODO choose only crew that can access station

            actions.append(CrewMoveAction(crew.id, crew_dist))

        # other_ships_ids = [shipId for shipId in game.shipsPositions.keys() if shipId != team_id]
        #
        # # Find who's not doing anything and try to give them a job?
        # idle_crewmates = [crewmate for crewmate in my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]
        #
        # for crewmate in idle_crewmates:
        #     station_to_move_to = random.choice(visitable_stations)
        #     actions.append(CrewMoveAction(crewmate.id, station_to_move_to.stationPosition))

        # Now crew members at stations should do something!
        # operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        # for turret_station in operatedTurretStations:
        #     possible_actions = [
        #         # Charge the turret.
        #         TurretChargeAction(turret_station.id),
        #         # Aim the turret itself.
        #         TurretLookAtAction(turret_station.id,
        #                            Vector(random.uniform(0, game.constants.world.width), random.uniform(0, game.constants.world.height))
        #         ),
        #         # Shoot!
        #         TurretShootAction(turret_station.id)
        #     ]
        #
        #     actions.append(random.choice(possible_actions))
        #
        # operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        # if operatedHelmStation:
        #     actions.append(ShipRotateAction(random.uniform(0, 360)))
        #
        # operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        # for radar_station in operatedRadarStation:
        #     actions.append(RadarScanAction(radar_station.id, random.choice(other_ships_ids)))

        return actions
