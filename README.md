# Illini Relief

> **Stop wandering, start walking.** The intelligent indoor navigation system for the University of Illinois Urbana-Champaign.

## Overview

Navigating massive campus buildings like Grainger Library or Siebel Center can feel like entering a labyrinth. **Illini Relief** transforms static, confusing floorplan images into an interactive GPS-like experience. By leveraging Computer Vision and optimized pathfinding, we provide students with the fastest routes to classrooms, restrooms, and water fountains.

## Key Features

* **Intelligent OCR Mapping:** Automatically extracts room numbers and coordinates from raw PNG floorplans.
* **Dynamic Pathfinding:** Uses advanced algorithms to calculate the shortest walkable path through complex hallway geometries.
* **Points of Interest (POI):** One-click routing to the nearest essential facilities (Restrooms, Water Fountains).
* **Seamless UI:** A modern, "glassmorphism" web interface built for speed and accessibility.

## Technical Stack

* **Frontend:** Next.js 15+, TypeScript, CSS Modules.
* **Backend:** FastAPI (Python), Uvicorn.
* **Database & Storage:** Supabase (PostgreSQL + Bucket Storage).
* **Computer Vision:** OpenCV / EasyOCR (via `room_location.py`).
* **Pathfinding Logic:** Custom graph traversal (via `hallway4.py`).

## Getting Started

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev

```

## How it Works

1. **Image Processing:** When a floorplan is uploaded, `room_location.py` scans the image for text, identifying room numbers and their $(x, y)$ coordinates.
2. **Spatial Data:** These coordinates are indexed in **Supabase** for instant lookup.
3. **Request:** The user selects their building, floor, and current location.
4. **The "Relief" Engine:** The backend fetches the floorplan, calculates the shortest path between the start and end coordinates using a custom hallway-aware algorithm, and returns a rendered PNG with the path drawn on it.

## Challenges We Overcame

* **The "Failed to Fetch" Ghost:** Debugging CORS and network handshake issues between Turbopack-driven Next.js and FastAPI.
* **Hallway Geometry:** Ensuring the pathfinding didn't "clip" through walls by implementing a robust collision-aware routing logic.
* **Real-time Image Rendering:** Optimizing the transition from raw image data to a processed, routed map response in under 500ms.
