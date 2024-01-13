from dataclasses import dataclass

from actions import StationAction
from game_message import GameMessage



class Task:
    def reset(self) -> None:
        pass

    def is_usable(self, game: GameMessage) -> bool:
        return True

    def is_station_exclusive(self) -> bool:
        return False

    def get_station_id(self, game: GameMessage) -> str:
        raise NotImplementedError

    def get_actions(self, game: GameMessage) -> list[StationAction]:
        raise NotImplementedError

    def get_score(self, game: GameMessage) -> float:
        raise NotImplementedError
