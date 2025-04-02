import pandas as pd
import os
import psycopg2
import dotenv
import math
from matplotlib import pyplot as plt, animation
from mplsoccer import Pitch

from phases import get_phase_timestamps, get_player_tracking, get_transition_timestamps, get_query_between_timestamps

def lerp(x, y, t):
    return x + t * (y - x)

def lerp_series(x, y, t):
    assert len(x) == len(y)
    result = []
    for i in range(len(x)):
        result.append(lerp(x[i], y[i], t))
    return result

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
    df = get_player_tracking('5uts2s7fl98clqz8uymaazehg', conn)
    
    df['x'] = df['x'].map(lambda x: x / 100)
    df['y'] = df['y'].map(lambda x: x / 100)

    df_ball = df[df['player_id'] == 'ball']
    df_home = df[df['team_id'] == '8y3iucyxguipljcmf87a11bk9']
    df_away = df[df['team_id'] == '4dtif7outbuivua8umbwegoo5']

    pitch = Pitch(pitch_type='metricasports', goal_type='line', pitch_width=68, pitch_length=105)
    fig, ax = pitch.draw(figsize=(16, 10.4))

    marker_kwargs = {'marker': 'o', 'markeredgecolor': 'black', 'linestyle': 'None'}
    ball, = ax.plot([], [], ms=10, markerfacecolor='#f00', zorder=3, **marker_kwargs)
    away, = ax.plot([], [], ms=10, markerfacecolor='#0f0', **marker_kwargs)
    home, = ax.plot([], [], ms=10, markerfacecolor='#00f', **marker_kwargs)

    interpoplation_frames = 25

    def animate(i):
        if i % interpoplation_frames == 0:
            i //= interpoplation_frames
            ball.set_data(df_ball.iloc[i, [0]], df_ball.iloc[i, [1]])
            frame = df_ball.iloc[i, 3]
            away.set_data(df_away.loc[df_away.frame_id == frame, 'x'],
                        df_away.loc[df_away.frame_id == frame, 'y'])
            home.set_data(df_home.loc[df_home.frame_id == frame, 'x'],
                        df_home.loc[df_home.frame_id == frame, 'y'])
        else:
            i_float = i/interpoplation_frames
            prev = int(math.floor(i_float))
            next = int(math.ceil(i_float))
            frac = i_float % 1

            ball_prev = df_ball.iloc[prev, [0]], df_ball.iloc[prev, [1]]
            ball_next = df_ball.iloc[next, [0]], df_ball.iloc[next, [1]]
            ball.set_data([
                [lerp(ball_prev[0].values[0], ball_next[0].values[0], frac)],
                [lerp(ball_prev[1].values[0], ball_next[1].values[0], frac)]
            ])
            
            frame_prev = df_ball.iloc[prev, 3]
            frame_next = df_ball.iloc[next, 3]

            away_prev = df_away.loc[df_away.frame_id == frame_prev, 'x'], df_away.loc[df_away.frame_id == frame_prev, 'y']
            away_next = df_away.loc[df_away.frame_id == frame_next, 'x'], df_away.loc[df_away.frame_id == frame_next, 'y']
            away.set_data([
                lerp_series(away_prev[0].values, away_next[0].values, frac),
                lerp_series(away_prev[1].values, away_next[1].values, frac)
            ])
            
            home_prev = df_home.loc[df_home.frame_id == frame_prev, 'x'], df_home.loc[df_home.frame_id == frame_prev, 'y']
            home_next = df_home.loc[df_home.frame_id == frame_next, 'x'], df_home.loc[df_home.frame_id == frame_next, 'y']
            home.set_data([
                lerp_series(home_prev[0].values, home_next[0].values, frac),
                lerp_series(home_prev[1].values, home_next[1].values, frac)
            ])

        return ball, away, home

    ani = animation.FuncAnimation(fig, animate, frames=len(df_ball) * interpoplation_frames, interval=40, blit=True)
    plt.show()

if __name__ == "__main__":
    main()
