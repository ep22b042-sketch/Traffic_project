import json

from traffic_sim.simulation import Simulation
from traffic_sim.junction import Junction
from traffic_sim.road import Road
from traffic_sim.source import Source
from traffic_sim.sink import Sink


def build_test_network():
    sim = Simulation(dt=1.0, total_steps=80)

    # -----------------------------
    # Junctions with 2D coordinates
    # -----------------------------
    junctions = [
        Junction("A", 0, 0),
        Junction("B", 4, 3),
        Junction("C", 4, -3),
        Junction("D", 9, 3),
        Junction("E", 9, -3),
        Junction("F", 13, 0),
    ]
    for j in junctions:
        sim.add_junction(j)

    # -----------------------------
    # Directed roads
    # -----------------------------
    roads = [
        Road("R1", "A", "B", length=5, speed=1.5, capacity=8),
        Road("R2", "A", "C", length=5, speed=1.5, capacity=8),
        Road("R3", "B", "D", length=5, speed=1.2, capacity=8),
        Road("R4", "C", "E", length=5, speed=1.2, capacity=8),
        Road("R5", "D", "F", length=5, speed=1.5, capacity=8),
        Road("R6", "E", "F", length=5, speed=1.5, capacity=8),
        Road("R7", "B", "C", length=4, speed=1.0, capacity=6),
        Road("R8", "C", "B", length=4, speed=1.0, capacity=6),
        Road("R9", "D", "E", length=4, speed=1.0, capacity=6),
        Road("R10", "E", "D", length=4, speed=1.0, capacity=6),
    ]
    for r in roads:
        sim.add_road(r)

    # -----------------------------
    # Sources and sinks
    # -----------------------------
    sim.add_source(Source("S1", "A", destination_ids=["F", "D", "E"], rate=0.6, mode="poisson"))
    sim.add_source(Source("S2", "B", destination_ids=["F", "E"], rate=0.3, mode="poisson"))
    sim.add_source(Source("S3", "C", destination_ids=["F", "D"], rate=0.3, mode="poisson"))

    sim.add_sink(Sink("K1", "F"))
    sim.add_sink(Sink("K2", "D"))
    sim.add_sink(Sink("K3", "E"))

    return sim


def main():
    sim = build_test_network()
    gif_file, stats = sim.run("traffic_simulation.gif")

    print("Simulation complete.")
    print(f"GIF saved to: {gif_file}")
    print(json.dumps(stats, indent=2))

    with open("stats.json", "w") as f:
        json.dump(stats, f, indent=2)


if __name__ == "__main__":
    main()