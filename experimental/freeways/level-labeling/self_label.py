"""
self_label.py: use computer vision to automatically label (a lot more complicated)
"""
import cv2
import numpy as np
import json

def estimate_arrow_direction(roi):
    """
    Estimates arrow heading by finding the center of mass offset
    of the white arrow pixels relative to the ROI center.
    """
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # Threshold for bright pixels (white arrows on node blocks)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    M = cv2.moments(thresh)
    if M["m00"] == 0:
        return 0.0  # Default angle if no arrow features are detected
    
    # Centroid of white pixels in ROI
    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]
    
    roi_cx, roi_cy = roi.shape[1] / 2.0, roi.shape[0] / 2.0
    dx = cx - roi_cx
    dy = cy - roi_cy
    
    # Compute angle in degrees (-180 to 180)
    angle_deg = np.degrees(np.arctan2(dy, dx))
    return round(float(angle_deg), 1)

def parse_freeways_level(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at path: {image_path}")
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Standard HSV color bounds for Freeways terminal nodes
    color_ranges = {
        "red": [((0, 120, 120), (10, 255, 255)), ((170, 120, 120), (180, 255, 255))],
        "green": [((35, 100, 100), (85, 255, 255))],
        "blue": [((100, 120, 120), (130, 255, 255))],
        "yellow": [((20, 120, 120), (35, 255, 255))],
        "orange": [((10, 120, 120), (25, 255, 255))],
        "purple": [((130, 100, 100), (160, 255, 255))]
    }
    
    nodes = []
    node_id = 0
    
    for color_name, ranges in color_ranges.items():
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in ranges:
            lower_bound = np.array(lower, dtype=np.uint8)
            upper_bound = np.array(upper, dtype=np.uint8)
            mask |= cv2.inRange(hsv, lower_bound, upper_bound)
            
        # Clean noise via morphological open/close
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Extract terminal contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Filter tiny noise artifacts and huge background shapes
            if 200 < area < 12000:
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = x + w // 2, y + h // 2
                
                # Estimate direction using white arrow intensity shift inside ROI
                roi = img[y:y+h, x:x+w]
                orientation = estimate_arrow_direction(roi)
                
                nodes.append({
                    "id": node_id,
                    "color": color_name,
                    "center": (int(cx), int(cy)),
                    "bbox": (int(x), int(y), int(w), int(h)),
                    "orientation_deg": orientation
                })
                node_id += 1
                
    return nodes

def visualize_parsed_nodes(image_path, nodes, output_path="parsed_level_debug.png"):
    """Draws detected bounding boxes, center points, and heading vectors onto the map."""
    img = cv2.imread(image_path)
    
    for node in nodes:
        cx, cy = node["center"]
        x, y, w, h = node["bbox"]
        
        # Bounding box & center dot
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), -1)
        
        # Orientation vector arrow
        rad = np.radians(node["orientation_deg"])
        arrow_len = 35
        end_x = int(cx + arrow_len * np.cos(rad))
        end_y = int(cy + arrow_len * np.sin(rad))
        cv2.arrowedLine(img, (cx, cy), (end_x, end_y), (255, 255, 0), 2, tipLength=0.3)
        
        # ID and Color text label
        label = f"#{node['id']} {node['color']}"
        cv2.putText(img, label, (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        
    cv2.imwrite(output_path, img)
    print(f"Debug visual saved to {output_path}")

if __name__ == "__main__":
    screenshot_path = "level_start.png"
    
    try:
        parsed_nodes = parse_freeways_level(screenshot_path)
        print("Parsed Level Data:")
        print(json.dumps(parsed_nodes, indent=2))
        
        # Render verification overlay
        visualize_parsed_nodes(screenshot_path, parsed_nodes)
    except FileNotFoundError as e:
        print(e)