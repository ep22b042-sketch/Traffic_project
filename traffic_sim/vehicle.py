from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Vehicle:
    vehicle_id: int
    source: str
    destination: str
    route: List[str]  # list of road IDs
    color: str = "blue"

    route_index: int = 0
    current_road: Optional[str] = None
    position: float = 0.0
    finished: bool = False

    created_time: float = 0.0
    finished_time: Optional[float] = None
    waiting_time: float = 0.0
    total_distance: float = 0.0
    state: str = "moving"  # moving, waiting, finished

    def next_road_id(self) -> Optional[str]:
        if self.route_index + 1 < len(self.route):
            return self.route[self.route_index + 1]
        return None