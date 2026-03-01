"use client";

import { useState } from "react";
import styles from "./page.module.css";
import { buildingData } from "./data";

type TargetType = "Room Number" | "Bathroom" | "Water";

export default function Home() {
  const buildings = Object.keys(buildingData);
  const [building, setBuilding] = useState(buildings[0]);
  const [floor, setFloor] = useState(buildingData[buildings[0]][0]);
  const [targetType, setTargetType] = useState<TargetType>("Room Number");

  // NEW: Track both current and destination
  const [currentRoom, setCurrentRoom] = useState("");
  const [destinationRoom, setDestinationRoom] = useState("");

  const [loading, setLoading] = useState(false);
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleBuildingChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newBuilding = e.target.value;
    setBuilding(newBuilding);
    setFloor(buildingData[newBuilding][0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setImageSrc(null);
    setError(null);

    // Construct URL with distinct current and target rooms
    const params = new URLSearchParams({
      building,
      floor,
      curr_room: currentRoom,
      target_room: targetType === "Room Number" ? destinationRoom : "",
      bathroom: (targetType === "Bathroom").toString(),
      water_fountain: (targetType === "Water").toString(),
    });

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/calculate_route?${params.toString()}`);
      console.log("before response");
      if (!response.ok) {
        const errData = await response.json();
        console.log("no response");
        throw new Error(errData.detail || "Failed to fetch floor map");
      }
      console.log("response");
      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      setImageSrc(imageUrl);
    } catch (err: any) {
      console.log("catch response");
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Illini <span className={styles.illiniOrange}>Relief</span></h1>

      <form className={styles.glassCard} onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Building</label>
          <select
            className={styles.select}
            value={building}
            onChange={handleBuildingChange}
          >
            {buildings.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Current Floor</label>
          <select
            className={styles.select}
            value={floor}
            onChange={(e) => setFloor(e.target.value)}
          >
            {buildingData[building].map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Where are you now? (Room #)</label>
          <input
            type="text"
            className={styles.input}
            placeholder="e.g. 1205"
            value={currentRoom}
            onChange={(e) => setCurrentRoom(e.target.value)}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>What are you looking for?</label>
          <select
            className={styles.select}
            value={targetType}
            onChange={(e) => setTargetType(e.target.value as TargetType)}
          >
            <option value="Room Number">Specific Room</option>
            <option value="Bathroom">Nearest Bathroom</option>
            <option value="Water">Nearest Water Fountain</option>
          </select>
        </div>

        {targetType === "Room Number" && (
          <div className={styles.formGroup}>
            <label className={styles.label}>Destination Room Number</label>
            <input
              type="text"
              className={styles.input}
              placeholder="e.g. 2400"
              value={destinationRoom}
              onChange={(e) => setDestinationRoom(e.target.value)}
              required
            />
          </div>
        )}

        <button type="submit" className={styles.button} disabled={loading}>
          {loading ? "Calculating..." : "Find My Way"}
        </button>
        {error && (
          <div className={styles.errorBox}>
            <p>{error}</p>
          </div>
        )}
      </form>

      {imageSrc && (
        <div className={styles.imageContainer}>
          <img src={imageSrc} alt="Navigation Path" className={styles.mapImg} />
        </div>
      )}
    </div>
  );
}