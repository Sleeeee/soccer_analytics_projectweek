import pandas as pd
import matplotlib.pyplot as plt
import mplsoccer

def plot_ball_tracking(tracking_data):
    pitch = mplsoccer.Pitch(pitch_color='grass', line_color='white', pitch_type='opta', pitch_length=105, pitch_width=68)
    fig, ax = pitch.draw(figsize=(12, 8))
    ball_data = tracking_data[tracking_data['player_name'] == 'Ball'].sort_values(by="timestamp")
    ball_data = ball_data.iloc[::10]
    pitch.scatter(ball_data['x'], ball_data['y'], s=3, color='yellow', alpha=1, ax=ax, label='Ball', zorder=3)
    pitch.plot(ball_data['x'], ball_data['y'], color='yellow', alpha=0.6, linewidth=1, ax=ax, zorder=2)
    ax.set_title('Ball Movement Over All Frames', fontsize=16)
    plt.tight_layout()
    plt.show()
    plot_ball_tracking(tracking_df)

def get_ball_plot(team_name: str, match_id: str, conn):
    query = f"""
        SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y, p.jersey_number, p.player_name, p.team_id
        FROM player_tracking pt
        JOIN players p ON pt.player_id = p.player_id
        JOIN teams t ON p.team_id = t.team_id
        JOIN matchevents me ON me.ball_owning_team = t.team_id
        WHERE pt.game_id = '{match_id}' AND p.player_name = 'Ball' AND t.team_name = '{team_name}';
    """
    ball_data = pd.read_sql_query(query, conn)
    plot_ball_tracking(ball_data)
