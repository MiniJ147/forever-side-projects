"""
manual_label.py is a prototype for labeling the start conditions for the bot.
"""
import cv2
import numpy as np
import json
import math

# Visual styling colors (BGR)
COLOR_IN = (0, 255, 120)     # Vibrant Green for IN (Origin)
COLOR_OUT = (50, 50, 255)    # Bright Red for OUT (Destination)
COLOR_DEMAND = (255, 220, 0) # Cyan-Yellow for demand vectors

class LevelAnnotator:
    def __init__(self, image_path, output_json="level_config.json"):
        self.image_path = image_path
        self.output_json = output_json
        
        self.orig_img = cv2.imread(image_path)
        if self.orig_img is None:
            raise FileNotFoundError(f"Could not load image at {image_path}")
            
        self.nodes = []      # List of node dicts
        self.demands = []    # List of {"from": id_A, "to": id_B}
        
        # Application Modes: "NODE" or "DEMAND"
        self.mode = "NODE"
        
        # Node Mode State: 0 = center click, 1 = orientation click
        self.click_state = 0
        self.temp_center = None
        self.default_node_type = "IN"
        
        # Demand Mode State
        self.selected_source_id = None
        
        self.curr_mouse_pos = (0, 0)
        self.show_controls = False

    def get_node_at_pos(self, x, y, max_dist=30):
        """Finds the closest node within hit distance of pixel (x, y)."""
        best_id = None
        min_d = float('inf')
        for node in self.nodes:
            cx, cy = node["center"]
            dist = math.sqrt((cx - x)**2 + (cy - y)**2)
            if dist < min_d and dist <= max_dist:
                min_d = dist
                best_id = node["id"]
        return best_id

    def mouse_callback(self, event, x, y, flags, param):
        if self.show_controls:
            return

        self.curr_mouse_pos = (x, y)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.mode == "NODE":
                if self.click_state == 0:
                    self.temp_center = (x, y)
                    self.click_state = 1
                elif self.click_state == 1:
                    dx = x - self.temp_center[0]
                    dy = y - self.temp_center[1]
                    angle_deg = round(math.degrees(math.atan2(dy, dx)), 1)
                    
                    next_id = len(self.nodes)
                    self.nodes.append({
                        "id": next_id,
                        "type": self.default_node_type,
                        "center": self.temp_center,
                        "orientation_deg": angle_deg
                    })
                    
                    self.click_state = 0
                    self.temp_center = None

            elif self.mode == "DEMAND":
                clicked_id = self.get_node_at_pos(x, y)
                if clicked_id is not None:
                    if self.selected_source_id is None:
                        # Step 1: Select Source (IN) Node
                        self.selected_source_id = clicked_id
                    else:
                        # Step 2: Select Target (OUT) Node and record demand link
                        if clicked_id != self.selected_source_id:
                            new_link = {"from": self.selected_source_id, "to": clicked_id}
                            if new_link not in self.demands:
                                self.demands.append(new_link)
                        self.selected_source_id = None  # Reset selection

    def render_controls_modal(self, canvas):
        """Draws an enlarged, semi-transparent help menu overlay."""
        h, w = canvas.shape[:2]
        box_w, box_h = 680, 480
        box_x = max(0, (w - box_w) // 2)
        box_y = max(0, (h - box_h) // 2)
        
        overlay = canvas.copy()
        cv2.rectangle(overlay, (box_x, box_y), (box_x + box_w, box_y + box_h), (15, 15, 15), -1)
        cv2.rectangle(overlay, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 255, 255), 3)
        cv2.addWeighted(overlay, 0.88, canvas, 0.12, 0, canvas)
        
        entries = [
            ("CONTROLS & LEVEL BUILDER GUIDE", (0, 255, 255), 0.85, 2),
            ("------------------------------------------------------------", (150, 150, 150), 0.5, 1),
            ("m             : Switch Mode (NODE Placement <-> DEMAND Linking)", (255, 255, 255), 0.55, 2),
            ("t             : Toggle Default Node Type (IN vs OUT) in Node Mode", (255, 255, 255), 0.55, 2),
            ("--- NODE MODE ---", (0, 255, 0), 0.55, 2),
            ("Left Click #1 : Place Node Center", (220, 220, 220), 0.50, 1),
            ("Left Click #2 : Set Orientation Arrow", (220, 220, 220), 0.50, 1),
            ("--- DEMAND MODE ---", (0, 200, 255), 0.55, 2),
            ("Left Click #1 : Click Source (IN) Node", (220, 220, 220), 0.50, 1),
            ("Left Click #2 : Click Target (OUT) Node to create route link", (220, 220, 220), 0.50, 1),
            ("--- GENERAL ---", (150, 150, 150), 0.5, 1),
            ("u             : Undo last node or demand link", (255, 255, 255), 0.55, 2),
            ("s             : Save level_config.json (Nodes + Demands)", (255, 255, 255), 0.55, 2),
            ("c             : Toggle this help menu | q / Esc: Quit", (255, 255, 255), 0.55, 2)
        ]
        
        start_y = box_y + 35
        for text, color, scale, thickness in entries:
            cv2.putText(canvas, text, (box_x + 25, start_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)
            start_y += 30

    def draw_overlay(self):
        canvas = self.orig_img.copy()
        
        # 1. Draw Demand Connection Lines
        for demand in self.demands:
            src_node = next((n for n in self.nodes if n["id"] == demand["from"]), None)
            dst_node = next((n for n in self.nodes if n["id"] == demand["to"]), None)
            if src_node and dst_node:
                p1 = tuple(src_node["center"])
                p2 = tuple(dst_node["center"])
                cv2.arrowedLine(canvas, p1, p2, COLOR_DEMAND, 2, tipLength=0.08, line_type=cv2.LINE_AA)

        # 2. Draw Nodes
        for node in self.nodes:
            node_id = node["id"]
            node_type = node.get("type", "IN")
            cx, cy = node["center"]
            
            color_bgr = COLOR_IN if node_type == "IN" else COLOR_OUT
            
            # Highlight selected source node in Demand Mode
            if self.mode == "DEMAND" and self.selected_source_id == node_id:
                cv2.circle(canvas, (cx, cy), 18, (0, 255, 255), 3)

            # Node center dots
            cv2.circle(canvas, (cx, cy), 8, color_bgr, -1)
            cv2.circle(canvas, (cx, cy), 11, (255, 255, 255), 2)
            
            # Orientation arrow
            rad = math.radians(node["orientation_deg"])
            arrow_len = 40
            end_x = int(cx + arrow_len * math.cos(rad))
            end_y = int(cy + arrow_len * math.sin(rad))
            cv2.arrowedLine(canvas, (cx, cy), (end_x, end_y), color_bgr, 3, tipLength=0.35)
            
            # Text label: ID + Type
            label = f"#{node_id} [{node_type}]"
            label_pos = (cx + 15, cy - 12)
            cv2.putText(canvas, label, label_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(canvas, label, label_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color_bgr, 2, cv2.LINE_AA)

        # 3. Preview line for current node creation
        if self.mode == "NODE" and self.click_state == 1 and self.temp_center and not self.show_controls:
            color_bgr = COLOR_IN if self.default_node_type == "IN" else COLOR_OUT
            cx, cy = self.temp_center
            mx, my = self.curr_mouse_pos
            cv2.circle(canvas, (cx, cy), 8, color_bgr, -1)
            cv2.line(canvas, (cx, cy), (mx, my), color_bgr, 3)

        # 4. Preview demand line when dragging/selecting in Demand Mode
        if self.mode == "DEMAND" and self.selected_source_id is not None and not self.show_controls:
            src_node = next((n for n in self.nodes if n["id"] == self.selected_source_id), None)
            if src_node:
                cv2.line(canvas, tuple(src_node["center"]), self.curr_mouse_pos, COLOR_DEMAND, 2, cv2.LINE_AA)

        # 5. Header status bar
        mode_str = f"MODE: {self.mode} | Default Type: {self.default_node_type}" if self.mode == "NODE" else "MODE: DEMAND LINKING"
        status = f"{mode_str} | Nodes: {len(self.nodes)} | Demands: {len(self.demands)}"
        cv2.putText(canvas, status, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 255), 2, cv2.LINE_AA)
        
        instructions = "Keys: 'm' Mode | 't' Toggle IN/OUT | 'u' Undo | 's' Save | 'c' Help | 'q' Quit"
        cv2.putText(canvas, instructions, (15, canvas.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 2, cv2.LINE_AA)
        
        if self.show_controls:
            self.render_controls_modal(canvas)
            
        return canvas

    def run(self):
        window_name = "Freeways Level Annotator & Demand Builder"
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse_callback)

        while True:
            canvas = self.draw_overlay()
            cv2.imshow(window_name, canvas)
            
            key = cv2.waitKey(20) & 0xFF
            
            if key == ord('q'):
                break
            elif key == 27:  # Esc
                if self.show_controls:
                    self.show_controls = False
                else:
                    break
            elif key == ord('c'):
                self.show_controls = not self.show_controls
            elif not self.show_controls:
                if key == ord('m'):  # Toggle Mode
                    self.mode = "DEMAND" if self.mode == "NODE" else "NODE"
                    self.click_state = 0
                    self.selected_source_id = None
                elif key == ord('t'):  # Toggle Default Type
                    self.default_node_type = "OUT" if self.default_node_type == "IN" else "IN"
                elif key == ord('u'):  # Undo
                    if self.mode == "NODE":
                        if self.click_state == 1:
                            self.click_state = 0
                            self.temp_center = None
                        elif self.nodes:
                            deleted_node = self.nodes.pop()
                            # Remove associated demands
                            self.demands = [d for d in self.demands if d["from"] != deleted_node["id"] and d["to"] != deleted_node["id"]]
                    elif self.mode == "DEMAND":
                        if self.selected_source_id is not None:
                            self.selected_source_id = None
                        elif self.demands:
                            self.demands.pop()
                elif key == ord('s'):  # Save full level config
                    out_data = {
                        "nodes": self.nodes,
                        "demands": self.demands
                    }
                    with open(self.output_json, 'w') as f:
                        json.dump(out_data, f, indent=2)
                    print(f"Saved {len(self.nodes)} nodes & {len(self.demands)} demands to '{self.output_json}'")

        cv2.destroyAllWindows()

if __name__ == "__main__":
    annotator = LevelAnnotator("level_start.png")
    annotator.run()