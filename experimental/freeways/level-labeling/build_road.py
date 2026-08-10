import math
import json
import time
import numpy as np

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False


class FreewaysSolver:
    def __init__(self, config_path="level_config.json", bridge_buffer_px=35.0):
        self.config_path = config_path
        self.bridge_buffer_px = bridge_buffer_px
        self.nodes = {}
        self.demands = []
        self.allow_elevated = True
        self.existing_roads = []  # Stores drawn paths as numpy arrays [N, 2]

        self.load_config(config_path)

    def load_config(self, config_path):
        """Loads and normalizes nodes, demands, and constraints from level JSON."""
        with open(config_path, "r") as f:
            data = json.load(f)

        if isinstance(data, dict):
            raw_nodes = data.get("nodes", [])
            self.demands = [(d["from"], d["to"]) for d in data.get("demands", [])]
            self.allow_elevated = data.get("allow_elevated", True)
        else:
            raw_nodes = data
            self.demands = []
            self.allow_elevated = True

        self.nodes = {}
        if isinstance(raw_nodes, dict):
            for k, node in raw_nodes.items():
                node_id = node.get("id", int(k) if str(k).isdigit() else k)
                node["id"] = node_id
                self.nodes[node_id] = node
        elif isinstance(raw_nodes, list):
            for idx, node in enumerate(raw_nodes):
                if isinstance(node, dict):
                    node_id = node.get("id", idx)
                    node["id"] = node_id
                    self.nodes[node_id] = node

    def get_dir_vector(self, node):
        """Converts node orientation angle (degrees) into a normalized 2D vector."""
        rad = math.radians(node.get("orientation_deg", 0.0))
        return np.array([math.cos(rad), math.sin(rad)])

    def generate_bezier_path(self, p0, v0, p3, v3, step_size_px=8.0):
        """
        Generates adaptive Bézier waypoints where sample density is scaled
        by Euclidean distance to ensure high-resolution intersection checks.
        """
        dist = np.linalg.norm(p3 - p0)
        tangent_scale = max(dist * 0.45, 30.0)

        p1 = p0 + v0 * tangent_scale
        p2 = p3 - v3 * tangent_scale

        est_length = dist * 1.3
        num_samples = max(int(est_length / step_size_px), 30)

        t = np.linspace(0.0, 1.0, num_samples)[:, np.newaxis]
        path = (
            ((1 - t) ** 3) * p0
            + 3 * ((1 - t) ** 2) * t * p1
            + 3 * (1 - t) * (t**2) * p2
            + (t**3) * p3
        )
        return path

    def detect_intersections(self, candidate_path):
        """Detects line-segment crossings against existing drawn roads."""
        intersections = []
        if len(self.existing_roads) == 0:
            return intersections

        for road_idx, existing_path in enumerate(self.existing_roads):
            for i in range(len(candidate_path) - 1):
                a1, a2 = candidate_path[i], candidate_path[i + 1]
                for j in range(len(existing_path) - 1):
                    b1, b2 = existing_path[j], existing_path[j + 1]

                    if self._line_segments_intersect(a1, a2, b1, b2):
                        pt = self._compute_intersection_point(a1, a2, b1, b2)
                        intersections.append({
                            "road_index": road_idx,
                            "intersection_point": pt.tolist() if pt is not None else a1.tolist(),
                            "segment_step": i
                        })
        return intersections

    @staticmethod
    def _ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    def _line_segments_intersect(self, a, b, c, d):
        """2D cross-product segment orientation check."""
        return (self._ccw(a, c, d) != self._ccw(b, c, d)) and (
            self._ccw(a, b, c) != self._ccw(a, b, d)
        )

    def _compute_intersection_point(self, p1, p2, p3, p4):
        """Calculates exact 2D coordinates where segments (p1-p2) and (p3-p4) cross."""
        x1, y1 = p1; x2, y2 = p2
        x3, y3 = p3; x4, y4 = p4
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-6:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        return np.array([x1 + t * (x2 - x1), y1 + t * (y2 - y1)])

    def build_combined_network(self, radius_px=110.0, ring_samples=36):
        """
        Generates a continuous spatial roundabout interchange for multi-node 
        levels to prevent gridlock, or direct routes for single pairs.
        """
        in_nodes = [n for n in self.nodes.values() if n.get("type") == "IN"]
        out_nodes = [n for n in self.nodes.values() if n.get("type") == "OUT"]

        # Single pair fallback
        if len(in_nodes) <= 1 and len(out_nodes) <= 1:
            return self._build_direct_routes()

        # 1. Compute Centroid for Roundabout Center
        all_coords = [n["center"] for n in in_nodes + out_nodes]
        cx, cy = np.mean(all_coords, axis=0)

        network_segments = []

        # 2. Draw Main Circular Ring Segment (Clockwise Loop)
        angles = np.linspace(0, 2 * math.pi, ring_samples)
        ring_pts = [
            [int(cx + radius_px * math.cos(a)), int(cy + radius_px * math.sin(a))]
            for a in angles
        ]
        
        ring_np = np.array(ring_pts)
        ring_crossings = self.detect_intersections(ring_np)
        
        network_segments.append({
            "label": "ROUNDABOUT_RING",
            "waypoints": ring_pts,
            "bridge_crossings": ring_crossings,
            "is_valid": self.allow_elevated or len(ring_crossings) == 0
        })
        self.existing_roads.append(ring_np)

        # 3. Tangentially Connect IN Nodes to the Ring
        for node in in_nodes:
            p0 = np.array(node["center"], dtype=float)
            v0 = self.get_dir_vector(node)

            entry_angle = math.atan2(p0[1] - cy, p0[0] - cx)
            merge_angle = entry_angle - math.radians(25)
            p3 = np.array([cx + radius_px * math.cos(merge_angle), 
                           cy + radius_px * math.sin(merge_angle)])

            # Tangent direction along clockwise circle
            v3 = np.array([-math.sin(merge_angle), math.cos(merge_angle)])

            path = self.generate_bezier_path(p0, v0, p3, v3)
            crossings = self.detect_intersections(path)

            network_segments.append({
                "label": f"IN_{node['id']} -> RING",
                "waypoints": [[int(pt[0]), int(pt[1])] for pt in path],
                "bridge_crossings": crossings,
                "is_valid": self.allow_elevated or len(crossings) == 0
            })
            self.existing_roads.append(path)

        # 4. Tangentially Branch OUT Nodes from the Ring
        for node in out_nodes:
            p3 = np.array(node["center"], dtype=float)
            v3 = self.get_dir_vector(node)

            exit_angle = math.atan2(p3[1] - cy, p3[0] - cx)
            detach_angle = exit_angle - math.radians(25)
            p0 = np.array([cx + radius_px * math.cos(detach_angle), 
                           cy + radius_px * math.sin(detach_angle)])

            v0 = np.array([-math.sin(detach_angle), math.cos(detach_angle)])

            path = self.generate_bezier_path(p0, v0, p3, v3)
            crossings = self.detect_intersections(path)

            network_segments.append({
                "label": f"RING -> OUT_{node['id']}",
                "waypoints": [[int(pt[0]), int(pt[1])] for pt in path],
                "bridge_crossings": crossings,
                "is_valid": self.allow_elevated or len(crossings) == 0
            })
            self.existing_roads.append(path)

        return network_segments

    def _build_direct_routes(self):
        """Direct single-pair Bézier route generator."""
        network_segments = []
        for demand in self.demands:
            src_id, dst_id = demand[0], demand[1]
            if src_id not in self.nodes or dst_id not in self.nodes:
                continue

            src_node = self.nodes[src_id]
            dst_node = self.nodes[dst_id]

            p0 = np.array(src_node["center"], dtype=float)
            v0 = self.get_dir_vector(src_node)
            p3 = np.array(dst_node["center"], dtype=float)
            v3 = self.get_dir_vector(dst_node)

            path = self.generate_bezier_path(p0, v0, p3, v3)
            crossings = self.detect_intersections(path)

            network_segments.append({
                "label": f"DIRECT_{src_id}->{dst_id}",
                "waypoints": [[int(pt[0]), int(pt[1])] for pt in path],
                "bridge_crossings": crossings,
                "is_valid": self.allow_elevated or len(crossings) == 0
            })
            self.existing_roads.append(path)

        return network_segments

    def execute_live(self, execution_plan, countdown=3, scale_factor=2.0):
        """Performs mouse drag actions with coordinate downscaling for HiDPI/Retina displays."""
        if not HAS_PYAUTOGUI:
            print("\n[Notice] 'pyautogui' module not found. Running in DRY-RUN mode.")
            return

        executable_routes = [r for r in execution_plan if r.get("is_valid", True)]

        if len(executable_routes) < len(execution_plan):
            print(f"\n[WARNING] Skipped {len(execution_plan) - len(executable_routes)} segment(s) due to disallowed elevation constraints.")

        if not executable_routes:
            print("[ABORT] No valid executable routes found.")
            return

        print(f"\n[INFO] Executing network drawing in {countdown} seconds. Focus game window...")
        for i in range(countdown, 0, -1):
            print(f"  {i}...")
            time.sleep(1)

        for route in executable_routes:
            waypoints = route["waypoints"]
            if not waypoints:
                continue

            scaled_pts = [(int(x / scale_factor), int(y / scale_factor)) for x, y in waypoints]

            pyautogui.moveTo(scaled_pts[0][0], scaled_pts[0][1])
            pyautogui.mouseDown(button="left")

            for x, y in scaled_pts[1:]:
                pyautogui.moveTo(x, y)

            pyautogui.mouseUp(button="left")
            time.sleep(0.2)


if __name__ == "__main__":
    config_file = "level_config.json"
    solver = FreewaysSolver(config_file)

    print(
        f"Loaded {len(solver.nodes)} nodes and {len(solver.demands)} demands. "
        f"Elevated surfaces allowed: {solver.allow_elevated}"
    )

    plan = solver.build_combined_network()

    print(f"\n--- COMBINED ROAD NETWORK PLAN ({len(plan)} segments) ---")
    print(json.dumps(plan, indent=2))

    solver.execute_live(plan, scale_factor=2.0)