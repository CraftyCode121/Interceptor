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
    plt.rcParams.update({'savefig.dpi': 300, 'figure.dpi': 150, 'font.size': 9})
    fig, axes = plt.subplots(2, 2, figsize=(18, 13))
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


def plot_scenario(m_traj, i_traj, intercept_time=None, intercept_point=None,
                  radar_time=None, launch_time=None):
    plt.rcParams.update({'savefig.dpi': 300, 'figure.dpi': 150, 'font.size': 9})

    # ── Pre-compute derived channels (same as animate_scenario) ───────────────
    full_t   = m_traj['time'].values
    m_speed  = np.sqrt(m_traj['vx'].values**2 + m_traj['vy'].values**2)
    MACH_SPD = 343.0
    m_mach   = m_speed / MACH_SPD
    m_ax_arr = np.gradient(m_traj['vx'].values, full_t)
    m_ay_arr = np.gradient(m_traj['vy'].values, full_t)
    m_gforce = np.sqrt(m_ax_arr**2 + (m_ay_arr + 9.81)**2) / 9.81
    m_alt_km = m_traj['y'].values / 1000
    full_t_end = m_traj['time'].iloc[-1]

    common_times = np.intersect1d(
        np.round(m_traj['time'].values, 2),
        np.round(i_traj['time'].values, 2)
    )
    m_sync = m_traj[np.round(m_traj['time'], 2).isin(common_times)].reset_index(drop=True)
    i_sync = i_traj[np.round(i_traj['time'], 2).isin(common_times)].reset_index(drop=True)
    n = min(len(m_sync), len(i_sync))
    m_sync = m_sync.iloc[:n]
    i_sync = i_sync.iloc[:n]
    common_times = common_times[:n]
    dist_km = np.sqrt((m_sync['x'].values - i_sync['x'].values)**2 +
                      (m_sync['y'].values - i_sync['y'].values)**2) / 1000

    # ── Figure: identical GridSpec to animate_scenario ────────────────────────
    fig = plt.figure(figsize=(26, 12))
    fig.patch.set_facecolor(DARK_BG)

    gs = fig.add_gridspec(
        4, 2,
        left=0.04, right=0.98,
        top=0.91, bottom=0.07,
        wspace=0.32, hspace=0.55,
        width_ratios=[1.55, 1],
        height_ratios=[1, 1, 1, 1]
    )

    ax_map  = fig.add_subplot(gs[:, 0])
    ax_alt  = fig.add_subplot(gs[0, 1])
    ax_mach = fig.add_subplot(gs[1, 1])
    ax_gee  = fig.add_subplot(gs[2, 1])
    ax_clo  = fig.add_subplot(gs[3, 1])

    fig.suptitle('[ MISSILE DEFENSE — ENGAGEMENT ASSESSMENT ]',
                 fontsize=14, fontweight='bold', color=ACCENT_GREEN,
                 fontfamily='monospace', y=0.97)

    i_start_x = i_traj['x'].iloc[0] / 1000

    # ── MAP ───────────────────────────────────────────────────────────────────
    all_x = pd.concat([m_traj['x'], i_traj['x']]) / 1000
    all_y = pd.concat([m_traj['y'], i_traj['y']]) / 1000
    ax_map.set_xlim(all_x.min() - 0.5, all_x.max() + 0.5)
    ax_map.set_ylim(-0.4, all_y.max() * 1.22)
    _apply_hud_style(ax_map)
    ax_map.axhline(y=0, color='#1a3a55', linewidth=0.8)
    ax_map.set_xlabel('HORIZONTAL DISTANCE (km)')
    ax_map.set_ylabel('ALTITUDE (km)')
    ax_map.set_title('// ENGAGEMENT GEOMETRY', fontsize=11)
    _corner_brackets(ax_map, color=THREAT_RED, size=0.025)
    _hud_label(ax_map, 'ENG-001')

    ax_map.plot(m_traj['x'] / 1000, m_traj['y'] / 1000,
                color=THREAT_RED, linewidth=1.8, label='THREAT', zorder=3,
                path_effects=[pe.Stroke(linewidth=5, foreground=THREAT_RED, alpha=0.15),
                              pe.Normal()])
    ax_map.plot(i_traj['x'] / 1000, i_traj['y'] / 1000,
                color=INTERCEPT_BLU, linewidth=1.8, label='INTERCEPTOR', zorder=3,
                path_effects=[pe.Stroke(linewidth=5, foreground=INTERCEPT_BLU, alpha=0.15),
                              pe.Normal()])

    ax_map.scatter(m_traj['x'].iloc[0] / 1000, 0,
                   color=THREAT_RED, s=70, marker='^', zorder=5, linewidths=0)
    ax_map.scatter(i_start_x, 0,
                   color=INTERCEPT_BLU, s=70, marker='s', zorder=5, linewidths=0)
    ax_map.text(m_traj['x'].iloc[0] / 1000, -0.28, 'LAUNCH ORIGIN',
                color=THREAT_RED, fontsize=7, ha='center', fontfamily='monospace')
    ax_map.text(i_start_x, -0.28, 'DEFENSE SITE',
                color=INTERCEPT_BLU, fontsize=7, ha='center', fontfamily='monospace')

    if intercept_point:
        px, py = intercept_point[0] / 1000, intercept_point[1] / 1000
        kill_outer = plt.Circle((px, py), 0.40, color=KILL_WHITE, fill=False,
                                 linewidth=1.0, linestyle='--', alpha=0.55, zorder=7)
        kill_inner = plt.Circle((px, py), 0.12, color=KILL_WHITE, fill=False,
                                 linewidth=0.6, alpha=0.35, zorder=7)
        ax_map.add_patch(kill_outer)
        ax_map.add_patch(kill_inner)
        cs = 0.22
        ax_map.plot([px - cs, px + cs], [py, py], color=KILL_WHITE,
                    linewidth=1.2, alpha=0.8, zorder=8)
        ax_map.plot([px, px], [py - cs, py + cs], color=KILL_WHITE,
                    linewidth=1.2, alpha=0.8, zorder=8)
        ax_map.text(px + 0.35, py + 0.1,
                    f'NEUTRALIZED  T+{intercept_time:.1f}s',
                    color=KILL_WHITE, fontsize=8, va='bottom',
                    fontfamily='monospace',
                    path_effects=[pe.withStroke(linewidth=2, foreground=DARK_BG)])

    ax_map.text(0.02, 0.97, 'TARGET NEUTRALIZED',
                transform=ax_map.transAxes, color=KILL_WHITE,
                fontsize=10, va='top', fontfamily='monospace', fontweight='bold')
    ax_map.legend(facecolor=PANEL_BG, labelcolor=DIM_TEXT,
                  edgecolor='#0d3050', loc='upper right', fontsize=8)

    # ── ALT ───────────────────────────────────────────────────────────────────
    ax_alt.set_xlim(0, full_t_end + 1)
    ax_alt.set_ylim(0, m_alt_km.max() * 1.2)
    _apply_hud_style(ax_alt)
    ax_alt.set_ylabel('ALT (km)', fontsize=8)
    ax_alt.set_title('// ALTITUDE', fontsize=9)
    _corner_brackets(ax_alt, color=ACCENT_GREEN, size=0.06)
    _hud_label(ax_alt, 'ALT-002')
    ax_alt.tick_params(labelbottom=False)
    ax_alt.plot(full_t, m_alt_km, color=ACCENT_GREEN, linewidth=1.4,
                path_effects=[pe.Stroke(linewidth=3, foreground=ACCENT_GREEN, alpha=0.18),
                              pe.Normal()])
    ax_alt.fill_between(full_t, m_alt_km, alpha=0.06, color=ACCENT_GREEN)
    if intercept_time:
        ax_alt.axvline(x=intercept_time, color=KILL_WHITE, linestyle='--',
                       linewidth=0.8, alpha=0.6)
    ax_alt.text(0.97, 0.93, f'{m_alt_km.max():.2f} km PEAK',
                transform=ax_alt.transAxes, color=ACCENT_GREEN,
                fontsize=8, ha='right', fontfamily='monospace', va='top')

    # ── MACH ──────────────────────────────────────────────────────────────────
    ax_mach.set_xlim(0, full_t_end + 1)
    ax_mach.set_ylim(0, m_mach.max() * 1.2)
    _apply_hud_style(ax_mach)
    ax_mach.set_ylabel('MACH', fontsize=8)
    ax_mach.set_title('// SPEED / MACH', fontsize=9)
    _corner_brackets(ax_mach, color=INTERCEPT_BLU, size=0.06)
    _hud_label(ax_mach, 'SPD-003')
    ax_mach.tick_params(labelbottom=False)
    for m_lvl in [1.0, 2.0, 3.0, 4.0, 5.0]:
        if m_lvl < m_mach.max() * 1.1:
            ax_mach.axhline(y=m_lvl, color='#1a3a55', linewidth=0.5,
                            linestyle=':', alpha=0.8)
            ax_mach.text(full_t_end * 0.02, m_lvl + m_mach.max() * 0.015,
                         f'M{m_lvl:.0f}', color='#2a5070', fontsize=6,
                         fontfamily='monospace')
    ax_mach.plot(full_t, m_mach, color=INTERCEPT_BLU, linewidth=1.4,
                 path_effects=[pe.Stroke(linewidth=3, foreground=INTERCEPT_BLU, alpha=0.18),
                               pe.Normal()])
    if intercept_time:
        ax_mach.axvline(x=intercept_time, color=KILL_WHITE, linestyle='--',
                        linewidth=0.8, alpha=0.6)
    ax_mach.text(0.97, 0.93, f'M {m_mach.max():.2f} PEAK',
                 transform=ax_mach.transAxes, color=INTERCEPT_BLU,
                 fontsize=8, ha='right', fontfamily='monospace', va='top')

    # ── G-FORCE ───────────────────────────────────────────────────────────────
    gmax = max(m_gforce.max() * 1.2, 5)
    ax_gee.set_xlim(0, full_t_end + 1)
    ax_gee.set_ylim(0, gmax)
    _apply_hud_style(ax_gee)
    ax_gee.set_ylabel('G-LOAD', fontsize=8)
    ax_gee.set_title('// G-FORCE', fontsize=9)
    _corner_brackets(ax_gee, color=ACCENT_AMBER, size=0.06)
    _hud_label(ax_gee, 'ACC-004')
    ax_gee.tick_params(labelbottom=False)
    for g_lvl in [1, 5, 10, 20, 30]:
        if g_lvl < gmax:
            ax_gee.axhline(y=g_lvl, color='#1a3a55', linewidth=0.5,
                           linestyle=':', alpha=0.8)
            ax_gee.text(full_t_end * 0.02, g_lvl + gmax * 0.015,
                        f'{g_lvl}G', color='#2a5070', fontsize=6,
                        fontfamily='monospace')
    ax_gee.plot(full_t, m_gforce, color=ACCENT_AMBER, linewidth=1.4,
                path_effects=[pe.Stroke(linewidth=3, foreground=ACCENT_AMBER, alpha=0.18),
                              pe.Normal()])
    if intercept_time:
        ax_gee.axvline(x=intercept_time, color=KILL_WHITE, linestyle='--',
                       linewidth=0.8, alpha=0.6)
    ax_gee.text(0.97, 0.93, f'{m_gforce.max():.1f} G PEAK',
                transform=ax_gee.transAxes, color=ACCENT_AMBER,
                fontsize=8, ha='right', fontfamily='monospace', va='top')

    # ── CLOSING DIST ──────────────────────────────────────────────────────────
    ax_clo.set_xlim(0, full_t_end + 1)
    ax_clo.set_ylim(0, dist_km.max() * 1.15)
    _apply_hud_style(ax_clo)
    ax_clo.set_xlabel('TIME (s)', fontsize=8)
    ax_clo.set_ylabel('SEP (km)', fontsize=8)
    ax_clo.set_title('// CLOSING DISTANCE', fontsize=9)
    _corner_brackets(ax_clo, color='#cc44ff', size=0.06)
    _hud_label(ax_clo, 'CLO-005')
    ax_clo.axhline(y=0.03, color=ACCENT_AMBER, linestyle=':', alpha=0.7,
                   linewidth=0.8)
    ax_clo.text(full_t_end * 0.02, 0.035, 'KILL RAD',
                color=ACCENT_AMBER, fontsize=6, fontfamily='monospace')
    if radar_time:
        ax_clo.axvline(x=radar_time, color=ACCENT_AMBER, linestyle='--',
                       alpha=0.6, linewidth=0.7)
    if launch_time:
        ax_clo.axvline(x=launch_time, color=INTERCEPT_BLU, linestyle='--',
                       alpha=0.6, linewidth=0.7)
    if intercept_time:
        ax_clo.axvline(x=intercept_time, color=KILL_WHITE, linestyle='--',
                       alpha=0.6, linewidth=0.7)
    ax_clo.plot(common_times, dist_km, color='#cc44ff', linewidth=1.4,
                path_effects=[pe.Stroke(linewidth=3, foreground='#cc44ff', alpha=0.18),
                              pe.Normal()])
    ax_clo.fill_between(common_times, dist_km, alpha=0.06, color='#cc44ff')
    if len(dist_km):
        ax_clo.text(0.97, 0.93, f'{dist_km.min():.3f} km MIN',
                    transform=ax_clo.transAxes, color='#cc44ff',
                    fontsize=8, ha='right', fontfamily='monospace', va='top')

    fig.text(0.5, 0.015, f'T+{full_t_end:.2f}s  //  ENGAGEMENT COMPLETE',
             ha='center', color=ACCENT_GREEN, fontsize=11,
             fontfamily='monospace',
             path_effects=[pe.withStroke(linewidth=2, foreground=DARK_BG)])
    fig.text(0.99, 0.01, 'TACTICAL DISPLAY SYSTEM  //  UNCLASSIFIED',
             color=DIM_TEXT, fontsize=7, ha='right', fontfamily='monospace')

    plt.savefig('./visuals/scenario.png', dpi=300, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    print("Saved scenario.png")
    plt.show()


def animate_scenario(m_traj, i_traj, intercept_time=None, intercept_point=None,
                     radar_time=None, launch_time=None):
    plt.rcParams.update({'savefig.dpi': 60, 'figure.dpi': 60, 'font.size': 11})

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

    # ── Pre-compute derived channels ──────────────────────────────────────────
    full_t   = m_traj['time'].values
    full_dt  = np.diff(full_t, prepend=full_t[0])
    full_dt  = np.where(full_dt == 0, 1e-9, full_dt)

    m_speed  = np.sqrt(m_traj['vx'].values**2 + m_traj['vy'].values**2)
    MACH_SPD = 343.0
    m_mach   = m_speed / MACH_SPD

    m_ax     = np.gradient(m_traj['vx'].values, full_t)
    m_ay     = np.gradient(m_traj['vy'].values, full_t)
    m_gforce = np.sqrt(m_ax**2 + (m_ay + 9.81)**2) / 9.81

    m_alt_km = m_traj['y'].values / 1000

    ddist    = np.gradient(dist_km, common_times) if len(dist_km) > 1 else np.zeros_like(dist_km)

    full_t_end = m_traj['time'].iloc[-1]

    # ── Figure: GridSpec — left wide map + right 4-strip sidebar ─────────────
    fig = plt.figure(figsize=(32, 18))
    fig.patch.set_facecolor(DARK_BG)

    gs = fig.add_gridspec(
        4, 2,
        left=0.04, right=0.98,
        top=0.91, bottom=0.07,
        wspace=0.32, hspace=0.55,
        width_ratios=[1.55, 1],
        height_ratios=[1, 1, 1, 1]
    )

    ax_map = fig.add_subplot(gs[:, 0])

    ax_alt  = fig.add_subplot(gs[0, 1])
    ax_mach = fig.add_subplot(gs[1, 1])
    ax_gee  = fig.add_subplot(gs[2, 1])
    ax_clo  = fig.add_subplot(gs[3, 1])

    fig.suptitle('[ MISSILE DEFENSE — LIVE ENGAGEMENT FEED ]',
                 fontsize=18, fontweight='bold', color=ACCENT_GREEN,
                 fontfamily='monospace', y=0.97)

    # ── MAP panel ─────────────────────────────────────────────────────────────
    all_x = pd.concat([m_traj['x'], i_traj['x']]) / 1000
    all_y = pd.concat([m_traj['y'], i_traj['y']]) / 1000
    ax_map.set_xlim(all_x.min() - 0.5, all_x.max() + 0.5)
    ax_map.set_ylim(-0.4, all_y.max() * 1.22)
    _apply_hud_style(ax_map)
    ax_map.axhline(y=0, color='#1a3a55', linewidth=0.8)
    ax_map.set_xlabel('HORIZONTAL DISTANCE (km)', fontsize=11)
    ax_map.set_ylabel('ALTITUDE (km)', fontsize=11)
    ax_map.set_title('// ENGAGEMENT GEOMETRY', fontsize=13)
    _corner_brackets(ax_map, color=THREAT_RED, size=0.025)
    _hud_label(ax_map, 'ENG-001')

    ax_map.scatter(m_traj['x'].iloc[0] / 1000, 0,
                   color=THREAT_RED, s=55, marker='^', zorder=5, linewidths=0)
    ax_map.scatter(i_start_x, 0,
                   color=INTERCEPT_BLU, s=55, marker='s', zorder=5, linewidths=0)
    ax_map.text(m_traj['x'].iloc[0] / 1000, -0.28, 'LAUNCH ORIGIN',
                color=THREAT_RED, fontsize=9, ha='center', fontfamily='monospace')
    ax_map.text(i_start_x, -0.28, 'DEFENSE SITE',
                color=INTERCEPT_BLU, fontsize=9, ha='center', fontfamily='monospace')

    m_trail, = ax_map.plot([], [], color=THREAT_RED, linewidth=1.5, alpha=0.85,
                           label='THREAT',
                           path_effects=[pe.Stroke(linewidth=4, foreground=THREAT_RED, alpha=0.12),
                                         pe.Normal()])
    i_trail, = ax_map.plot([], [], color=INTERCEPT_BLU, linewidth=1.5, alpha=0.85,
                           label='INTERCEPTOR',
                           path_effects=[pe.Stroke(linewidth=4, foreground=INTERCEPT_BLU, alpha=0.12),
                                         pe.Normal()])
    m_dot,    = ax_map.plot([], [], 'o', color=THREAT_RED, markersize=8, zorder=6,
                            markeredgecolor='#ff8888', markeredgewidth=0.5)
    i_dot,    = ax_map.plot([], [], 'o', color=INTERCEPT_BLU, markersize=8, zorder=6,
                            markeredgecolor='#88ccff', markeredgewidth=0.5)
    i_static, = ax_map.plot([i_start_x], [0], 's', color=INTERCEPT_BLU,
                             markersize=8, zorder=6,
                             markeredgecolor='#88ccff', markeredgewidth=0.5)

    kill_outer = Circle((0, 0), 0.40, color=KILL_WHITE, fill=False,
                         linewidth=0.9, linestyle='--', alpha=0, zorder=7)
    kill_inner = Circle((0, 0), 0.12, color=KILL_WHITE, fill=False,
                         linewidth=0.5, alpha=0, zorder=7)
    kill_cross_h, = ax_map.plot([], [], color=KILL_WHITE, linewidth=1.2,
                                 alpha=0, zorder=8)
    kill_cross_v, = ax_map.plot([], [], color=KILL_WHITE, linewidth=1.2,
                                 alpha=0, zorder=8)
    ax_map.add_patch(kill_outer)
    ax_map.add_patch(kill_inner)

    hit_text = ax_map.text(0, 0, '', color=KILL_WHITE, fontsize=8,
                           va='bottom', fontfamily='monospace',
                           path_effects=[pe.withStroke(linewidth=2, foreground=DARK_BG)])

    status_text = ax_map.text(0.02, 0.97, 'THREAT INBOUND',
                              transform=ax_map.transAxes,
                              color=THREAT_RED, fontsize=9, va='top',
                              fontfamily='monospace', fontweight='bold')

    ax_map.legend(facecolor=PANEL_BG, labelcolor=DIM_TEXT,
                  edgecolor='#0d3050', loc='upper right', fontsize=10)

    # ── SIDEBAR — ALT ─────────────────────────────────────────────────────────
    ax_alt.set_xlim(0, full_t_end + 1)
    ax_alt.set_ylim(0, m_alt_km.max() * 1.2)
    _apply_hud_style(ax_alt)
    ax_alt.set_ylabel('ALT (km)', fontsize=10)
    ax_alt.set_title('// ALTITUDE', fontsize=11)
    _corner_brackets(ax_alt, color=ACCENT_GREEN, size=0.06)
    _hud_label(ax_alt, 'ALT-002')
    ax_alt.tick_params(labelbottom=False)

    alt_line, = ax_alt.plot([], [], color=ACCENT_GREEN, linewidth=1.6,
                             path_effects=[pe.Stroke(linewidth=4, foreground=ACCENT_GREEN, alpha=0.18),
                                           pe.Normal()])
    alt_fill  = ax_alt.fill_between([], [], alpha=0)
    alt_dot,  = ax_alt.plot([], [], 'o', color=ACCENT_GREEN, markersize=7, zorder=5)
    alt_val   = ax_alt.text(0.97, 0.93, '', transform=ax_alt.transAxes,
                             color=ACCENT_GREEN, fontsize=11, ha='right',
                             fontfamily='monospace', va='top')
    alt_cur   = ax_alt.axvline(x=0, color=KILL_WHITE, linewidth=0.7, alpha=0.3)

    # ── SIDEBAR — MACH ────────────────────────────────────────────────────────
    ax_mach.set_xlim(0, full_t_end + 1)
    ax_mach.set_ylim(0, m_mach.max() * 1.2)
    _apply_hud_style(ax_mach)
    ax_mach.set_ylabel('MACH', fontsize=10)
    ax_mach.set_title('// SPEED / MACH', fontsize=11)
    _corner_brackets(ax_mach, color=INTERCEPT_BLU, size=0.06)
    _hud_label(ax_mach, 'SPD-003')
    ax_mach.tick_params(labelbottom=False)
    for m_lvl in [1.0, 2.0, 3.0, 4.0, 5.0]:
        if m_lvl < m_mach.max() * 1.1:
            ax_mach.axhline(y=m_lvl, color='#1a3a55', linewidth=0.5,
                            linestyle=':', alpha=0.8)
            ax_mach.text(full_t_end * 0.02, m_lvl + m_mach.max() * 0.015,
                         f'M{m_lvl:.0f}', color='#2a5070', fontsize=8,
                         fontfamily='monospace')

    mach_line, = ax_mach.plot([], [], color=INTERCEPT_BLU, linewidth=1.6,
                               path_effects=[pe.Stroke(linewidth=4, foreground=INTERCEPT_BLU, alpha=0.18),
                                             pe.Normal()])
    mach_dot,  = ax_mach.plot([], [], 'o', color=INTERCEPT_BLU, markersize=7, zorder=5)
    mach_val   = ax_mach.text(0.97, 0.93, '', transform=ax_mach.transAxes,
                               color=INTERCEPT_BLU, fontsize=11, ha='right',
                               fontfamily='monospace', va='top')
    mach_cur   = ax_mach.axvline(x=0, color=KILL_WHITE, linewidth=0.7, alpha=0.3)

    # ── SIDEBAR — G-FORCE ─────────────────────────────────────────────────────
    ax_gee.set_xlim(0, full_t_end + 1)
    gmax = max(m_gforce.max() * 1.2, 5)
    ax_gee.set_ylim(0, gmax)
    _apply_hud_style(ax_gee)
    ax_gee.set_ylabel('G-LOAD', fontsize=10)
    ax_gee.set_title('// G-FORCE', fontsize=11)
    _corner_brackets(ax_gee, color=ACCENT_AMBER, size=0.06)
    _hud_label(ax_gee, 'ACC-004')
    ax_gee.tick_params(labelbottom=False)
    for g_lvl in [1, 5, 10, 20, 30]:
        if g_lvl < gmax:
            ax_gee.axhline(y=g_lvl, color='#1a3a55', linewidth=0.5,
                           linestyle=':', alpha=0.8)
            ax_gee.text(full_t_end * 0.02, g_lvl + gmax * 0.015,
                        f'{g_lvl}G', color='#2a5070', fontsize=8,
                        fontfamily='monospace')

    gee_line, = ax_gee.plot([], [], color=ACCENT_AMBER, linewidth=1.6,
                             path_effects=[pe.Stroke(linewidth=4, foreground=ACCENT_AMBER, alpha=0.18),
                                           pe.Normal()])
    gee_dot,  = ax_gee.plot([], [], 'o', color=ACCENT_AMBER, markersize=7, zorder=5)
    gee_val   = ax_gee.text(0.97, 0.93, '', transform=ax_gee.transAxes,
                             color=ACCENT_AMBER, fontsize=11, ha='right',
                             fontfamily='monospace', va='top')
    gee_cur   = ax_gee.axvline(x=0, color=KILL_WHITE, linewidth=0.7, alpha=0.3)

    # ── SIDEBAR — CLOSING DIST ────────────────────────────────────────────────
    ax_clo.set_xlim(0, full_t_end + 1)
    ax_clo.set_ylim(0, dist_km.max() * 1.15)
    _apply_hud_style(ax_clo)
    ax_clo.set_xlabel('TIME (s)', fontsize=10)
    ax_clo.set_ylabel('SEP (km)', fontsize=10)
    ax_clo.set_title('// CLOSING DISTANCE', fontsize=11)
    _corner_brackets(ax_clo, color='#cc44ff', size=0.06)
    _hud_label(ax_clo, 'CLO-005')
    ax_clo.axhline(y=0.03, color=ACCENT_AMBER, linestyle=':', alpha=0.7,
                   linewidth=0.8)
    ax_clo.text(full_t_end * 0.02, 0.035, 'KILL RAD',
                color=ACCENT_AMBER, fontsize=8, fontfamily='monospace')
    if radar_time:
        ax_clo.axvline(x=radar_time, color=ACCENT_AMBER, linestyle='--',
                       alpha=0.6, linewidth=0.7)
    if launch_time:
        ax_clo.axvline(x=launch_time, color=INTERCEPT_BLU, linestyle='--',
                       alpha=0.6, linewidth=0.7)
    if intercept_time:
        ax_clo.axvline(x=intercept_time, color=KILL_WHITE, linestyle='--',
                       alpha=0.6, linewidth=0.7)

    clo_line, = ax_clo.plot([], [], color='#cc44ff', linewidth=1.6,
                             path_effects=[pe.Stroke(linewidth=4, foreground='#cc44ff', alpha=0.18),
                                           pe.Normal()])
    clo_dot,  = ax_clo.plot([], [], 'o', color='#cc44ff', markersize=7, zorder=5)
    clo_val   = ax_clo.text(0.97, 0.93, '', transform=ax_clo.transAxes,
                             color='#cc44ff', fontsize=11, ha='right',
                             fontfamily='monospace', va='top')
    clo_cur   = ax_clo.axvline(x=0, color=KILL_WHITE, linewidth=0.7, alpha=0.3)

    # ── Bottom bar ────────────────────────────────────────────────────────────
    time_text = fig.text(0.5, 0.015, 'T+0.00s', ha='center',
                         color=ACCENT_GREEN, fontsize=16,
                         fontfamily='monospace',
                         path_effects=[pe.withStroke(linewidth=2, foreground=DARK_BG)])
    fig.text(0.99, 0.01, 'TACTICAL DISPLAY SYSTEM  //  UNCLASSIFIED',
             color=DIM_TEXT, fontsize=9, ha='right', fontfamily='monospace')

    n_total = len(m_traj)
    step    = max(1, n_total // 600)

    intercepted = [False]

    def update(frame):
        fi    = min(frame * step, n_total - 1)
        t_now = float(m_traj['time'].iloc[fi])

        # MAP — missile trail
        mx = m_traj['x'].iloc[:fi + 1] / 1000
        my = m_traj['y'].iloc[:fi + 1] / 1000
        m_trail.set_data(mx.values, my.values)
        m_dot.set_data([mx.iloc[-1]], [my.iloc[-1]])

        # MAP — interceptor trail
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

        # MAP — status label
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

        # MAP — intercept flash
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
            i_trail.set_data(i_traj['x'].values / 1000, i_traj['y'].values / 1000)
            m_trail.set_data(m_traj['x'].values / 1000, m_traj['y'].values / 1000)

        # SIDEBAR — altitude
        t_mask = full_t <= t_now
        t_vis  = full_t[t_mask]
        if t_mask.any():
            alt_line.set_data(t_vis, m_alt_km[t_mask])
            alt_dot.set_data([t_vis[-1]], [m_alt_km[t_mask][-1]])
            alt_val.set_text(f'{m_alt_km[t_mask][-1]:.2f} km')
        alt_cur.set_xdata([t_now, t_now])

        # SIDEBAR — mach
        if t_mask.any():
            mach_line.set_data(t_vis, m_mach[t_mask])
            mach_dot.set_data([t_vis[-1]], [m_mach[t_mask][-1]])
            mach_val.set_text(f'M {m_mach[t_mask][-1]:.2f}')
        mach_cur.set_xdata([t_now, t_now])

        # SIDEBAR — g-force
        if t_mask.any():
            gee_line.set_data(t_vis, m_gforce[t_mask])
            gee_dot.set_data([t_vis[-1]], [m_gforce[t_mask][-1]])
            gee_val.set_text(f'{m_gforce[t_mask][-1]:.1f} G')
        gee_cur.set_xdata([t_now, t_now])

        # SIDEBAR — closing distance
        c_mask = common_times <= t_now
        if c_mask.any():
            clo_line.set_data(common_times[c_mask], dist_km[c_mask])
            clo_dot.set_data([common_times[c_mask][-1]], [dist_km[c_mask][-1]])
            clo_val.set_text(f'{dist_km[c_mask][-1]:.2f} km')
        clo_cur.set_xdata([t_now, t_now])

        time_text.set_text(f'T+{t_now:.2f}s')

        return (m_trail, i_trail, m_dot, i_dot, i_static,
                kill_outer, kill_inner, kill_cross_h, kill_cross_v,
                hit_text, status_text,
                alt_line, alt_dot, alt_val, alt_cur,
                mach_line, mach_dot, mach_val, mach_cur,
                gee_line, gee_dot, gee_val, gee_cur,
                clo_line, clo_dot, clo_val, clo_cur,
                time_text)

    total_frames = (n_total + step - 1) // step
    ani = animation.FuncAnimation(
        fig, update, frames=total_frames, interval=30, blit=True
    )

    Writer = animation.FFMpegWriter(
        fps=30, bitrate=8000,
        extra_args=['-vcodec', 'libx264', '-crf', '18',
                    '-preset', 'slow', '-pix_fmt', 'yuv420p',
                    '-vf', 'scale=1920:1080:flags=lanczos']
    )
    ani.save('./visuals/scenario_animation.mp4', writer=Writer,
             dpi=60, savefig_kwargs={'facecolor': fig.get_facecolor()})
    print("Saved scenario_animation.mp4")
    plt.close(fig)
    return ani