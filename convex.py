import pandas as pd
import psycopg2 
import dotenv
import os
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotsoccer as mps
from phases import get_phase_timestamps, get_query_between_timestamps, get_transition_timestamps



def display_convex(query, conn) : 
    tracking_df = pd.read_sql_query(query, conn)
    pitch = Pitch()
    fig, ax = pitch.draw(figsize=(8, 6))
    hull = pitch.convexhull(tracking_df.x * 1.2, tracking_df.y * 0.8)
    poly = pitch.polygon(hull, ax=ax, edgecolor='cornflowerblue', facecolor='cornflowerblue', alpha=0.3)
    scatter = pitch.scatter(tracking_df.x * 1.2, tracking_df.y * 0.8, ax=ax, edgecolor='black', facecolor='cornflowerblue')
    plt.show()