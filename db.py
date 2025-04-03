import pandas as pd

def get_player_tracking(match_id, conn):
    query = f"""
    SELECT
        x,
        y,
        pt.player_id,
        frame_id,
        team_id,
        timestamp,
        period_id
    FROM player_tracking pt
    JOIN players p ON pt.player_id = p.player_id
    WHERE game_id = '{match_id}'
    ORDER BY period_id, timestamp, player_id
    """
    return pd.read_sql_query(query, conn)

def get_home_away(match_id, conn):
    query = f"""
        SELECT
        home_team_id,
        away_team_id
    FROM matches
    WHERE match_id = '{match_id}'
    """
    return pd.read_sql_query(query, conn).iloc[0]
