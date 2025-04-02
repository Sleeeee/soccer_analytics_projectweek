import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplsoccer
import scipy.ndimage

from phases import get_transition_timestamps, get_phase_timestamps, get_query_between_timestamps

def get_heatmap(match_id: str, team_name: str, phase_name: str, conn, fig, ax):
    BASE_QUERY = f"""
        SELECT me.timestamp, me.end_timestamp, me.x, me.y
        FROM matchevents me
        JOIN teams t ON me.team_id = t.team_id
        WHERE me.match_id = '{match_id}' AND t.team_name = '{team_name}'
    """
    timestamps = get_transition_timestamps(match_id, conn)
    phase_timestamps = get_phase_timestamps(phase_name, team_name, timestamps)
    phase_query = get_query_between_timestamps(BASE_QUERY, phase_timestamps, conn)
    phase_df = pd.read_sql_query(phase_query, conn)
    print(phase_query)

    pitch = mplsoccer.Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#efefef')
    pitch.draw(ax=ax, figsize=(6.6, 4.125))
    bin_statistic = pitch.bin_statistic(phase_df.x, phase_df.y, statistic='count', bins=(25, 25))
    bin_statistic['statistic'] = scipy.ndimage.gaussian_filter(bin_statistic['statistic'], 1)
    pcm = pitch.heatmap(bin_statistic, ax=ax, cmap='hot', edgecolors='#22312b')
    fig.set_facecolor('#22312b')
    cbar = fig.colorbar(pcm, ax=ax, shrink=0.6)
    cbar.outline.set_edgecolor('#efefef')
    cbar.ax.yaxis.set_tick_params(color='#efefef')
    ticks = plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#efefef')
    
def get_heatmaps(match_id: str, phase_name: str, conn):
    HOME_TEAM_NAME = "Dender"
    AWAY_TEAM_NAME = "Gent"
    fig, (ax1, ax2) = plt.subplots(1, 2)
    get_heatmap(match_id, HOME_TEAM_NAME, phase_name, conn, fig, ax1)
    get_heatmap(match_id, AWAY_TEAM_NAME, phase_name, conn, fig, ax2)
    plt.show()
