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
    def __init__(self, name, odor, wetness, affinity, sizes=None):
        self.name = name
        self.odor = odor
        self.wetness = wetness
        self.affinity = affinity  # long-term vs short-term
        # sizes: list of (w,h) options for the stall footprint in grid cells
        # if None, default to single-cell
        self.sizes = sizes or [(1, 1)]

FRESH = StallType("Fresh", odor=3, wetness=3, affinity="long", sizes=[(2,2),(2,3),(3,2)])
PRODUCE = StallType("Produce", odor=1, wetness=1, affinity="both", sizes=[(1,1),(1,2),(2,1)])
COOKED = StallType("Cooked", odor=3, wetness=1, affinity="short", sizes=[(1,1),(1,2)])
GENERAL = StallType("General", odor=0, wetness=0, affinity="both", sizes=[(1,1),(2,1)])

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
import matplotlib
# use non-interactive backend to avoid GUI backend crashes (headless or incompatible setups)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
import datetime
import uuid

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

    # choose size option for this stall type
    w, h = random.choice(STALL_TYPES[best_idx].sizes)

    # check bounds and occupancy for footprint (x..x+w-1, y..y+h-1)
    if x + w > grid.width or y + h > grid.height:
        return
    region = grid.cells[y:y+h, x:x+w]
    if np.any(region != CellType.EMPTY):
        return

    # place the stall: mark all cells in footprint
    grid.cells[y:y+h, x:x+w] = CellType.STALL
    grid.stall_map[y:y+h, x:x+w] = best_idx

def fitness_score(x, y, stall, efficiency, exploration):
    score = 0.0
    if stall.affinity == "long":
        score += efficiency[y, x]
    elif stall.affinity == "short":
        score += exploration[y, x]
    return score

if __name__ == "__main__":
    print("Script started")
    grid = Grid(40, 25)

    eff = efficiency_field(grid)
    exp = exploration_field(grid)

    # --- Define primary/secondary paths and utilities (drains/electric) ---
    primary_paths = []
    secondary_paths = []
    # primary: central horizontal aisle and outer border
    center_row = grid.height // 2
    for x in range(grid.width):
        primary_paths.append((x, center_row))
        primary_paths.append((x, 0))
        primary_paths.append((x, grid.height - 1))
    # secondary: vertical aisles every 6 columns
    for x in range(3, grid.width, 6):
        for y in range(grid.height):
            secondary_paths.append((x, y))

    # utilities
    drain_points = [(10, 0), (30, 0)]
    electric_points = [(0, center_row), (grid.width - 1, center_row)]

    # mark aisles on grid
    for (x, y) in primary_paths + secondary_paths:
        if grid.in_bounds(x, y):
            grid.cells[y, x] = CellType.AISLE

    # ensure utilities are not overwritten
    for (x, y) in drain_points + electric_points:
        if grid.in_bounds(x, y):
            grid.cells[y, x] = CellType.AISLE

    # Run CA steps until target density reached or max attempts exceeded
    total_cells = grid.width * grid.height
    target_density = 0.35  # desired fraction of cells to fill with stalls (adjustable)
    target_cells = int(total_cells * target_density)
    placed_cells = 0
    attempts = 0
    max_attempts = 5000
    while placed_cells < target_cells and attempts < max_attempts:
        before = int((grid.cells == CellType.STALL).sum())
        ca_step(grid, eff, exp)
        after = int((grid.cells == CellType.STALL).sum())
        placed_cells += max(0, after - before)
        attempts += 1

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
    # Skip COMPAS imports to avoid native GUI/library crashes in this environment.
    Viewer = None
    Mesh = None

    # diagnostic: report whether a COMPAS Viewer is available
    try:
        print("Viewer available:", Viewer is not None)
    except NameError:
        print("Viewer available: False (Viewer not defined)")

    # Allow forcing viewer off in environments where it causes crashes
    if os.environ.get('USE_COMPAS_VIEWER', '0') != '1':
        Viewer = None
        print('COMPAS viewer disabled (set USE_COMPAS_VIEWER=1 to enable)')

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
        if Mesh is None:
            # return a lightweight representation when Mesh class not available
            return {'verts': verts, 'faces': faces}
        else:
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
        # add path visuals (flat boxes) for primary and secondary
        def add_path_cells(cells, col):
            for (px, py) in cells:
                if not grid.in_bounds(px, py):
                    continue
                pmesh = box_mesh_at(px, py, 0, height=0.02)
                try:
                    viewer.scene.add(pmesh, color=col)
                except Exception:
                    try:
                        d = pmesh.to_data(); d['color'] = col; viewer.scene.add(d)
                    except Exception:
                        pass

        add_path_cells(primary_paths, (0.05, 0.05, 0.05))
        add_path_cells(secondary_paths, (0.5, 0.5, 0.5))

        # add utility markers
        def add_util_point(pt, col):
            px, py = pt
            if not grid.in_bounds(px, py):
                return
            umesh = box_mesh_at(px, py, 0, height=0.3)
            try:
                viewer.scene.add(umesh, color=col)
            except Exception:
                try:
                    d = umesh.to_data(); d['color'] = col; viewer.scene.add(d)
                except Exception:
                    pass

        for dp in drain_points:
            add_util_point(dp, (0.2, 0.4, 0.9))
        for ep in electric_points:
            add_util_point(ep, (1.0, 1.0, 0.0))
        print("Opening COMPAS viewer window...")
        try:
            viewer.show()
        except Exception as e:
            print("Viewer failed to open:", e)
    else:
        # fallback: continue to matplotlib visualizations below
        pass

    # --- Always also save matplotlib 2D heatmap and 3D bar plot for quick viewing ---
    print("Saving matplotlib images...")
    try:
        os.makedirs('outputs', exist_ok=True)
        # unique timestamp + short uuid to avoid overwriting previous runs
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:6]
        saved_files = []
        stall_grid = np.full((grid.height, grid.width), -1, dtype=int)
        for y in range(grid.height):
            for x in range(grid.width):
                stall_grid[y, x] = grid.stall_map[y, x]

        # 2D RGB visualization by stall category saved via Pillow (avoids matplotlib GUI issues)
        try:
            from PIL import Image
            height, width = stall_grid.shape
            rgb = np.ones((height, width, 3), dtype=float)  # default white for empty
            for y in range(height):
                for x in range(width):
                    idx = stall_grid[y, x]
                    if idx >= 0:
                        stname = STALL_TYPES[idx].name
                        rgb[y, x, :] = color_map.get(stname, (0.5, 0.5, 0.5))

            img_arr = (np.clip(rgb, 0.0, 1.0) * 255).astype('uint8')
            fname_debug = f'outputs/stall_map_debug_{ts}.png'
            Image.fromarray(img_arr, 'RGB').save(fname_debug)
            saved_files.append(fname_debug)

            # overlay primary/secondary/utilities by drawing on a copy
            overlay = img_arr.copy()
            # primary paths: black pixels
            for (px, py) in primary_paths:
                if 0 <= py < height and 0 <= px < width:
                    overlay[py, px] = (0, 0, 0)
            # secondary paths: gray
            for (sx, sy) in secondary_paths:
                if 0 <= sy < height and 0 <= sx < width:
                    overlay[sy, sx] = (128, 128, 128)
            # drains: blue
            for (dx, dy) in drain_points:
                if 0 <= dy < height and 0 <= dx < width:
                    overlay[dy, dx] = (0, 0, 255)
            # electric: yellow
            for (ex, ey) in electric_points:
                if 0 <= ey < height and 0 <= ex < width:
                    overlay[ey, ex] = (255, 255, 0)

            fname_paths = f'outputs/stall_map_with_paths_{ts}.png'
            Image.fromarray(overlay, 'RGB').save(fname_paths)
            saved_files.append(fname_paths)

            # save raw stall grid as CSV for quick inspection
            csv_path = f'outputs/stall_grid_{ts}.csv'
            np.savetxt(csv_path, stall_grid, fmt='%d', delimiter=',')
            saved_files.append(csv_path)
        except Exception as e:
            # Pillow not available or saving failed; fall back to writing CSV only
            try:
                csv_path = f'outputs/stall_grid_{ts}.csv'
                np.savetxt(csv_path, stall_grid, fmt='%d', delimiter=',')
                saved_files.append(csv_path)
                print('Pillow not available; saved stall grid CSV only.')
            except Exception as e2:
                print('Failed to save visualizations via Pillow or CSV:', e, e2)

        # write run summary (counts + saved filenames)
        summary_path = f'outputs/run_summary_{ts}.txt'
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f'Script timestamp: {ts}\n')
                f.write(f'Total cells: {total_cells}, Stalls placed: {stall_count}, Empty: {empty_count}\n')
                f.write('Stall type counts:\n')
                for k, v in counts.items():
                    f.write(f'  {k}: {v}\n')
                f.write('\nSaved files:\n')
                for p in saved_files:
                    f.write(f'  {p}\n')
            print(f'Saved images and summary to outputs/ (summary: {summary_path})')
        except Exception as e:
            print('Failed to write run summary:', e)
    except Exception as e:
        print('Failed to save matplotlib visualizations:', e)

