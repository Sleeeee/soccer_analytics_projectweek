import matplotlib.pyplot as plt
import matplotsoccer as mps
import pandas as pd
import os
import psycopg2
import dotenv

from phases import get_phase_timestamps, get_transition_timestamps

def main():
    dotenv.load_dotenv()

    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_USER = os.getenv("PG_USER")
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")
    PG_DATABASE = os.getenv("PG_DB")

    conn = psycopg2.connect(
        host=PG_HOST,
        database=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
        port=PG_PORT,
        sslmode="require",
    )

    print(get_phase_timestamps("out_of_possession", "Dender", get_transition_timestamps('5uts2s7fl98clqz8uymaazehg', conn)))

    mps.field("green", figsize=8)
    plt.show()

if __name__ == "__main__":
    main()
