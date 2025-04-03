import pandas as pd
import psycopg2
import dotenv
import os
import matplotsoccer
import matplotlib.pyplot as plot
from phases import get_transition_timestamps, get_query_between_timestamps, get_phase_timestamps

def envent_bar(match_id, out_of_possess, ball_team, conn) :
    query = f"""
    SELECT et.name, t.team_name
    FROM players p
    JOIN matchevents me ON p.player_id = me.player_id
    JOIN teams t ON p.team_id = t.team_id
    JOIN eventtypes et ON me.eventtype_id = et.eventtype_id
    WHERE me.match_id = '{match_id}' AND me.ball_owning_team = '{ball_team}' AND p.team_id = '{out_of_possess}' 
    """

    timestamps = get_transition_timestamps(match_id, conn)
    filtered_timestamps = get_phase_timestamps("out_of_possession", out_of_possess, timestamps)
    data = get_query_between_timestamps(query, filtered_timestamps)


    tracking_df = pd.read_sql_query(data, conn)
    event_count = tracking_df['name'].value_counts()
    plot.figure(figsize = (8,6))
    event_count.plot(kind = 'bar')
    plot.title(tracking_df['team_name'][0])
    plot.show() 
