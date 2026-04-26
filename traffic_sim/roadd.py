class Road:
    def __init__(self, road_id, start_junction, end_junction, length=10.0, speed=2.0, capacity=10):
        self.road_id = road_id
        self.start_junction = start_junction
        self.end_junction = end_junction
        self.length = length
        self.speed = speed
        self.capacity = capacity
        self.vehicles = []

        self.occupancy_history = []
        self.waiting_history = []

    def can_enter(self):
        return len(self.vehicles) < self.capacity

    def enter(self, vehicle):
        if not self.can_enter():
            return False
        vehicle.current_road = self.road_id
        vehicle.position = 0.0
        vehicle.state = "moving"
        self.vehicles.append(vehicle)
        return True

    def remove(self, vehicle):
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

    def update_positions(self, dt):
        for vehicle in self.vehicles:
            if vehicle.finished:
                continue

            if vehicle.state == "moving":
                move = self.speed * dt
                vehicle.position += move
                vehicle.total_distance += move

                if vehicle.position >= self.length:
                    vehicle.position = self.length
                    vehicle.state = "waiting"
            elif vehicle.state == "waiting":
                vehicle.waiting_time += dt

        self.occupancy_history.append(len(self.vehicles))
        self.waiting_history.append(sum(1 for v in self.vehicles if v.state == "waiting"))

    def first_waiting_vehicle(self):
        waiting = [v for v in self.vehicles if v.state == "waiting"]
        if not waiting:
            return None
        waiting.sort(key=lambda v: v.vehicle_id)
        return waiting[0]