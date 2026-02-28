import cv2
import numpy as np
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

def find_floorplan_path(image_path, start_point, end_point, wall_padding=10):
    # 1. LOAD AND PRE-PROCESS
    # img = cv2.imread(image_path)
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # # Binary threshold: Walls become 0 (black), Floor becomes 255 (white)
    # # Using OTSU to automatically find the best contrast level
    # _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # # 2. ADD SAFETY MARGIN (Padding)
    # # We "dilate" the black walls so the path doesn't scrape against them.
    # # In OpenCV, cv2.erode on a white background shrinks the walkable area.
    # kernel = np.ones((wall_padding, wall_padding), np.uint8)
    # walkable_mask = cv2.erode(binary, kernel, iterations=1)

    # 3. PREPARE FOR PATHFINDING
    # The 'pathfinding' library expects 1 for walkable and 0 for blocked.
    # Currently, our floor is 255, so we divide by 255.
    grid_matrix, img = preprocess_with_doors(image_path)

    # grid_matrix = (walkable_mask / 255).astype(int)
    grid = Grid(matrix=grid_matrix)

    # Define start and end nodes (library uses x, y coordinates)
    start = grid.node(start_point[0], start_point[1])
    end = grid.node(end_point[0], end_point[1])

    # 4. RUN A* ALGORITHM
    finder = AStarFinder()
    path, runs = finder.find_path(start, end, grid)

    # 5. VISUALIZE THE RESULT
    if path:
        print(f"Path found! Length: {len(path)} pixels")

        if len(img.shape) == 2:  # If image is currently grayscale
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        # Draw the path on the original image
        for point in path:
            img[point.y, point.x] = [0, 0, 255] # Draw in Red
        
        # Draw Start and End points as large circles
        cv2.circle(img, start_point, 5, (0, 255, 0), -1) # Green Start
        cv2.circle(img, end_point, 5, (255, 0, 0), -1)   # Blue End
        
        cv2.imshow("Floor Plan Path", img)
        cv2.waitKey(0)
    else:
        print("No path found. Check if start/end points are inside walls.")

# Usage: (x, y) coordinates
# find_floorplan_path('my_floor_plan.png', (50, 50), (400, 350))

def preprocess_with_doors(image_path):
    # Load and invert: Walls/Lines = 255 (White), Floor = 0 (Black)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY_INV)

    # --- STEP 1: CLOSE THE DOUBLE-LINE WALLS ---
    # This kernel should be just wide enough to bridge the gap between lines (e.g., 3-5px)
    gap_closer_kernel = np.ones((3, 3), np.uint8)
    # Closing = Dilate then Erode. It fills small holes (like the gap between lines)
    closed_walls = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, gap_closer_kernel)

    # display closed walls for debugging
    cv2.imshow("Closed Walls", closed_walls)
    cv2.waitKey(0)

    # --- STEP 2: REMOVE THE DOORS ---
    # Now that walls are solid blocks, we can erode. 
    # This kernel must be larger than the thickness of the door curves.
    door_removal_kernel = np.ones((3, 3), np.uint8)
    walls_only = cv2.erode(closed_walls, door_removal_kernel, iterations=1)
    
    # Bring the walls back to a healthy size
    walls_only = cv2.dilate(walls_only, door_removal_kernel, iterations=1)

    # remove small contours that may be numbers or text
    contours, _ = cv2.findContours(walls_only, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) < 600:  # Threshold area to filter out small contours
            cv2.drawContours(walls_only, [cnt], -1, 0, -1)  # Fill small contours with black   

    # display walls only for debugging
    cv2.imshow("Walls Only", walls_only)
    cv2.waitKey(0)

    # --- STEP 3: PADDING ---
    # Create a "no-go" zone so the path doesn't hug the wall
    padding_kernel = np.ones((12, 12), np.uint8)
    buffered_walls = cv2.dilate(walls_only, padding_kernel, iterations=1)

    # Display intermediate results for debugging
    cv2.imshow("Buffered Walls", buffered_walls)
    cv2.waitKey(0)

    # --- STEP 4: PREPARE FOR GRID ---
    # Invert back: Floor = 1 (Walkable), Walls = 0 (Blocked)
    walkable_area = cv2.bitwise_not(buffered_walls)
    grid_matrix = (walkable_area / 255).astype(int)
    
    return grid_matrix, img

if __name__ == "__main__":
    # Example usage
    # find_floorplan_path('thing.png', (100, 50), (190, 350))
    # find_floorplan_path('thing.png', (190, 450), (415, 660))
    find_floorplan_path('thing.png', (415, 660), (190, 450))