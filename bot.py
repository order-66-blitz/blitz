from dataclasses import dataclass
from typing import Union

from actions import *
from game_message import *
from strategy import Strategy
from strategy_default import DefaultStrategy
from task import Task

STRATEGIES = {
    "default": DefaultStrategy(),
}


@dataclass
class TaskAssignment:
    station_id: str
    score: float
    task_index: int
    assigned: bool


class Bot:
    last_max_strategy_name: str
    task_assignments: dict[str, Optional[TaskAssignment]]

    def __init__(self):
        self.last_max_strategy_name = ""
        self.task_assignments = {}
        print("Bot start")

    def choose_strategy(self, game: GameMessage) -> Strategy:
        # Choose strategy to apply
        max_strategy_name = ""
        max_strategy_score = -math.inf
        for name, strategy in STRATEGIES.items():
            score = strategy.get_score(game)
            if score > max_strategy_score:
                max_strategy_name = name
                max_strategy_score = score

        strategy = STRATEGIES[max_strategy_name]

        if max_strategy_name != self.last_max_strategy_name:
            # Strategy changed, reset its tasks
            strategy.reset()
            self.reset_assignments(game)
            print(f"Using '{max_strategy_name}' strategy")

        self.last_max_strategy_name = max_strategy_name

        return strategy

    def reset_assignments(self, game: GameMessage) -> None:
        self.task_assignments = {}
        ship = game.get_own_ship()
        for crew in ship.crew:
            self.task_assignments[crew.id] = None

    def assign_task(self, game: GameMessage, task: Task, task_index: int) -> Union[None, str, CrewMoveAction]:
        ship = game.get_own_ship()
        score = task.get_score(game)
        station_id = task.get_station_id(game)

        # Find everyone who can go to the station
        allowed_crew = {}
        for crew in ship.crew:
            all_crew_dist = (crew.distanceFromStations.shields + crew.distanceFromStations.turrets +
                             crew.distanceFromStations.helms + crew.distanceFromStations.radars)
            crew_dist = next((s.stationPosition for s in all_crew_dist if s.stationId == station_id), None)
            assignment = self.task_assignments[crew.id]
            if assignment and assignment.assigned:
                continue
            if crew_dist:
                allowed_crew[crew.id] = crew_dist
        if not allowed_crew:
            return "unassignable"

        reason: str

        # Check if someone is already there
        for crew_id, assignment in self.task_assignments.items():
            if assignment and assignment.station_id == station_id and not assignment.assigned:
                reason = "not moved"
                assigned = crew_id
                break
        else:
            for crew_id in allowed_crew.keys():
                # Find someone who does nothing
                assignment = self.task_assignments[crew_id]
                if assignment is None:
                    assigned = crew_id
                    reason = "idle"
                    break
            else:
                # Find person with lowest score task assignment
                min_score = math.inf
                min_id = ""
                for crew_id in allowed_crew.keys():
                    assignment = self.task_assignments[crew_id]
                    if assignment.score < min_score:
                        min_score = assignment.score
                        min_id = crew_id
                assigned = min_id
                reason = "better score"

        old_assignment = self.task_assignments[assigned]
        self.task_assignments[assigned] = TaskAssignment(station_id, score, task_index, True)

        print(f"Crew '{assigned}' went to station '{station_id}' ({task.__class__.__name__}) because: {reason}")

        if not old_assignment or old_assignment.station_id != station_id:
            return CrewMoveAction(assigned, allowed_crew[assigned])
        return None

    def get_next_move(self, game: GameMessage):
        ship = game.get_own_ship()
        strategy = self.choose_strategy(game)
        all_tasks = strategy.get_tasks(game)

        tasks = list(enumerate(all_tasks))

        # Assign turret operators even if they haven't arrived yet...
        for turret in ship.stations.turrets:
            for crew_id, assignment in self.task_assignments.items():
                if assignment and not turret.operator and assignment.station_id == turret.id:
                    turret.operator = crew_id

        for assignment in self.task_assignments.values():
            if assignment is not None:
                assignment.assigned = False

        actions = []

        crew_count = len(ship.crew)
        while crew_count > 0:
            # Discard tasks that can't be performed
            tasks = [t for t in tasks if t[1].is_usable(game)]
            # Get best tasks
            tasks.sort(key=lambda t: t[1].get_score(game), reverse=True)
            if not tasks:
                break  # No tasks left to assign

            task_index, task = tasks[0]
            station_id = task.get_station_id(game)
            if task.is_station_exclusive():
                skip = False
                for assignment in self.task_assignments.values():
                    if (assignment is not None and assignment.station_id == station_id and
                            assignment.task_index != task_index):
                        # There's already someone there and it's not for this task
                        del tasks[0]
                        skip = True
                        break
                if skip:
                    continue

            move_action = self.assign_task(game, task, task_index)
            if move_action != "unassignable":
                if move_action:
                    actions.append(move_action)

                actions += task.get_actions(game)

            del tasks[0]
            crew_count -= 1

        # Reset all unassigned tasks (if they have state)
        assigned_indices = {a.task_index for a in self.task_assignments.values() if a is not None}
        for i, task in enumerate(all_tasks):
            if i not in assigned_indices:
                task.reset()

        return actions
