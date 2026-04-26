class Sink:
    def __init__(self, sink_id, junction_id):
        self.sink_id = sink_id
        self.junction_id = junction_id
        self.received = 0

    def accept(self, vehicle):
        self.received += 1
        vehicle.finished = True
        vehicle.state = "finished"