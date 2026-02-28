import cv2
import numpy as np
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

def find_floorplan_path(image_path, start_point, end_point):
    # 1. Get the weighted grid
    grid_matrix, img = preprocess_with_doors(image_path)

    # 2. Initialize Grid with weights
    grid = Grid(matrix=grid_matrix)

    start = grid.node(start_point[0], start_point[1])
    end = grid.node(end_point[0], end_point[1])

    # 3. RUN A* (The finder now respects the weights in the matrix)
    finder = AStarFinder()
    path, runs = finder.find_path(start, end, grid)

    if path:
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        # Draw path
        for point in path:
            img[point.y, point.x] = [0, 0, 255]
        
        cv2.circle(img, start_point, 5, (0, 255, 0), -1)
        cv2.circle(img, end_point, 5, (255, 0, 0), -1)
        
        cv2.imshow("Centered Path", img)
        cv2.waitKey(0)
    else:
        print("No path found.")

def preprocess_with_doors(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY_INV)

    # STEP 1: CLOSE DOUBLE WALLS
    gap_closer_kernel = np.ones((3, 3), np.uint8)
    closed_walls = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, gap_closer_kernel)

    # STEP 2: REMOVE DOORS
    door_removal_kernel = np.ones((3, 3), np.uint8)
    walls_only = cv2.erode(closed_walls, door_removal_kernel, iterations=1)
    walls_only = cv2.dilate(walls_only, door_removal_kernel, iterations=1)

    # STEP 3: REMOVE TEXT/NUMBERS
    contours, _ = cv2.findContours(walls_only, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) < 600:
            cv2.drawContours(walls_only, [cnt], -1, 0, -1)

    # --- STEP 4: DISTANCE TRANSFORM FOR CENTERING ---
    # First, get the walkable area (invert walls_only)
    walkable_mask = cv2.bitwise_not(walls_only)
    
    # Calculate distance from every white pixel to the nearest black wall
    dist = cv2.distanceTransform(walkable_mask, cv2.DIST_L2, 5)
    
    # Normalize distance for weighting (0 to 100 range)
    # The center of the hall will have the HIGHEST distance value.
    max_dist = np.max(dist) if np.max(dist) > 0 else 1
    
    # Create a Weight Map:
    # We want center pixels to be 1 (cheap) and pixels near walls to be high (expensive).
    # Weight = (Max_Distance - Current_Distance) + 1
    # We use a power of 2 to make the "repulsion" from walls even stronger.
    weights = (max_dist - dist)
    weights = np.where(walls_only > 0, 0, weights) # 0 is still a wall (blocked)
    
    # Final cleanup: Ensure walkable areas are at least 1 (A* needs > 0)
    # We scale the weights so the library handles them as integers effectively.
    final_grid = np.where(weights > 0, weights + 1, 0).astype(int)

    return final_grid, img

if __name__ == "__main__":
    find_floorplan_path('thing.png', (100, 50), (415, 660))
