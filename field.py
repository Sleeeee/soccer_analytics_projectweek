import pandas as pd
import numpy as np

def get_quadrant_coordinates(quadrant_id: int):
    x = (((quadrant_id % 3) * 1/3) + 1/6) * 100
    y = (((quadrant_id // 3) * 1/3) + 1/6) * 100
    return {"x": x, "y": y}

def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def get_closest_quadrant(ball_coords):
    distances = []
    for i in range(9):
        quadrant = get_quadrant_coordinates(i)
        distance = calculate_distance(ball_coords["x"], ball_coords["y"], quadrant["x"], quadrant["y"])
        distances.append(distance)
    return np.argmin(distances)

def get_ball_quadrant(events_df: pd.DataFrame):
    events_df["closest_quadrant"] = events_df.apply(lambda row: get_closest_quadrant({"x": row["x"], "y": row["y"]}), axis=1)
    return events_df.drop(columns=["x", "y"])
