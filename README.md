# 🟠 Illini Relief

> **"Find your way through any UIUC building—instantly."**

**Illini Relief** is an intelligent indoor navigation system designed to eliminate the frustration of getting lost in UIUC’s most complex buildings. By combining Computer Vision (OCR) with advanced pathfinding algorithms, we transform static floorplans into dynamic, routed maps.

---

## The Problem

Navigating "labyrinth" buildings like Grainger Library or Siebel Center is a rite of passage for Illini—but it shouldn't be. Students often waste time wandering hallways looking for a specific classroom, the nearest water fountain, or an accessible restroom. Existing GPS tools stop at the front door; **Illini Relief** takes you the rest of the way.

## Key Features

* **Intelligent OCR Mapping:** Automatically extracts room numbers and spatial coordinates $(x, y)$ from raw PNG floorplans using `EasyOCR`.
* **Hallway-Aware Routing:** Custom pathfinding logic ensures routes follow walkable paths and don't "clip" through walls.
* **POI Quick-Select:** One-tap navigation to the nearest essential facilities (Restrooms, Water Fountains).
* **Modern Glassmorphism UI:** A sleek, responsive Next.js frontend designed for students on the move.

---

## Technical Stack

| Component | Technology |
| --- | --- |
| **Frontend** | Next.js 15 (Turbopack), TypeScript, CSS Modules |
| **Backend** | FastAPI (Python), Uvicorn |
| **Database** | Supabase (PostgreSQL) |
| **Storage** | Supabase Buckets (Floorplan Assets) |
| **CV & Logic** | OpenCV, EasyOCR, NumPy |

---

## How It Works

1. **Ingestion:** Floorplans are uploaded and processed. `room_location.py` identifies room text and anchors them to pixel coordinates.
2. **Spatial Indexing:** Data is stored in Supabase. We index room IDs against building and floor metadata for $O(1)$ lookup speeds.
3. **The Routing Engine:** When a user requests a path:
* The backend retrieves the $(x, y)$ start and end points.
* If a "Bathroom" is requested, it calculates the **Euclidean distance** $d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$ to find the nearest ticker.
* `hallway4.py` generates the optimal path and draws it onto the image buffer.


4. **Delivery:** The processed image is sent back to the Next.js frontend as a `blob` and displayed instantly.

---

## Installation & Setup

### 1. Backend (Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload

```

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev

```

---

## Challenges We Overcame

* **The "Failed to Fetch" Ghost:** We wrestled with CORS middleware and Turbopack caching to ensure seamless communication between our decoupled frontend and backend.
* **Dynamic Image Manipulation:** Handling image buffers in memory to ensure fast response times without cluttering the server's local storage.
* **OCR Accuracy:** Fine-tuning the detection of room numbers on low-contrast architectural drawings.

## Future Roadmap

* **Multi-Floor Routing:** Logic for navigating through stairs and elevators between floors.
* **Live AR View:** Using the phone's camera to overlay pathing arrows on the physical hallway.
* **Crowdsourced Data:** Allowing users to report closed hallways or broken water fountains in real-time.
