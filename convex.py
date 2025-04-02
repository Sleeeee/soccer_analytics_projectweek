import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotsoccer as mps

def display_convex(query, conn) : 
    tracking_df = pd.read_sql_query(query, conn)
    pitch = Pitch(pitch_type='metricasports', goal_type='line', pitch_width=68, pitch_length=105)
    fig, ax = pitch.draw(figsize=(8, 6))
    hull = pitch.convexhull(tracking_df.x * 0.01, tracking_df.y * 0.01)
    poly = pitch.polygon(hull, ax=ax, edgecolor='cornflowerblue', facecolor='cornflowerblue', alpha=0.3)
    scatter = pitch.scatter(tracking_df.x * 0.01, tracking_df.y * 0.01, ax=ax, edgecolor='black', facecolor='cornflowerblue')
    plt.show()