import matplotlib.pyplot as plt
import imageio.v2 as imageio
import os


class Visualizer:
    def __init__(self, junctions, roads):
        self.junctions = junctions
        self.roads = roads
        self.frame_paths = []
        self.frame_dir = "frames"
        os.makedirs(self.frame_dir, exist_ok=True)

    def _vehicle_xy_on_road(self, road, vehicle):
        j1 = self.junctions[road.start_junction]
        j2 = self.junctions[road.end_junction]

        frac = min(max(vehicle.position / max(road.length, 1e-9), 0.0), 1.0)
        x = j1.x + frac * (j2.x - j1.x)
        y = j1.y + frac * (j2.y - j1.y)
        return x, y

    def save_frame(self, roads_by_id, step):
        fig, ax = plt.subplots(figsize=(8, 6))

        for road in roads_by_id.values():
            j1 = self.junctions[road.start_junction]
            j2 = self.junctions[road.end_junction]
            ax.annotate(
                "",
                xy=(j2.x, j2.y),
                xytext=(j1.x, j1.y),
                arrowprops=dict(arrowstyle="->", linewidth=1.5)
            )
            mx = (j1.x + j2.x) / 2
            my = (j1.y + j2.y) / 2
            ax.text(mx, my, road.road_id, fontsize=8)

        for jid, junction in self.junctions.items():
            ax.scatter(junction.x, junction.y, s=140, color="black")
            ax.text(junction.x + 0.1, junction.y + 0.1, jid, fontsize=10)

        for road in roads_by_id.values():
            for vehicle in road.vehicles:
                x, y = self._vehicle_xy_on_road(road, vehicle)
                ax.scatter(x, y, s=35, color=vehicle.color)

        ax.set_title(f"Traffic Simulation - Step {step}")
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)

        xs = [j.x for j in self.junctions.values()]
        ys = [j.y for j in self.junctions.values()]
        ax.set_xlim(min(xs) - 2, max(xs) + 2)
        ax.set_ylim(min(ys) - 2, max(ys) + 2)

        path = os.path.join(self.frame_dir, f"frame_{step:04d}.png")
        plt.savefig(path, bbox_inches="tight")
        plt.close(fig)
        self.frame_paths.append(path)

    def make_gif(self, output_path="traffic_simulation.gif", fps=5):
        images = [imageio.imread(path) for path in self.frame_paths]
        imageio.mimsave(output_path, images, fps=fps)
        return output_path