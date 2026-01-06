import numpy as np
from enum import Enum

class CellType(Enum):
    EMPTY = 0
    STALL = 1
    AISLE = 2
    EDGE = 3

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = np.full((height, width), CellType.EMPTY)
        self.stall_map = np.full((height, width), -1, dtype=int)  # store stall type index when a stall is placed

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def neighbors(self, x, y):
        dirs = [(-1,-1), (-1,0), (-1,1),
                (0,-1),          (0,1),
                (1,-1),  (1,0),  (1,1)]
        return [(x+dx, y+dy) for dx, dy in dirs
                if self.in_bounds(x+dx, y+dy)]
    
class StallType:
    def __init__(self, name, odor, wetness, affinity):
        self.name = name
        self.odor = odor
        self.wetness = wetness
        self.affinity = affinity  # long-term vs short-term

FRESH = StallType("Fresh", odor=3, wetness=3, affinity="long")
PRODUCE = StallType("Produce", odor=1, wetness=1, affinity="both")
COOKED = StallType("Cooked", odor=3, wetness=1, affinity="short")
GENERAL = StallType("General", odor=0, wetness=0, affinity="both")

def efficiency_field(grid):
    # 越靠近主動線，值越高
    field = np.zeros_like(grid.cells, dtype=float)
    # placeholder
    return field

def exploration_field(grid):
    field = np.zeros_like(grid.cells, dtype=float)
    return field

import random
import os
import matplotlib.pyplot as plt
from matplotlib import cm

# Use the StallType instances defined above
STALL_TYPES = [FRESH, PRODUCE, COOKED, GENERAL]

def ca_step(grid, efficiency, exploration):
    x = random.randint(0, grid.width - 1)
    y = random.randint(0, grid.height - 1)
    if grid.cells[y, x] != CellType.EMPTY:
        return

    # compute fitness scores for each stall type
    scores = [fitness_score(x, y, stall, efficiency, exploration) for stall in STALL_TYPES]
    max_score = max(scores)
    # pick randomly among tied best scores to avoid bias toward first entry
    best_indices = [i for i, s in enumerate(scores) if s == max_score]
    best_idx = random.choice(best_indices)

    # place the stall
    grid.cells[y, x] = CellType.STALL
    grid.stall_map[y, x] = best_idx

def fitness_score(x, y, stall, efficiency, exploration):
    score = 0.0
    if stall.affinity == "long":
        score += efficiency[y, x]
    elif stall.affinity == "short":
        score += exploration[y, x]
    return score

if __name__ == "__main__":
    grid = Grid(40, 25)

    eff = efficiency_field(grid)
    exp = exploration_field(grid)

    # Run a few CA steps for debugging
    for i in range(200):
        ca_step(grid, eff, exp)

    # report counts
    total_cells = grid.width * grid.height
    stall_count = int((grid.cells == CellType.STALL).sum())
    empty_count = int((grid.cells == CellType.EMPTY).sum())
    print(f"Total cells: {total_cells}, Stalls placed: {stall_count}, Empty: {empty_count}")
    # counts per stall type
    counts = {}
    for idx, st in enumerate(STALL_TYPES):
        counts[st.name] = int((grid.stall_map == idx).sum())
    print("Stall type counts:", counts)

    # --- Visualization: try COMPAS viewer, fallback to matplotlib heatmap ---
    try:
        import compas
        from compas.datastructures import Mesh
        try:
            from compas_viewer import Viewer
        except Exception:
            Viewer = None
    except Exception:
        Viewer = None

    def box_mesh_at(x, y, idx, height=0.6):
        # create small prism centered on cell (x,y) with height
        cx = x + 0.5
        cy = y + 0.5
        cz = height / 2.0
        L = W = 1.0
        lx = L / 2.0
        wy = W / 2.0
        hz = height / 2.0
        verts = [
            (cx - lx, cy - wy, cz - hz),
            (cx + lx, cy - wy, cz - hz),
            (cx + lx, cy + wy, cz - hz),
            (cx - lx, cy + wy, cz - hz),
            (cx - lx, cy - wy, cz + hz),
            (cx + lx, cy - wy, cz + hz),
            (cx + lx, cy + wy, cz + hz),
            (cx - lx, cy + wy, cz + hz),
        ]
        faces = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
        ]
        return Mesh.from_vertices_and_faces(verts, faces)

    color_map = {
        'Fresh': (1.0, 0.2, 0.2),
        'Produce': (0.2, 0.8, 0.2),
        'Cooked': (0.9, 0.6, 0.1),
        'General': (0.6, 0.6, 0.6),
    }

    if Viewer is not None:
        viewer = Viewer()
        # add meshes for each placed stall
        h = 0.6
        for y in range(grid.height):
            for x in range(grid.width):
                idx = grid.stall_map[y, x]
                if idx >= 0:
                    mesh = box_mesh_at(x, y, idx, height=h)
                    # attach color attribute and pass color to viewer if supported
                    stname = STALL_TYPES[idx].name
                    color = color_map.get(stname, (0.5, 0.5, 0.5))
                    try:
                        mesh.attributes['color'] = color
                    except Exception:
                        pass
                    try:
                        viewer.scene.add(mesh, color=color)
                    except Exception:
                        try:
                            data = mesh.to_data()
                            data['color'] = color
                            viewer.scene.add(data)
                        except Exception:
                            pass
        print("Opening COMPAS viewer window...")
        try:
            viewer.show()
        except Exception as e:
            print("Viewer failed to open:", e)
    else:
        # fallback: continue to matplotlib visualizations below
        pass

    # --- Always also save matplotlib 2D heatmap and 3D bar plot for quick viewing ---
    try:
        os.makedirs('outputs', exist_ok=True)
        stall_grid = np.full((grid.height, grid.width), -1, dtype=int)
        for y in range(grid.height):
            for x in range(grid.width):
                stall_grid[y, x] = grid.stall_map[y, x]

        # 2D RGB visualization by stall category
        height, width = stall_grid.shape
        rgb = np.ones((height, width, 3), dtype=float)  # default white for empty
        for y in range(height):
            for x in range(width):
                idx = stall_grid[y, x]
                if idx >= 0:
                    stname = STALL_TYPES[idx].name
                    rgb[y, x, :] = color_map.get(stname, (0.5, 0.5, 0.5))

        plt.figure(figsize=(10, 6))
        plt.imshow(rgb, interpolation='nearest', origin='lower')
        plt.title('Stall map (color-coded by category)')
        # legend
        import matplotlib.patches as mpatches
        patches = [mpatches.Patch(color=color_map[s.name], label=s.name) for s in STALL_TYPES]
        patches.insert(0, mpatches.Patch(color=(1,1,1), label='Empty'))
        plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('outputs/stall_map_debug.png', dpi=200)
        plt.close()

        # 3D bar plot
        try:
            from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            dx = dy = 0.8
            for y in range(grid.height):
                for x in range(grid.width):
                    idx = grid.stall_map[y, x]
                    if idx >= 0:
                        z = 0
                        dz = 0.6
                        color = color_map.get(STALL_TYPES[idx].name, (0.5, 0.5, 0.5))
                        ax.bar3d(x - 0.4, y - 0.4, z, dx, dy, dz, color=color, shade=True)
            ax.set_xlim(0, grid.width)
            ax.set_ylim(0, grid.height)
            ax.set_zlim(0, 1)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Height')
            plt.title('3D Stall layout (matplotlib)')
            plt.savefig('outputs/stall_map_3d.png', dpi=200)
            plt.close()
        except Exception as e:
            print('3D plot failed:', e)

        print("Saved images: outputs/stall_map_debug.png, outputs/stall_map_3d.png")
    except Exception as e:
        print('Failed to save matplotlib visualizations:', e)

