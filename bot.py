from actions import *
from game_message import *
from strategy_default import DefaultStrategy

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
        # Discard tasks that can't be performed
        tasks = [t for t in tasks if t.is_usable(game)]
        # Get best tasks
        tasks.sort(key=lambda t: t.get_score(game), reverse=True)
        # Choose one task per crew member
        crew_count = len(my_ship.crew)
        tasks = tasks[:min(len(tasks), crew_count)]

        tasks_actions = [t.get_actions(game) for t in tasks]

        # Find which crew is where
        crew_by_station = {}
        for crew in my_ship.crew:
            station = crew.currentStation
            if station not in crew_by_station:
                crew_by_station[station] = []
            crew_by_station[station].append(crew)

        actions = []

        # Use already stationed crew for tasks
        for i, task_actions in reversed(list(enumerate(tasks_actions))):
            task_station = task_actions.station_id
            if task_station in crew_by_station and crew_by_station[task_station]:
                # Someone is there already
                actions += task_actions.actions
                del crew_by_station[task_station][0]
                del tasks_actions[i]

        # Move remaining crew
        # TODO choose nearest
        remaining_crew = []
        for crews in crew_by_station.values():
            remaining_crew += crews
        tries = len(remaining_crew) * 2
        while tries and remaining_crew and tasks_actions:
            tries -= 1

            tasks = tasks_actions[0]
            crew = remaining_crew[0]

            all_crew_dist = (crew.distanceFromStations.shields + crew.distanceFromStations.turrets +
                             crew.distanceFromStations.helms + crew.distanceFromStations.radars)
            station_id = tasks.station_id
            crew_dist = next((s.stationPosition for s in all_crew_dist if s.stationId == station_id), None)
            if not crew_dist:
                continue  # Cannot go!

            print(f"Crew '{crew.name}' went to station '{station_id}'")

            del remaining_crew[0]
            del tasks_actions[0]

            actions.append(CrewMoveAction(crew.id, crew_dist))

        return actions
