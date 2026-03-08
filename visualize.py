import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
from matplotlib.ticker import MultipleLocator
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd
from scenario import run_scenario

DARK_BG      = '#03080f'
PANEL_BG     = '#060d16'
GRID_COLOR   = '#0d2035'
ACCENT_GREEN = '#00ff41'
ACCENT_AMBER = '#ffb000'
THREAT_RED   = '#ff2a2a'
INTERCEPT_BLU= '#00aaff'
KILL_WHITE   = '#e8f0f8'
DIM_TEXT     = '#3a6080'
SCAN_LINE    = '#0d2a1a'

def _apply_hud_style(ax):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=DIM_TEXT, labelsize=7, length=3, width=0.5)
    ax.xaxis.label.set_color(DIM_TEXT)
    ax.yaxis.label.set_color(DIM_TEXT)
    ax.xaxis.label.set_fontsize(8)
    ax.yaxis.label.set_fontsize(8)
    ax.title.set_color(ACCENT_GREEN)
    ax.title.set_fontsize(9)
    ax.title.set_fontfamily('monospace')
    for spine in ax.spines.values():
        spine.set_edgecolor('#0d3050')
        spine.set_linewidth(0.8)
    ax.grid(True, color=GRID_COLOR, linewidth=0.4, alpha=1.0)
    ax.xaxis.set_minor_locator(MultipleLocator(
        (ax.get_xlim()[1] - ax.get_xlim()[0]) / 40 if ax.get_xlim()[1] != ax.get_xlim()[0] else 1
    ))
    ax.yaxis.set_minor_locator(MultipleLocator(
        (ax.get_ylim()[1] - ax.get_ylim()[0]) / 40 if ax.get_ylim()[1] != ax.get_ylim()[0] else 1
    ))
    ax.grid(True, which='minor', color=SCAN_LINE, linewidth=0.2, alpha=0.6)

def _corner_brackets(ax, color=ACCENT_GREEN, size=0.04, lw=1.0):
    corners = [(0, 0), (1, 0), (0, 1), (1, 1)]
    dx_signs = [1, -1, 1, -1]
    dy_signs = [1, 1, -1, -1]
    for (cx, cy), dxs, dys in zip(corners, dx_signs, dy_signs):
        ax.plot([cx, cx + dxs * size], [cy, cy],
                transform=ax.transAxes, color=color, lw=lw, clip_on=False)
        ax.plot([cx, cx], [cy, cy + dys * size],
                transform=ax.transAxes, color=color, lw=lw, clip_on=False)

def _hud_label(ax, text):
    ax.text(0.012, 0.988, text, transform=ax.transAxes,
            color=ACCENT_GREEN, fontsize=7, va='top', fontfamily='monospace',
            alpha=0.7)

def plot_trajectory(trajectory, title="Missile Trajectory", save=False):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle(f'[ {title.upper()} ]', fontsize=13, fontweight='bold',
                 color=ACCENT_GREEN, fontfamily='monospace', y=0.98)

    ax1 = axes[0, 0]
    ax1.set_xlim(trajectory['x'].min() / 1000 - 1,
                 trajectory['x'].max() / 1000 + 1)
    ax1.set_ylim(-0.5, trajectory['y'].max() / 1000 * 1.18)
    _apply_hud_style(ax1)
    ax1.plot(trajectory['x'] / 1000, trajectory['y'] / 1000,
             color=THREAT_RED, linewidth=1.4,
             path_effects=[pe.Stroke(linewidth=3, foreground=THREAT_RED, alpha=0.18),
                           pe.Normal()])
    ax1.fill_between(trajectory['x'] / 1000, 0,
                     trajectory['y'] / 1000, alpha=0.06, color=THREAT_RED)
    ax1.axhline(y=0, color='#1a3a55', linewidth=0.8)
    ax1.set_xlabel('HORIZONTAL DISTANCE (km)')
    ax1.set_ylabel('ALTITUDE (km)')
    ax1.set_title('// FLIGHT PATH')
    _corner_brackets(ax1, color=THREAT_RED)
    _hud_label(ax1, 'TRK-001')
    max_height_idx = trajectory['y'].idxmax()
    px = trajectory['x'][max_height_idx] / 1000
    py = trajectory['y'][max_height_idx] / 1000
    ax1.annotate(f'APOGEE\n{py:.1f} km',
                 xy=(px, py), xytext=(15, 10), textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', color=ACCENT_AMBER, lw=0.8),
                 color=ACCENT_AMBER, fontsize=7, fontfamily='monospace')

    ax2 = axes[0, 1]
    speed = np.sqrt(trajectory['vx']**2 + trajectory['vy']**2)
    ax2.set_xlim(trajectory['time'].min(), trajectory['time'].max())
    ax2.set_ylim(0, speed.max() * 1.15)
    _apply_hud_style(ax2)
    ax2.plot(trajectory['time'], speed, color=INTERCEPT_BLU, linewidth=1.4,
             path_effects=[pe.Stroke(linewidth=3, foreground=INTERCEPT_BLU, alpha=0.18),
                           pe.Normal()])
    ax2.axvline(x=10, color=ACCENT_AMBER, linestyle='--', linewidth=0.8,
                label='BURNOUT t=10s')
    ax2.set_xlabel('TIME (s)')
    ax2.set_ylabel('SPEED (m/s)')
    ax2.set_title('// SPEED PROFILE')
    ax2.legend(facecolor=PANEL_BG, labelcolor=DIM_TEXT,
               edgecolor='#0d3050', fontsize=7)
    _corner_brackets(ax2, color=INTERCEPT_BLU)
    _hud_label(ax2, 'VEL-002')

    ax3 = axes[1, 0]
    ax3.set_xlim(trajectory['time'].min(), trajectory['time'].max())
    ax3.set_ylim(0, trajectory['y'].max() / 1000 * 1.18)
    _apply_hud_style(ax3)
    ax3.plot(trajectory['time'], trajectory['y'] / 1000,
             color=ACCENT_GREEN, linewidth=1.4,
             path_effects=[pe.Stroke(linewidth=3, foreground=ACCENT_GREEN, alpha=0.18),
                           pe.Normal()])
    ax3.fill_between(trajectory['time'], trajectory['y'] / 1000,
                     alpha=0.05, color=ACCENT_GREEN)
    ax3.axvline(x=10, color=ACCENT_AMBER, linestyle='--', linewidth=0.8,
                label='BURNOUT t=10s')
    ax3.set_xlabel('TIME (s)')
    ax3.set_ylabel('ALTITUDE (km)')
    ax3.set_title('// ALTITUDE PROFILE')
    ax3.legend(facecolor=PANEL_BG, labelcolor=DIM_TEXT,
               edgecolor='#0d3050', fontsize=7)
    _corner_brackets(ax3, color=ACCENT_GREEN)
    _hud_label(ax3, 'ALT-003')

    ax4 = axes[1, 1]
    ax4.set_xlim(trajectory['time'].min(), trajectory['time'].max())
    vmin = min(trajectory['vx'].min(), trajectory['vy'].min()) * 1.1
    vmax = max(trajectory['vx'].max(), trajectory['vy'].max()) * 1.1
    ax4.set_ylim(vmin, vmax)
    _apply_hud_style(ax4)
    ax4.plot(trajectory['time'], trajectory['vx'],
             color='#cc44ff', linewidth=1.2, label='Vx HORIZONTAL')
    ax4.plot(trajectory['time'], trajectory['vy'],
             color='#00ddcc', linewidth=1.2, label='Vy VERTICAL')
    ax4.axvline(x=10, color=ACCENT_AMBER, linestyle='--', linewidth=0.8,
                label='BURNOUT t=10s')
    ax4.axhline(y=0, color='#1a3a55', linewidth=0.6)
    ax4.set_xlabel('TIME (s)')
    ax4.set_ylabel('VELOCITY (m/s)')
    ax4.set_title('// VELOCITY COMPONENTS')
    ax4.legend(facecolor=PANEL_BG, labelcolor=DIM_TEXT,
               edgecolor='#0d3050', fontsize=7)
    _corner_brackets(ax4, color='#cc44ff')
    _hud_label(ax4, 'VEC-004')

    fig.text(0.99, 0.01, 'BALLISTIC ANALYSIS SYSTEM  //  UNCLASSIFIED',
             color=DIM_TEXT, fontsize=6, ha='right', fontfamily='monospace')

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.28, hspace=0.55, top=0.93)
    if save:
        plt.savefig('./visuals/trajectory.png', dpi=300, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        print("Plot saved as trajectory.png")
    plt.show()


def plot_scenario(m_traj, i_traj, intercept_time=None, intercept_point=None):
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor(DARK_BG)

    ax1 = axes[0]
    ax1.set_xlim(
        min(m_traj['x'].min(), i_traj['x'].min()) / 1000 - 1,
        max(m_traj['x'].max(), i_traj['x'].max()) / 1000 + 1
    )
    ax1.set_ylim(-0.5,
                 max(m_traj['y'].max(), i_traj['y'].max()) / 1000 * 1.2)
    _apply_hud_style(ax1)

    ax1.plot(m_traj['x'] / 1000, m_traj['y'] / 1000,
             color=THREAT_RED, linewidth=1.6, label='THREAT', zorder=3,
             path_effects=[pe.Stroke(linewidth=4, foreground=THREAT_RED, alpha=0.15),
                           pe.Normal()])
    ax1.plot(i_traj['x'] / 1000, i_traj['y'] / 1000,
             color=INTERCEPT_BLU, linewidth=1.6, label='INTERCEPTOR', zorder=3,
             path_effects=[pe.Stroke(linewidth=4, foreground=INTERCEPT_BLU, alpha=0.15),
                           pe.Normal()])

    ax1.scatter(m_traj['x'].iloc[0] / 1000, m_traj['y'].iloc[0] / 1000,
                color=THREAT_RED, s=60, zorder=5, marker='^', linewidths=0)
    ax1.scatter(i_traj['x'].iloc[0] / 1000, i_traj['y'].iloc[0] / 1000,
                color=INTERCEPT_BLU, s=60, zorder=5, marker='^', linewidths=0)
    ax1.axhline(y=0, color='#1a3a55', linewidth=0.8)

    if intercept_point:
        px, py = intercept_point[0] / 1000, intercept_point[1] / 1000
        ax1.scatter(px, py, color=KILL_WHITE, s=120, zorder=6,
                    marker='x', linewidths=2,
                    label=f'ENGAGEMENT ({px:.1f} km, {py:.1f} km)')
        ring1 = plt.Circle((px, py), 0.30, color=KILL_WHITE,
                            fill=False, linewidth=0.8, linestyle='--',
                            alpha=0.5, zorder=5)
        ring2 = plt.Circle((px, py), 0.08, color=KILL_WHITE,
                            fill=False, linewidth=0.5,
                            alpha=0.3, zorder=5)
        ax1.add_patch(ring1)
        ax1.add_patch(ring2)
        ax1.annotate(f'  INTERCEPT  t={intercept_time:.1f}s',
                     xy=(px, py), color=KILL_WHITE,
                     fontsize=7, va='center', fontfamily='monospace',
                     path_effects=[pe.withStroke(linewidth=2, foreground=DARK_BG)])

    ax1.set_xlabel('HORIZONTAL DISTANCE (km)')
    ax1.set_ylabel('ALTITUDE (km)')
    ax1.set_title('// ENGAGEMENT GEOMETRY')
    ax1.legend(facecolor=PANEL_BG, labelcolor=DIM_TEXT,
               edgecolor='#0d3050', fontsize=7)
    _corner_brackets(ax1, color=THREAT_RED)
    _hud_label(ax1, 'ENG-001')

    ax2 = axes[1]
    common_times = np.intersect1d(
        np.round(m_traj['time'].values, 2),
        np.round(i_traj['time'].values, 2)
    )
    m_sync = m_traj[np.round(m_traj['time'], 2).isin(common_times)].reset_index(drop=True)
    i_sync = i_traj[np.round(i_traj['time'], 2).isin(common_times)].reset_index(drop=True)
    dist = np.sqrt((m_sync['x'] - i_sync['x'])**2 +
                   (m_sync['y'] - i_sync['y'])**2) / 1000
    ax2.set_xlim(common_times.min(), common_times.max())
    ax2.set_ylim(0, dist.max() * 1.15)
    _apply_hud_style(ax2)

    ax2.plot(common_times, dist, color=ACCENT_GREEN, linewidth=1.4,
             path_effects=[pe.Stroke(linewidth=3, foreground=ACCENT_GREEN, alpha=0.18),
                           pe.Normal()])
    ax2.fill_between(common_times, dist, alpha=0.06, color=ACCENT_GREEN)

    if intercept_time:
        ax2.axvline(x=intercept_time, color=KILL_WHITE, linestyle='--',
                    linewidth=0.9, label=f'INTERCEPT {intercept_time:.1f}s')
        ax2.axhline(y=0.03, color=ACCENT_AMBER, linestyle=':', alpha=0.7,
                    linewidth=0.8, label='KILL RADIUS 30m')
        ax2.legend(facecolor=PANEL_BG, labelcolor=DIM_TEXT,
                   edgecolor='#0d3050', fontsize=7)

    ax2.set_xlabel('TIME (s)')
    ax2.set_ylabel('SEPARATION DISTANCE (km)')
    ax2.set_title('// CLOSING DISTANCE')
    _corner_brackets(ax2, color=ACCENT_GREEN)
    _hud_label(ax2, 'CLO-002')

    fig.suptitle('[ MISSILE DEFENSE — ENGAGEMENT ASSESSMENT ]',
                 fontsize=12, fontweight='bold', color=ACCENT_GREEN,
                 fontfamily='monospace', y=1.01)
    fig.text(0.99, 0.01, 'TACTICAL DISPLAY SYSTEM  //  UNCLASSIFIED',
             color=DIM_TEXT, fontsize=6, ha='right', fontfamily='monospace')

    plt.tight_layout()
    plt.savefig('./visuals/scenario.png', dpi=300, bbox_inches='tight',
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
    fig.patch.set_facecolor(DARK_BG)

    fig.suptitle('[ MISSILE DEFENSE — LIVE ENGAGEMENT FEED ]',
                 fontsize=12, fontweight='bold', color=ACCENT_GREEN,
                 fontfamily='monospace')

    ax1 = axes[0]
    all_x = pd.concat([m_traj['x'], i_traj['x']]) / 1000
    all_y = pd.concat([m_traj['y'], i_traj['y']]) / 1000
    ax1.set_xlim(all_x.min() - 0.5, all_x.max() + 0.5)
    ax1.set_ylim(-0.3, all_y.max() * 1.2)
    _apply_hud_style(ax1)
    ax1.axhline(y=0, color='#1a3a55', linewidth=0.8)
    ax1.set_xlabel('HORIZONTAL DISTANCE (km)')
    ax1.set_ylabel('ALTITUDE (km)')
    ax1.set_title('// ENGAGEMENT GEOMETRY')
    _corner_brackets(ax1, color=THREAT_RED)
    _hud_label(ax1, 'ENG-001')

    ax1.scatter(m_traj['x'].iloc[0] / 1000, 0,
                color=THREAT_RED, s=55, marker='^', zorder=5, linewidths=0)
    ax1.scatter(i_start_x, 0,
                color=INTERCEPT_BLU, s=55, marker='s', zorder=5, linewidths=0)
    ax1.text(m_traj['x'].iloc[0] / 1000, -0.18, 'LAUNCH ORIGIN',
             color=THREAT_RED, fontsize=6, ha='center', fontfamily='monospace')
    ax1.text(i_start_x, -0.18, 'DEFENSE SITE',
             color=INTERCEPT_BLU, fontsize=6, ha='center', fontfamily='monospace')

    m_trail, = ax1.plot([], [], color=THREAT_RED, linewidth=1.4, alpha=0.85,
                        label='THREAT',
                        path_effects=[pe.Stroke(linewidth=3, foreground=THREAT_RED, alpha=0.12),
                                      pe.Normal()])
    i_trail, = ax1.plot([], [], color=INTERCEPT_BLU, linewidth=1.4, alpha=0.85,
                        label='INTERCEPTOR',
                        path_effects=[pe.Stroke(linewidth=3, foreground=INTERCEPT_BLU, alpha=0.12),
                                      pe.Normal()])
    m_dot,   = ax1.plot([], [], 'o', color=THREAT_RED, markersize=7, zorder=6,
                        markeredgecolor='#ff8888', markeredgewidth=0.5)
    i_dot,   = ax1.plot([], [], 'o', color=INTERCEPT_BLU, markersize=7, zorder=6,
                        markeredgecolor='#88ccff', markeredgewidth=0.5)
    i_static, = ax1.plot([i_start_x], [0], 's', color=INTERCEPT_BLU,
                          markersize=7, zorder=6,
                          markeredgecolor='#88ccff', markeredgewidth=0.5)

    kill_outer = Circle((0, 0), 0.40, color=KILL_WHITE, fill=False,
                         linewidth=0.9, linestyle='--', alpha=0, zorder=7)
    kill_inner = Circle((0, 0), 0.12, color=KILL_WHITE, fill=False,
                         linewidth=0.5, alpha=0, zorder=7)
    kill_cross_h, = ax1.plot([], [], color=KILL_WHITE, linewidth=1.2,
                              alpha=0, zorder=8)
    kill_cross_v, = ax1.plot([], [], color=KILL_WHITE, linewidth=1.2,
                              alpha=0, zorder=8)
    ax1.add_patch(kill_outer)
    ax1.add_patch(kill_inner)

    hit_text = ax1.text(0, 0, '', color=KILL_WHITE, fontsize=8,
                        va='bottom', fontfamily='monospace',
                        path_effects=[pe.withStroke(linewidth=2, foreground=DARK_BG)])

    status_text = ax1.text(0.02, 0.97, 'THREAT INBOUND',
                           transform=ax1.transAxes,
                           color=ACCENT_GREEN, fontsize=8, va='top',
                           fontfamily='monospace')

    ax1.legend(facecolor=PANEL_BG, labelcolor=DIM_TEXT,
               edgecolor='#0d3050', loc='upper right', fontsize=7)

    ax2 = axes[1]
    full_t_end = m_traj['time'].iloc[-1]
    ax2.set_xlim(0, full_t_end + 1)
    ax2.set_ylim(0, dist_km.max() * 1.15)
    _apply_hud_style(ax2)
    ax2.axhline(y=0.03, color=ACCENT_AMBER, linestyle=':', alpha=0.7,
                linewidth=0.8, label='KILL RADIUS 30m')
    if radar_time:
        ax2.axvline(x=radar_time, color=ACCENT_AMBER, linestyle='--',
                    alpha=0.7, linewidth=0.8,
                    label=f'RADAR LOCK t={radar_time:.1f}s')
    if launch_time:
        ax2.axvline(x=launch_time, color=INTERCEPT_BLU, linestyle='--',
                    alpha=0.7, linewidth=0.8,
                    label=f'INTERCEPT LAUNCH t={launch_time:.1f}s')
    if intercept_time:
        ax2.axvline(x=intercept_time, color=KILL_WHITE, linestyle='--',
                    alpha=0.7, linewidth=0.8,
                    label=f'ENGAGEMENT t={intercept_time:.1f}s')
    ax2.legend(facecolor=PANEL_BG, labelcolor=DIM_TEXT,
               edgecolor='#0d3050', fontsize=7)
    ax2.set_xlabel('TIME (s)')
    ax2.set_ylabel('SEPARATION DISTANCE (km)')
    ax2.set_title('// CLOSING DISTANCE')
    _corner_brackets(ax2, color=ACCENT_GREEN)
    _hud_label(ax2, 'CLO-002')

    dist_line,  = ax2.plot([], [], color=ACCENT_GREEN, linewidth=1.4,
                            path_effects=[pe.Stroke(linewidth=3, foreground=ACCENT_GREEN, alpha=0.18),
                                          pe.Normal()])
    time_cursor = ax2.axvline(x=0, color=KILL_WHITE, linewidth=0.6, alpha=0.35)

    time_text = fig.text(0.5, 0.02, 'T+0.00s', ha='center',
                         color=ACCENT_GREEN, fontsize=11,
                         fontfamily='monospace',
                         path_effects=[pe.withStroke(linewidth=2, foreground=DARK_BG)])

    fig.text(0.99, 0.01, 'TACTICAL DISPLAY SYSTEM  //  UNCLASSIFIED',
             color=DIM_TEXT, fontsize=6, ha='right', fontfamily='monospace')

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.09)

    n_total = len(m_traj)
    step    = max(1, n_total // 600)

    intercepted = [False]

    def update(frame):
        fi    = min(frame * step, n_total - 1)
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
                status_text.set_color(ACCENT_AMBER)
            elif launch_time and t_now >= launch_time:
                status = 'INTERCEPTOR AIRBORNE'
                status_text.set_color(INTERCEPT_BLU)
            else:
                status = 'THREAT INBOUND'
                status_text.set_color(THREAT_RED)
        else:
            status = 'TARGET NEUTRALIZED'
            status_text.set_color(KILL_WHITE)
        status_text.set_text(status)

        if intercept_time and t_now >= intercept_time and not intercepted[0]:
            intercepted[0] = True
            px = intercept_point[0] / 1000
            py = intercept_point[1] / 1000
            kill_outer.center = (px, py)
            kill_outer.set_alpha(0.55)
            kill_inner.center = (px, py)
            kill_inner.set_alpha(0.35)
            cs = 0.22
            kill_cross_h.set_data([px - cs, px + cs], [py, py])
            kill_cross_h.set_alpha(0.8)
            kill_cross_v.set_data([px, px], [py - cs, py + cs])
            kill_cross_v.set_alpha(0.8)
            hit_text.set_position((px + 0.35, py + 0.1))
            hit_text.set_text(f'NEUTRALIZED  T+{intercept_time:.1f}s')
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

        mask = common_times <= t_now
        if mask.any():
            dist_line.set_data(common_times[mask], dist_km[mask])
        time_cursor.set_xdata([t_now, t_now])

        time_text.set_text(f'T+{t_now:.2f}s')

        return (m_trail, i_trail, m_dot, i_dot, i_static,
                kill_outer, kill_inner, kill_cross_h, kill_cross_v,
                hit_text, status_text,
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