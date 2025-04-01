import re
import pandas as pd
import psycopg2
import dotenv
import os

def timestamp_to_seconds(timestamp: str):
    if not timestamp.endswith("000"):
        timestamp += ".000000"
    m = re.match(r'(\d+) days (\d\d):(\d\d):(\d\d)\.(\d+)', timestamp)
    return (int(m.group(1)) * 24 * 60 * 60 * 1000000 + int(m.group(2)) * 60 * 60 * 1000000 + int(m.group(3)) * 60 * 1000000 + int(m.group(4)) * 1000000 + int(m.group(5))) / 1000000

def get_transition_timestamps(match_id, conn):
    query = f"""
    SELECT
        event_id,
        timestamp,
        -- end_timestamp,
        ball_owning_team,
        t.team_name
    FROM matchevents e
    JOIN
        teams t ON e.ball_owning_team = t.team_id
    WHERE e.match_id = '{match_id}'
    ORDER BY timestamp
    """

    events_df = pd.read_sql_query(query, conn)
    current_timestamp = events_df.iloc[0]['timestamp']
    current_team = events_df.iloc[0]['team_name']
    phase_list = []
    for i, row in events_df.iterrows():
        if i == 0: continue
        if row['team_name'] == current_team:
            continue
        phase_list.append({'team': current_team, 'timestamp': timestamp_to_seconds(current_timestamp), 'original_timestamp': current_timestamp})
        current_team = row['team_name']
        current_timestamp = row['timestamp']

    phase_list2 = []
    for i in range(len(phase_list)):
        if i == len(phase_list)-1:
            break
        
        if phase_list[i+1]['timestamp'] - phase_list[i]['timestamp'] > 5:
            phase = phase_list[i]
            phase['possession'] = False
            phase_list2.append(phase.copy())

            phase['possession'] = True
            phase['timestamp'] += 5
            phase_list2.append(phase)
        else:
            phase = phase_list[i]
            phase['possession'] = False
            phase_list2.append(phase)
    return phase_list2

def get_phase_timestamps(phase_name: str, team_name: str, timestamps: list):
    phase_map = {
        "possession": {
            "team": team_name,
            "possession": True
        },
        "out_of_possession": {
            "team": None,
            "possession": True
        },
        "transition_to_attack": {
            "team": team_name,
            "possession": False
        },
        "transition_to_defense": {
            "team": None,
            "possession": False
        }
    }
    target_phase = phase_map.get(phase_name)
    if not target_phase:
        raise ValueError("Invalid phase_name or team_status")
    filtered = []
    for i in range(len(timestamps) - 1):
        current_event = timestamps[i]
        next_event = timestamps[i+1]
        if (target_phase["team"] == current_event["team"] or target_phase["team"] is None) and target_phase["possession"] == current_event["possession"]:
            filtered.append({
                "timestamp": current_event["original_timestamp"],
                "end_timestamp": next_event["original_timestamp"]
            })
    return filtered
