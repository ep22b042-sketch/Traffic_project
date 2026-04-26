import random


class Source:
    def __init__(self, source_id, junction_id, destination_ids, rate=0.3, mode="poisson"):
        self.source_id = source_id
        self.junction_id = junction_id
        self.destination_ids = destination_ids
        self.rate = rate
        self.mode = mode
        self._accumulator = 0.0

    def maybe_generate(self, dt):
        generated = 0

        if self.mode == "constant":
            self._accumulator += self.rate * dt
            while self._accumulator >= 1.0:
                generated += 1
                self._accumulator -= 1.0
        elif self.mode == "poisson":
            if random.random() < self.rate * dt:
                generated = 1

        return generated

    def choose_destination(self):
        return random.choice(self.destination_ids)