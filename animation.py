import math
import pandas as pd
from matplotlib import pyplot as plt, animation
from mplsoccer import Pitch

from db import get_home_away, get_player_tracking
from phases import get_phases, get_transition_timestamps

def lerp(x, y, t):
    return x + t * (y - x)

def lerp_series(x, y, t):
    assert len(x) == len(y)
    result = []
    for i in range(len(x)):
        result.append(lerp(x[i], y[i], t))
    return result

def render_animation(match_id, interpolation, frame_interval, conn):
    df = get_player_tracking(match_id, conn)
    home_away = get_home_away(match_id, conn)
    phases = get_phases(home_away['home_team_id'], get_transition_timestamps(match_id, conn))

    df['x'] = df['x'].map(lambda x: 1 - (x / 100))
    df['y'] = df['y'].map(lambda y: 1 - (y / 100))

    df_ball = df[df['player_id'] == 'ball']
    df_home = df[df['team_id'] == home_away['home_team_id']]
    df_away = df[df['team_id'] == home_away['away_team_id']]

    pitch = Pitch(pitch_type='metricasports', goal_type='line', pitch_width=68, pitch_length=105)
    fig, ax = pitch.draw(figsize=(8, 6))

    marker_kwargs = {'marker': 'o', 'markeredgecolor': 'black', 'linestyle': 'None'}
    ball, = ax.plot([], [], ms=6, markerfacecolor='#f00', zorder=3, **marker_kwargs)
    away, = ax.plot([], [], ms=6, markerfacecolor='#0f0', **marker_kwargs)
    home, = ax.plot([], [], ms=6, markerfacecolor='#00f', **marker_kwargs)

    home_hull, = ax.fill([], [], "#0000ff55")
    away_hull, = ax.fill([], [], "#00ff0055")

    info = ax.text(0, -0.01, '')

    interpolation += 1

    next_phase = {'next_phase':1}

    def animate(i):
        if i % interpolation == 0:
            i //= interpolation

            while phases[next_phase['next_phase']]['timestamp'] < pd.Timedelta(df_ball.iloc[i, 5]).total_seconds():
                next_phase['next_phase'] += 1

            timestamp_str = str(pd.Timedelta(df_ball.iloc[i, 5]).round('s')).replace('0 days', '')
            current_phase = phases[next_phase['next_phase']-1]['phase']
            info.set_text(f'Period: {df_ball.iloc[i, 6]}, Time: {timestamp_str}, Phase: {current_phase}')

            ball.set_data(df_ball.iloc[i, [0]], df_ball.iloc[i, [1]])
            frame = df_ball.iloc[i, 3]
            away.set_data(df_away.loc[df_away.frame_id == frame, 'x'], df_away.loc[df_away.frame_id == frame, 'y'])
            home.set_data(df_home.loc[df_home.frame_id == frame, 'x'], df_home.loc[df_home.frame_id == frame, 'y'])

            home_convex_hull = pitch.convexhull(df_home.loc[df_home.frame_id == frame, 'x'], df_home.loc[df_home.frame_id == frame, 'y'])
            home_hull.set_xy(home_convex_hull[0])

            away_convex_hull = pitch.convexhull(df_away.loc[df_away.frame_id == frame, 'x'], df_away.loc[df_away.frame_id == frame, 'y'])
            away_hull.set_xy(away_convex_hull[0])
        else:
            i_float = i / interpolation
            prev = int(math.floor(i_float))
            next = int(math.ceil(i_float))
            frac = i_float % 1

            ball_prev = df_ball.iloc[prev, [0]], df_ball.iloc[prev, [1]]
            ball_next = df_ball.iloc[next, [0]], df_ball.iloc[next, [1]]
            ball.set_data([
                [lerp(ball_prev[0].values[0], ball_next[0].values[0], frac)],
                [lerp(ball_prev[1].values[0], ball_next[1].values[0], frac)],
            ])
            
            frame_prev = df_ball.iloc[prev, 3]
            frame_next = df_ball.iloc[next, 3]

            away_prev = df_away.loc[df_away.frame_id == frame_prev, 'x'], df_away.loc[df_away.frame_id == frame_prev, 'y']
            away_next = df_away.loc[df_away.frame_id == frame_next, 'x'], df_away.loc[df_away.frame_id == frame_next, 'y']
            away_data = [
                lerp_series(away_prev[0].values, away_next[0].values, frac),
                lerp_series(away_prev[1].values, away_next[1].values, frac),
            ]
            away.set_data(away_data)
            
            home_prev = df_home.loc[df_home.frame_id == frame_prev, 'x'], df_home.loc[df_home.frame_id == frame_prev, 'y']
            home_next = df_home.loc[df_home.frame_id == frame_next, 'x'], df_home.loc[df_home.frame_id == frame_next, 'y']
            home_data = [
                lerp_series(home_prev[0].values, home_next[0].values, frac),
                lerp_series(home_prev[1].values, home_next[1].values, frac),
            ]
            home.set_data(home_data)

            home_convex_hull = pitch.convexhull(home_data[0], home_data[1])
            home_hull.set_xy(home_convex_hull[0])

            away_convex_hull = pitch.convexhull(away_data[0], away_data[1])
            away_hull.set_xy(away_convex_hull[0])

        return ball, away, home, home_hull, away_hull, info

    ani = animation.FuncAnimation(fig, animate, frames=len(df_ball) * interpolation, interval=frame_interval, blit=True)
    plt.show()
