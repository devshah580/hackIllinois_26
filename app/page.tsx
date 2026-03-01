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
  const [destinationRoom, setDestinationRoom] = useState("");

  const [loading, setLoading] = useState(false);
  const [imageSrc, setImageSrc] = useState<string | null>(null);

  const handleBuildingChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newBuilding = e.target.value;
    setBuilding(newBuilding);
    setFloor(buildingData[newBuilding][0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setImageSrc(null);

    const payload = {
      building,
      floor,
      room_number: targetType === "Room Number" ? destinationRoom : "",
      bathroom: targetType === "Bathroom" ? 1 : 0,
      water: targetType === "Water" ? 1 : 0,
    };

    try {
      // Placeholder URL. Replace with actual python backend URL
      const response = await fetch("http://127.0.0.1:5000/api/navigate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch floor map");
      }

      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      setImageSrc(imageUrl);
    } catch (error) {
      console.error(error);
      alert("Error connecting to backend or fetching image.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>
        Illini <span className={styles.illiniOrange}>Relief</span>
      </h1>
      <p className={styles.subtitle}>Find your way through any UIUC building.</p>

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
          <div className={`${styles.formGroup} ${styles.expandField}`}>
            <label className={styles.label}>Destination Room Number</label>
            <input
              type="text"
              className={styles.input}
              placeholder="e.g. 2400"
              value={destinationRoom}
              onChange={(e) => setDestinationRoom(e.target.value)}
              required={targetType === "Room Number"}
            />
          </div>
        )}

        <button
          type="submit"
          className={styles.button}
          disabled={loading || (targetType === "Room Number" && !destinationRoom.trim())}
        >
          {loading ? <div className={styles.spinner}></div> : "Find My Way"}
        </button>
      </form>

      {imageSrc && (
        <div className={styles.imageContainer}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={imageSrc} alt="Floor map with navigation path" className={styles.mapImg} />
        </div>
      )}
    </div>
  );
}
