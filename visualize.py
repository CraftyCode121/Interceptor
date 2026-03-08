import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np
import pandas as pd
from scenario import run_scenario


def plot_trajectory(trajectory, title="Missile Trajectory", save=False):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')

    ax1 = axes[0, 0]
    ax1.plot(trajectory['x'] / 1000, trajectory['y'] / 1000,
             color='red', linewidth=2)
    ax1.set_xlabel('Horizontal Distance (km)')
    ax1.set_ylabel('Altitude (km)')
    ax1.set_title('Flight Path')
    ax1.fill_between(trajectory['x'] / 1000, 0,
                     trajectory['y'] / 1000, alpha=0.1, color='red')
    ax1.grid(True, alpha=0.3)
    max_height_idx = trajectory['y'].idxmax()
    ax1.annotate('Peak',
                 xy=(trajectory['x'][max_height_idx] / 1000,
                     trajectory['y'][max_height_idx] / 1000),
                 xytext=(10, 10), textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', color='black'),
                 fontsize=9)

    ax2 = axes[0, 1]
    speed = np.sqrt(trajectory['vx']**2 + trajectory['vy']**2)
    ax2.plot(trajectory['time'], speed, color='blue', linewidth=2)
    ax2.axvline(x=10, color='orange', linestyle='--', label='Burnout (t=10s)')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Speed (m/s)')
    ax2.set_title('Speed Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    ax3 = axes[1, 0]
    ax3.plot(trajectory['time'], trajectory['y'] / 1000,
             color='green', linewidth=2)
    ax3.axvline(x=10, color='orange', linestyle='--', label='Burnout (t=10s)')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Altitude (km)')
    ax3.set_title('Altitude Over Time')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    ax4 = axes[1, 1]
    ax4.plot(trajectory['time'], trajectory['vx'],
             color='purple', linewidth=2, label='vx (horizontal)')
    ax4.plot(trajectory['time'], trajectory['vy'],
             color='cyan', linewidth=2, label='vy (vertical)')
    ax4.axvline(x=10, color='orange', linestyle='--', label='Burnout (t=10s)')
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Velocity (m/s)')
    ax4.set_title('Velocity Components Over Time')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.2, hspace=0.5)
    if save:
        plt.savefig('./visuals/trajectory.png', dpi=150, bbox_inches='tight')
        print("Plot saved as trajectory.png")
    plt.show()


def plot_scenario(m_traj, i_traj, intercept_time=None, intercept_point=None):
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor('#0a0a1a')
    for ax in axes:
        ax.set_facecolor('#0d1117')
        ax.tick_params(colors='#aaaaaa')
        ax.xaxis.label.set_color('#aaaaaa')
        ax.yaxis.label.set_color('#aaaaaa')
        ax.title.set_color('white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#333355')

    ax1 = axes[0]
    ax1.plot(m_traj['x'] / 1000, m_traj['y'] / 1000,
             color='#ff4444', linewidth=2, label='Missile', zorder=3)
    ax1.plot(i_traj['x'] / 1000, i_traj['y'] / 1000,
             color='#44aaff', linewidth=2, label='Interceptor', zorder=3)
    ax1.scatter(m_traj['x'].iloc[0] / 1000, m_traj['y'].iloc[0] / 1000,
                color='#ff4444', s=80, zorder=5, marker='^')
    ax1.scatter(i_traj['x'].iloc[0] / 1000, i_traj['y'].iloc[0] / 1000,
                color='#44aaff', s=80, zorder=5, marker='^')
    if intercept_point:
        px, py = intercept_point[0] / 1000, intercept_point[1] / 1000
        ax1.scatter(px, py, color='yellow', s=200, zorder=6,
                    marker='*', label=f'Intercept ({px:.1f} km, {py:.1f} km)')
        circle = plt.Circle((px, py), 0.3, color='yellow', alpha=0.15, zorder=4)
        ax1.add_patch(circle)
        ax1.annotate(f'  HIT t={intercept_time:.1f}s',
                     xy=(px, py), color='yellow', fontsize=9, va='center')
    ax1.set_xlabel('Horizontal Distance (km)')
    ax1.set_ylabel('Altitude (km)')
    ax1.set_title('Intercept Scenario — Flight Paths')
    ax1.legend(facecolor='#1a1a2e', labelcolor='white', edgecolor='#333355')
    ax1.grid(True, alpha=0.15, color='#334')

    ax2 = axes[1]
    common_times = np.intersect1d(
        np.round(m_traj['time'].values, 2),
        np.round(i_traj['time'].values, 2)
    )
    m_sync = m_traj[np.round(m_traj['time'], 2).isin(common_times)].reset_index(drop=True)
    i_sync = i_traj[np.round(i_traj['time'], 2).isin(common_times)].reset_index(drop=True)
    dist = np.sqrt((m_sync['x'] - i_sync['x'])**2 +
                   (m_sync['y'] - i_sync['y'])**2) / 1000
    ax2.plot(common_times, dist, color='#88ff88', linewidth=2)
    ax2.fill_between(common_times, dist, alpha=0.1, color='#88ff88')
    if intercept_time:
        ax2.axvline(x=intercept_time, color='yellow', linestyle='--',
                    label=f'Intercept {intercept_time:.1f}s')
        ax2.axhline(y=0.03, color='orange', linestyle=':', alpha=0.6,
                    label='Kill radius (30m)')
        ax2.legend(facecolor='#1a1a2e', labelcolor='white', edgecolor='#333355')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Distance between objects (km)')
    ax2.set_title('Closing Distance Over Time')
    ax2.grid(True, alpha=0.15, color='#334')

    fig.suptitle('MISSILE DEFENSE SCENARIO', fontsize=15,
                 fontweight='bold', color='white', y=1.01)
    plt.tight_layout()
    plt.savefig('./visuals/scenario.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    print("Saved scenario.png")
    plt.show()


def animate_scenario(m_traj, i_traj, intercept_time=None, intercept_point=None,
                     radar_time=None, launch_time=None):

    i_start_x = i_traj['x'].iloc[0] / 1000
    i_start_y = i_traj['y'].iloc[0] / 1000  

    i_times = i_traj['time'].values
    m_window = m_traj[(m_traj['time'] >= i_times[0]) &
                      (m_traj['time'] <= i_times[-1])].copy()

    m_r = np.round(m_window['time'].values, 2)
    i_r = np.round(i_traj['time'].values, 2)
    common_times = np.intersect1d(m_r, i_r)

    m_sync = m_window[np.isin(m_r, common_times)].reset_index(drop=True)
    i_sync = i_traj[np.isin(i_r, common_times)].reset_index(drop=True)
    n = min(len(m_sync), len(i_sync))
    m_sync = m_sync.iloc[:n]
    i_sync = i_sync.iloc[:n]
    common_times = common_times[:n]

    dist_km = np.sqrt((m_sync['x'].values - i_sync['x'].values)**2 +
                      (m_sync['y'].values - i_sync['y'].values)**2) / 1000

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor('#0a0a1a')
    for ax in axes:
        ax.set_facecolor('#0d1117')
        ax.tick_params(colors='#aaaaaa')
        ax.xaxis.label.set_color('#aaaaaa')
        ax.yaxis.label.set_color('#aaaaaa')
        ax.title.set_color('white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#333355')

    fig.suptitle('MISSILE DEFENSE SCENARIO', fontsize=15,
                 fontweight='bold', color='white')

    ax1 = axes[0]

    all_x = pd.concat([m_traj['x'], i_traj['x']]) / 1000
    all_y = pd.concat([m_traj['y'], i_traj['y']]) / 1000
    ax1.set_xlim(all_x.min() - 0.5, all_x.max() + 0.5)
    ax1.set_ylim(-0.2, all_y.max() * 1.2)
    ax1.set_xlabel('Horizontal Distance (km)')
    ax1.set_ylabel('Altitude (km)')
    ax1.set_title('Flight Paths')
    ax1.grid(True, alpha=0.15, color='#334')
    ax1.axhline(y=0, color='#445', linewidth=1)

    ax1.scatter(m_traj['x'].iloc[0] / 1000, 0,
                color='#ff4444', s=80, marker='^', zorder=5)

    ax1.scatter(i_start_x, 0,
                color='#44aaff', s=80, marker='s', zorder=5)

    ax1.text(m_traj['x'].iloc[0] / 1000, -0.15, 'LAUNCH',
             color='#ff6666', fontsize=7, ha='center')
    ax1.text(i_start_x, -0.15, 'DEFENSE',
             color='#66bbff', fontsize=7, ha='center')

    m_trail, = ax1.plot([], [], color='#ff4444', linewidth=1.5,
                        alpha=0.8, label='Missile')
    i_trail, = ax1.plot([], [], color='#44aaff', linewidth=1.5,
                        alpha=0.8, label='Interceptor')
    m_dot,   = ax1.plot([], [], 'o', color='#ff6666', markersize=9, zorder=6)
    i_dot,   = ax1.plot([], [], 'o', color='#66bbff', markersize=9, zorder=6)

    i_static, = ax1.plot([i_start_x], [0], 's',
                         color='#44aaff', markersize=9, zorder=6)

    blast_circle = Circle((0, 0), 0.25, color='yellow', alpha=0, zorder=7)
    ax1.add_patch(blast_circle)
    hit_star, = ax1.plot([], [], '*', color='yellow', markersize=24, zorder=8)
    hit_text  = ax1.text(0, 0, '', color='yellow', fontsize=10,
                         va='bottom', fontweight='bold')

    status_text = ax1.text(0.02, 0.97, 'MISSILE IN FLIGHT',
                           transform=ax1.transAxes,
                           color='#aaffaa', fontsize=9, va='top',
                           fontfamily='monospace')

    ax1.legend(facecolor='#1a1a2e', labelcolor='white',
               edgecolor='#333355', loc='upper right')

    ax2 = axes[1]
    full_t_end = m_traj['time'].iloc[-1]
    ax2.set_xlim(0, full_t_end + 1)
    ax2.set_ylim(0, dist_km.max() * 1.15)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Distance between objects (km)')
    ax2.set_title('Closing Distance Over Time')
    ax2.grid(True, alpha=0.15, color='#334')

    ax2.axhline(y=0.03, color='orange', linestyle=':', alpha=0.7,
                label='Kill radius (30 m)')
    if radar_time:
        ax2.axvline(x=radar_time, color='#ffaa00', linestyle='--', alpha=0.7,
                    label=f'Radar lock (t={radar_time:.1f}s)')
    if launch_time:
        ax2.axvline(x=launch_time, color='#44aaff', linestyle='--', alpha=0.7,
                    label=f'Interceptor launch (t={launch_time:.1f}s)')
    if intercept_time:
        ax2.axvline(x=intercept_time, color='yellow', linestyle='--', alpha=0.7,
                    label=f'Intercept (t={intercept_time:.1f}s)')
    ax2.legend(facecolor='#1a1a2e', labelcolor='white',
               edgecolor='#333355', fontsize=8)

    dist_line,  = ax2.plot([], [], color='#88ff88', linewidth=2)
    time_cursor = ax2.axvline(x=0, color='white', linewidth=0.8, alpha=0.4)

    time_text = fig.text(0.5, 0.02, 't = 0.00 s', ha='center',
                         color='#cccccc', fontsize=12)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.09)

    n_total = len(m_traj)
    step    = max(1, n_total // 600)

    intercepted = [False]

    def update(frame):
        fi   = min(frame * step, n_total - 1)
        t_now = float(m_traj['time'].iloc[fi])

        mx = m_traj['x'].iloc[:fi + 1] / 1000
        my = m_traj['y'].iloc[:fi + 1] / 1000
        m_trail.set_data(mx.values, my.values)
        m_dot.set_data([mx.iloc[-1]], [my.iloc[-1]])

        if launch_time is None or t_now < launch_time:
            i_static.set_data([i_start_x], [0])
            i_trail.set_data([], [])
            i_dot.set_data([], [])
        else:
            i_static.set_data([], [])
            i_mask = i_traj['time'] <= t_now
            if i_mask.any():
                ix = i_traj['x'][i_mask] / 1000
                iy = i_traj['y'][i_mask] / 1000
                i_trail.set_data(ix.values, iy.values)
                i_dot.set_data([ix.iloc[-1]], [iy.iloc[-1]])

        if not intercepted[0]:
            if radar_time and t_now >= radar_time and \
               (launch_time is None or t_now < launch_time):
                status = 'RADAR LOCK — TRACKING'
                status_text.set_color('#ffcc00')
            elif launch_time and t_now >= launch_time:
                status = 'INTERCEPTOR IN FLIGHT'
                status_text.set_color('#44aaff')
            else:
                status = 'MISSILE IN FLIGHT'
                status_text.set_color('#aaffaa')
        else:
            status = '  TARGET DESTROYED  '
            status_text.set_color('yellow')
        status_text.set_text(status)

        # ── Intercept flash ──
        if intercept_time and t_now >= intercept_time and not intercepted[0]:
            intercepted[0] = True
            px = intercept_point[0] / 1000
            py = intercept_point[1] / 1000
            blast_circle.center = (px, py)
            blast_circle.set_alpha(0.35)
            hit_star.set_data([px], [py])
            hit_text.set_position((px + 0.15, py + 0.15))
            hit_text.set_text(f'HIT t={intercept_time:.1f}s')
            m_dot.set_data([px], [py])
            i_dot.set_data([px], [py])
            i_trail.set_data(
                i_traj['x'].values / 1000,
                i_traj['y'].values / 1000
            )
            m_trail.set_data(
                m_traj['x'].values / 1000,
                m_traj['y'].values / 1000
            )

        # ── Closing distance line ──
        mask = common_times <= t_now
        if mask.any():
            dist_line.set_data(common_times[mask], dist_km[mask])
        time_cursor.set_xdata([t_now, t_now])

        time_text.set_text(f't = {t_now:.2f} s')

        return (m_trail, i_trail, m_dot, i_dot, i_static,
                blast_circle, hit_star, hit_text, status_text,
                dist_line, time_cursor, time_text)

    total_frames = (n_total + step - 1) // step
    ani = animation.FuncAnimation(
        fig, update, frames=total_frames, interval=30, blit=True
    )

    ani.save('./visuals/scenario_animation.mp4', writer='ffmpeg', fps=30,
             savefig_kwargs={'facecolor': fig.get_facecolor()})
    print("Saved scenario_animation.mp4")
    plt.close(fig)
    return ani
