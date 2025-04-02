import pandas as pd

def get_transition_timestamps(match_id, conn):
    query = f"""
    SELECT
        event_id,
        period_id,
        timestamp,
        ball_owning_team,
        t.team_name
    FROM matchevents e
    JOIN
        teams t ON e.ball_owning_team = t.team_id
    WHERE e.match_id = '{match_id}'
    ORDER BY period_id, timestamp
    """

    events_df = pd.read_sql_query(query, conn)
    current_timestamp = events_df.iloc[0]['timestamp']
    current_team = events_df.iloc[0]['team_name']
    current_period = events_df.iloc[0]['period_id']
    phase_list = []
    for i, row in events_df.iterrows():
        if i == 0: continue
        if row['team_name'] == current_team:
            continue
        phase_list.append({'team': current_team, 'timestamp': pd.Timedelta(current_timestamp).total_seconds(), 'original_timestamp': current_timestamp, 'period_id': current_period})
        current_team = row['team_name']
        current_timestamp = row['timestamp']
        current_period = row['period_id']

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
        if (target_phase["team"] == current_event["team"] or target_phase["team"] is None) and target_phase["possession"] == current_event["possession"] and current_event["period_id"] == next_event["period_id"]:
            filtered.append({
                "timestamp": current_event["original_timestamp"],
                "period_id": current_event["period_id"],
                "end_timestamp": next_event["original_timestamp"]
            })
    return filtered

def get_query_between_timestamps(query, filtered_data) :
    query += 'AND ('

    timestamp_conditions = []
    for entry in filtered_data:
        start_time = entry['timestamp']
        end_time = entry["end_timestamp"]
        condition = f"(me.timestamp BETWEEN '{start_time}' AND '{end_time}')"
        timestamp_conditions.append(condition)

    query += " OR ".join(timestamp_conditions)
    query += ")"

    return query
