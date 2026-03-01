import easyocr
import numpy as np
import hallway2
import hallway3

# Initialize the reader (English language)
# This takes a second to load, so do it once at the top of your script
reader = easyocr.Reader(['en'])

def map_room_numbers(image_path):
    """
    Scans the floorplan and returns a dictionary: {'101': (x, y), '102': (x, y)}
    """
    print("Scanning for room numbers... (this may take a few seconds)")
    results = reader.readtext(image_path)
    
    room_map = {}
    for (bbox, text, prob) in results:
        # EasyOCR returns bbox as [[top_left], [top_right], [bottom_right], [bottom_left]]
        # We calculate the center point of the box
        (tl, tr, br, bl) = bbox
        center_x = int((tl[0] + br[0]) / 2)
        center_y = int((tl[1] + br[1]) / 2)
        
        # Clean the text (remove spaces/extra chars)
        room_id = text.strip()
        room_map[room_id] = (center_x, center_y)
        
    return room_map

# --- INTEGRATION WITH YOUR APP ---

# 1. Map the rooms once
rooms = map_room_numbers('Siebel03.png')

print("Room not found. Here are the rooms I detected:", list(rooms.keys()))

# 2. Get user input
target_room = input("Enter destination room number: ") # e.g., "105"
current_room = input("Enter your current room number: ") # e.g., "101"

if current_room in rooms:
    current_location = rooms[current_room]
    print(f"Current location set to room {current_room} at {current_location}")
else:
    print("Current room not found.")
    exit()

if target_room in rooms:
    destination_coords = rooms[target_room]
    print(f"Room {target_room} found at {destination_coords}")
    
    # 3. Pass to your pathfinding function
    hallway3.find_floorplan_path('Siebel03.png', current_location, destination_coords)
else:
    print("Room not found. Here are the rooms I detected:", list(rooms.keys()))