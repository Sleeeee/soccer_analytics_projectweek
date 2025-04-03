import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplsoccer
import scipy.ndimage

from phases import get_transition_timestamps, get_phase_timestamps, get_query_between_timestamps

def get_heatmap(match_id: str, team_name: str, home: bool, period_id: int, phase_name: str, conn, fig, ax, vmin=None, vmax=None):
    BASE_QUERY = f"""
        SELECT me.timestamp, me.end_timestamp, me.x, me.y
        FROM matchevents me
        JOIN teams t ON me.team_id = t.team_id
        WHERE me.match_id = '{match_id}' AND t.team_name = '{team_name}' AND me.period_id = {period_id}
    """
    timestamps = get_transition_timestamps(match_id, conn)
    phase_timestamps = get_phase_timestamps(phase_name, team_name, timestamps)
    phase_query = get_query_between_timestamps(BASE_QUERY, phase_timestamps)
    phase_df = pd.read_sql_query(phase_query, conn)

    pitch = mplsoccer.Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#efefef')
    pitch.draw(ax=ax, figsize=(6.6, 4.125))
    bin_statistic = pitch.bin_statistic(phase_df.x, phase_df.y, statistic='count', bins=(10, 10))
    bin_statistic['statistic'] = scipy.ndimage.gaussian_filter(bin_statistic['statistic'], 1)
    pcm = pitch.heatmap(bin_statistic, ax=ax, cmap='hot', edgecolors='#22312b', vmin=vmin, vmax=vmax)
    fig.set_facecolor('#22312b')
    cbar = fig.colorbar(pcm, ax=ax, shrink=0.6)
    cbar.outline.set_edgecolor('#efefef')
    cbar.ax.yaxis.set_tick_params(color='#efefef')
    ticks = plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#efefef')
    ax.set_title(f"{team_name} - Half {period_id}\n{'→' if home else '←'}", color="white")

def get_match_heatmaps(match_id: str, phase_name: str, filename: str, conn):
    query = f"""
        SELECT t1.team_name AS home_team , t2.team_name AS away_team, m.home_score, m.away_score
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        WHERE m.match_id = '{match_id}'
    """
    teams = pd.read_sql_query(query, conn)
    fig, axes = plt.subplots(2, 2)
    ax1, ax2, ax3, ax4 = axes.flatten()
    global_vmin = float('inf')
    global_vmax = float('-inf') 
    for team_name, home, period_id, ax in [
        (teams["home_team"][0], True, 1, ax1),
        (teams["away_team"][0], False, 1, ax2),
        (teams["home_team"][0], True, 2, ax3),
        (teams["away_team"][0], False, 2, ax4)
    ]:
        BASE_QUERY = f"""
            SELECT me.timestamp, me.end_timestamp, me.x, me.y
            FROM matchevents me
            JOIN teams t ON me.team_id = t.team_id
            JOIN matches m ON me.match_id = m.match_id
            WHERE me.match_id = '{match_id}' AND t.team_name = '{team_name}' AND me.period_id = {period_id}
        """
        timestamps = get_transition_timestamps(match_id, conn)
        phase_timestamps = get_phase_timestamps(phase_name, team_name, timestamps)
        phase_query = get_query_between_timestamps(BASE_QUERY, phase_timestamps)
        phase_df = pd.read_sql_query(phase_query, conn)

        pitch = mplsoccer.Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#efefef')
        pitch.draw(ax=ax, figsize=(6.6, 4.125))
        bin_statistic = pitch.bin_statistic(phase_df.x, phase_df.y, statistic='count', bins=(10, 10))
        bin_statistic['statistic'] = scipy.ndimage.gaussian_filter(bin_statistic['statistic'], 1)
        local_vmin = bin_statistic['statistic'].min()
        local_vmax = bin_statistic['statistic'].max()
        global_vmin = min(global_vmin, local_vmin)
        global_vmax = max(global_vmax, local_vmax)

    get_heatmap(match_id, teams["home_team"][0], True, 1, phase_name, conn, fig, ax1, vmin=global_vmin, vmax=global_vmax)
    get_heatmap(match_id, teams["away_team"][0], False, 1, phase_name, conn, fig, ax2, vmin=global_vmin, vmax=global_vmax)
    get_heatmap(match_id, teams["home_team"][0], True, 2, phase_name, conn, fig, ax3, vmin=global_vmin, vmax=global_vmax)
    get_heatmap(match_id, teams["away_team"][0], False, 2, phase_name, conn, fig, ax4, vmin=global_vmin, vmax=global_vmax)

    fig.suptitle(f"Match events when out of possession - {teams["home_team"][0]} {teams["home_score"][0]} - {teams["away_score"][0]} {teams["away_team"][0]}", color="white")
    plt.savefig(f"./figures/{filename}")
    print(f"{filename} saved")

def get_team_season_heatmaps(team_name: str, phase_name: str, conn):
    query = f"""
        SELECT m.match_id
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        WHERE t1.team_name = '{team_name}' OR t2.team_name = '{team_name}';
    """
    matches_df = pd.read_sql_query(query, conn)
    matches = matches_df["match_id"].values
    for match in matches:
        try:
            get_match_heatmaps(match, phase_name, match, conn)
        except:
            print(f"Could not generate heatmap for match {match}")
