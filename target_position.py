import cv2
import numpy as np
import os


def cluster_matches(matches, distance=25):
    clusters = []

    for m in matches:
        x, y = m["x"], m["y"]
        placed = False

        for cluster in clusters:
            cx, cy = cluster["center"]

            if abs(cx - x) < distance and abs(cy - y) < distance:
                cluster["points"].append(m)

                # Keep best scoring point as center
                best = max(cluster["points"], key=lambda p: p["score"])
                cluster["center"] = (best["x"], best["y"])
                cluster["best"] = best

                placed = True
                break

        if not placed:
            clusters.append({
                "center": (x, y),
                "points": [m],
                "best": m
            })

    return clusters


def template_match_water_fountain(input_folder):
    threshold = 0.625
    ticker_path = os.path.join("ticker_water", "water_fountain.png")

    matches = []

    if not os.path.isfile(ticker_path):
        print("Missing water fountain template")
        return matches

    ticker = cv2.imread(ticker_path)
    ticker_gray = cv2.cvtColor(ticker, cv2.COLOR_BGR2GRAY)

    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)

        if not os.path.isfile(file_path):
            continue

        image = cv2.imread(file_path)
        if image is None:
            continue

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


        for scale in np.linspace(0.08, 0.15, 6):
            resized = cv2.resize(ticker_gray, None, fx=scale, fy=scale)

            if (resized.shape[0] > image_gray.shape[0] or
                resized.shape[1] > image_gray.shape[1]):
                continue

            result = cv2.matchTemplate(
                image_gray,
                resized,
                cv2.TM_CCOEFF_NORMED
            )

            locations = np.where(result >= threshold)

            h, w = resized.shape

            for pt in zip(locations[1], locations[0]):
                x, y = pt

                score = result[y, x]

                matches.append({
                    "image": file,
                    "ticker": "water_fountain",
                    "x": int(x + w / 2),
                    "y": int(y),
                    "score": float(score)
                })

    return matches


def template_match_bathroom(input_folder):
    threshold = 0.625
    ticker_folder = "ticker_bathroom"

    matches = []

    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)

        if not os.path.isfile(file_path):
            continue

        image = cv2.imread(file_path)
        if image is None:
            continue

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


        for ticker_file in os.listdir(ticker_folder):
            ticker_path = os.path.join(ticker_folder, ticker_file)

            if not os.path.isfile(ticker_path):
                continue

            ticker = cv2.imread(ticker_path)
            if ticker is None:
                continue

            ticker_gray = cv2.cvtColor(ticker, cv2.COLOR_BGR2GRAY)

            for scale in np.linspace(0.08, 0.15, 6):
                resized = cv2.resize(
                    ticker_gray,
                    None,
                    fx=scale,
                    fy=scale
                )

                if (resized.shape[0] > image_gray.shape[0] or
                    resized.shape[1] > image_gray.shape[1]):
                    continue

                result = cv2.matchTemplate(
                    image_gray,
                    resized,
                    cv2.TM_CCOEFF_NORMED
                )

                locations = np.where(result >= threshold)

                h, w = resized.shape

                for pt in zip(locations[1], locations[0]):
                    x, y = pt

                    score = result[y, x]

                    matches.append({
                        "image": file,
                        "ticker": ticker_file,
                        "x": int(x + w / 2),
                        "y": int(y),
                        "score": float(score)
                    })

    return matches


if __name__ == "__main__":
    input_folder = "data_with_tickers_png"

    # Water fountains
    water_matches = template_match_water_fountain(input_folder)
    water_clusters = cluster_matches(water_matches)
        

    # Bathrooms
    bathroom_matches = template_match_bathroom(input_folder)
    bathroom_clusters = cluster_matches(bathroom_matches)

    
        