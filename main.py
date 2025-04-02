import pandas as pd
import os
import psycopg2
import dotenv

from animation import render_animation
from phases import get_phase_timestamps, get_transition_timestamps, get_query_between_timestamps

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

    render_animation('5uts2s7fl98clqz8uymaazehg', conn)

    MATCH_ID = "5uts2s7fl98clqz8uymaazehg"
    PHASE_NAME = "out_of_possession"
    TEAM_NAME = "Dender"
    BASE_QUERY = """
        SELECT et.name, p.player_id, p.player_name, p.team_id, me.match_id, me.timestamp, me.end_timestamp
        FROM players p
        JOIN matchevents me ON p.player_id = me.player_id
        JOIN eventtypes et ON me.eventtype_id = et.eventtype_id
        WHERE me.match_id = '5uts2s7fl98clqz8uymaazehg' 
    """

    timestamps = get_transition_timestamps(MATCH_ID, conn)
    phase_timestamps = get_phase_timestamps(PHASE_NAME, TEAM_NAME, timestamps)
    phase_query = get_query_between_timestamps(BASE_QUERY, phase_timestamps)
    phase_df = pd.read_sql_query(phase_query, conn)
    print(phase_df.head())

    print(get_phase_timestamps("out_of_possession", "Dender", get_transition_timestamps('5uts2s7fl98clqz8uymaazehg', conn)))

if __name__ == "__main__":
    main()
