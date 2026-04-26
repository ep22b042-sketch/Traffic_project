import itertools
import statistics

from .vehicle import Vehicle
from .routing import shortest_path_road_ids
from .visualization import Visualizer


class Simulation:
    def __init__(self, dt=1.0, total_steps=60):
        self.dt = dt
        self.total_steps = total_steps
        self.time = 0.0

        self.junctions = {}
        self.roads = {}
        self.sources = []
        self.sinks = {}

        self.vehicle_counter = itertools.count(1)
        self.active_vehicles = []
        self.finished_vehicles = []
        self.generated_count = 0
        self.dropped_count = 0

        self.destination_colors = {}
        self.default_colors = [
            "red", "blue", "green", "orange", "purple", "cyan", "magenta", "brown"
        ]
        self.visualizer = None

    def add_junction(self, junction):
        self.junctions[junction.junction_id] = junction

    def add_road(self, road):
        self.roads[road.road_id] = road
        self.junctions[road.start_junction].add_outgoing_road(road)
        self.junctions[road.end_junction].add_incoming_road(road)

    def add_source(self, source):
        self.sources.append(source)

    def add_sink(self, sink):
        self.sinks[sink.junction_id] = sink

    def _get_color_for_destination(self, dest):
        if dest not in self.destination_colors:
            idx = len(self.destination_colors) % len(self.default_colors)
            self.destination_colors[dest] = self.default_colors[idx]
        return self.destination_colors[dest]

    def build_visualizer(self):
        self.visualizer = Visualizer(self.junctions, self.roads)

    def _spawn_vehicle(self, source):
        destination = source.choose_destination()
        if destination == source.junction_id:
            return

        route = shortest_path_road_ids(
            self.junctions,
            self.roads,
            source.junction_id,
            destination,
        )
        if not route:
            self.dropped_count += 1
            return

        vehicle = Vehicle(
            vehicle_id=next(self.vehicle_counter),
            source=source.junction_id,
            destination=destination,
            route=route,
            color=self._get_color_for_destination(destination),
            created_time=self.time,
        )
        first_road = self.roads[route[0]]
        if first_road.enter(vehicle):
            vehicle.current_road = first_road.road_id
            self.active_vehicles.append(vehicle)
            self.generated_count += 1
        else:
            self.dropped_count += 1

    def _generate_vehicles(self):
        for source in self.sources:
            count = source.maybe_generate(self.dt)
            for _ in range(count):
                self._spawn_vehicle(source)

    def _update_roads(self):
        for road in self.roads.values():
            road.update_positions(self.dt)

    def _process_junctions(self):
        for junction in self.junctions.values():
            vehicle, next_road = junction.choose_vehicle_round_robin(self.roads)
            if vehicle is None:
                continue

            current_road = self.roads[vehicle.current_road]
            current_road.remove(vehicle)

            if next_road is None:
                sink = self.sinks.get(junction.junction_id)
                if sink is not None and vehicle.destination == junction.junction_id:
                    sink.accept(vehicle)
                    vehicle.finished_time = self.time
                    self.finished_vehicles.append(vehicle)
                else:
                    vehicle.finished = True
                    vehicle.state = "finished"
                    vehicle.finished_time = self.time
                    self.finished_vehicles.append(vehicle)
                continue

            vehicle.route_index += 1
            next_road.enter(vehicle)

        self.active_vehicles = [v for v in self.active_vehicles if not v.finished]

    def step(self, step_num):
        self._generate_vehicles()
        self._update_roads()
        self._process_junctions()

        if self.visualizer is not None:
            self.visualizer.save_frame(self.roads, step_num)

        self.time += self.dt
    
    def run(self, gif_path="traffic_simulation.gif"):
        if self.visualizer is None:
            self.build_visualizer()

        for step_num in range(self.total_steps):
            self.step(step_num)

        gif_file = self.visualizer.make_gif(gif_path)
        stats = self.get_statistics()
        return gif_file, stats

    def get_statistics(self):
        travel_times = []
        waiting_times = []
        for v in self.finished_vehicles:
            if v.finished_time is not None:
                travel_times.append(v.finished_time - v.created_time)
                waiting_times.append(v.waiting_time)

        road_stats = {}
        for road_id, road in self.roads.items():
            road_stats[road_id] = {
                "avg_occupancy": statistics.mean(road.occupancy_history) if road.occupancy_history else 0.0,
                "max_occupancy": max(road.occupancy_history) if road.occupancy_history else 0,
                "avg_waiting": statistics.mean(road.waiting_history) if road.waiting_history else 0.0,
                "max_waiting": max(road.waiting_history) if road.waiting_history else 0,
            }

        stats = {
            "generated": self.generated_count,
            "finished": len(self.finished_vehicles),
            "dropped": self.dropped_count,
            "avg_travel_time": statistics.mean(travel_times) if travel_times else 0.0,
            "avg_waiting_time": statistics.mean(waiting_times) if waiting_times else 0.0,
            "throughput": len(self.finished_vehicles) / max(self.time, 1e-9),
            "road_stats": road_stats,
        }
        return stats