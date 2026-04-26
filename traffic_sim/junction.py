class Junction:
    def __init__(self, junction_id, x=0.0, y=0.0):
        self.junction_id = junction_id
        self.x = x
        self.y = y
        self.incoming_roads = []
        self.outgoing_roads = []
        self.rr_index = 0

    def add_incoming_road(self, road):
        self.incoming_roads.append(road)

    def add_outgoing_road(self, road):
        self.outgoing_roads.append(road)

    def choose_vehicle_round_robin(self, roads_by_id):
        n = len(self.incoming_roads)
        if n == 0:
            return None, None

        for step in range(n):
            idx = (self.rr_index + step) % n
            road = self.incoming_roads[idx]
            vehicle = road.first_waiting_vehicle()
            if vehicle is None:
                continue

            next_road_id = vehicle.next_road_id()
            if next_road_id is None:
                self.rr_index = (idx + 1) % n
                return vehicle, None

            next_road = roads_by_id[next_road_id]
            if next_road.can_enter():
                self.rr_index = (idx + 1) % n
                return vehicle, next_road

        return None, None