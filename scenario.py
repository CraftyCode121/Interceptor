import numpy as np
import pandas as pd
from missile import Missile
from interceptor import Interceptor

G     = 9.81
N     = 5    

# --- Radar & reaction parameters ---
RADAR_DETECTION_RANGE = 8000   # radar detects missile within 8km
RADAR_TRACK_TIME      = 2.0    
REACTION_TIME         = 1.5    # crew/system reaction after confirmation
MIN_DETECTION_TIME    = 3.0    

# --- Missile evasion parameters ---
EVASION_START_TIME    = 10.0
EVASION_INTERVAL_MIN  = 0.5
EVASION_INTERVAL_MAX  = 1.5
EVASION_THRUST        = 60000 
EVASION_DURATION      = 0.8
EVASION_SEED          = 42

def compute_los_rate(mx, my, ix, iy, mvx, mvy, ivx, ivy):
    """
    Compute line-of-sight rotation rate (lambda_dot).
    LOS rate = cross(r, v_rel) / range^2
    """
    rx  = mx - ix
    ry  = my - iy
    rvx = mvx - ivx
    rvy = mvy - ivy

    range_ = np.sqrt(rx**2 + ry**2)
    if range_ < 1:
        return 0.0, range_

    los_rate = (rx * rvy - ry * rvx) / (range_**2)
    return los_rate, range_


def generate_evasion_schedule(t_start, t_end, rng):
    """
    Pre-generate a list of (maneuver_time, direction) pairs.
    direction = +1 (upward kick) or -1 (downward kick)
    """
    schedule = []
    t = t_start
    while t < t_end:
        interval  = rng.uniform(EVASION_INTERVAL_MIN, EVASION_INTERVAL_MAX)
        t        += interval
        direction = rng.choice([-1, 1])
        schedule.append((t, direction))
    return schedule


def run_scenario():
    rng = np.random.default_rng(EVASION_SEED)

    missile     = Missile()
    interceptor = Interceptor()

    # --- Initial conditions: missile ---
    angle_rad = np.radians(missile.launch_angle)
    mx  = 0.0
    my  = 0.0
    mvx = missile.launch_speed * np.cos(angle_rad)
    mvy = missile.launch_speed * np.sin(angle_rad)

    # --- Initial conditions: interceptor ---
    i_angle_rad = np.radians(interceptor.launch_angle)
    ix  = interceptor.defense_x
    iy  = interceptor.defense_y
    ivx = interceptor.launch_speed * np.cos(i_angle_rad) * -1
    ivy = interceptor.launch_speed * np.sin(i_angle_rad)

    dt    = 0.05
    t     = 0.0
    t_max = 300.0

    evasion_schedule = generate_evasion_schedule(EVASION_START_TIME, 60.0, rng)
    evasion_idx      = 0       
    active_maneuver  = None   

    m_traj = []
    i_traj = []

    intercept_time       = None
    intercept_point      = None
    i_flight_time        = 0.0
    interceptor_launched = False
    radar_tracking_since = None
    launch_time          = None

    while t < t_max:

        evade_ax = 0.0
        evade_ay = 0.0

        if t >= EVASION_START_TIME:
            if (evasion_idx < len(evasion_schedule) and
                    t >= evasion_schedule[evasion_idx][0]):
                maneuver_t, direction = evasion_schedule[evasion_idx]
                active_maneuver = (t + EVASION_DURATION, direction)
                evasion_idx += 1
                print(f"[t={t:.1f}s] Missile EVADING — "
                      f"{'UP' if direction > 0 else 'DOWN'} kick")

            # Apply thrust kick if maneuver is active
            if active_maneuver and t < active_maneuver[0]:
                direction = active_maneuver[1]
                speed     = np.sqrt(mvx**2 + mvy**2)
                if speed > 0:
    
                    perp_x = -mvy / speed
                    perp_y =  mvx / speed
                    m_mass = missile.get_current_mass(t)
                    evade_ax = direction * EVASION_THRUST * perp_x / m_mass
                    evade_ay = direction * EVASION_THRUST * perp_y / m_mass

        m_mass = missile.get_current_mass(t)
        tx, ty = missile.get_thrust_vector(t, mvx, mvy)
        dx, dy = missile.get_drag_force(mvx, mvy)

        m_ax = (tx + dx) / m_mass + evade_ax
        m_ay = (ty + dy) / m_mass - G + evade_ay

        mx  += mvx * dt
        my  += mvy * dt
        mvx += m_ax * dt
        mvy += m_ay * dt

        # Radar detection logic
        if not interceptor_launched:
            dist_to_radar = np.sqrt(
                (mx - interceptor.defense_x)**2 + (my - interceptor.defense_y)**2
            )

            if dist_to_radar < RADAR_DETECTION_RANGE and t >= MIN_DETECTION_TIME:
                if radar_tracking_since is None:
                    radar_tracking_since = t
                    print(f"[t={t:.1f}s] Radar acquired missile at "
                          f"{dist_to_radar/1000:.1f} km range")

                elif t >= radar_tracking_since + RADAR_TRACK_TIME + REACTION_TIME:
                    interceptor_launched = True
                    launch_time = t
                    print(f"[t={t:.1f}s] Interceptor LAUNCHED  "
                          f"(tracked {RADAR_TRACK_TIME}s + {REACTION_TIME}s reaction)")

        if interceptor_launched:
            i_flight_time += dt

            i_mass     = interceptor.get_current_mass(i_flight_time)
            itx, ity   = interceptor.get_thrust_vector(i_flight_time, ivx, ivy)
            i_dx, i_dy = interceptor.get_drag_force(ivx, ivy)

            los_rate, range_ = compute_los_rate(mx, my, ix, iy, mvx, mvy, ivx, ivy)

            rx, ry   = mx - ix, my - iy
            rvx, rvy = mvx - ivx, mvy - ivy
            closing_vel = -(rx * rvx + ry * rvy) / (range_ + 1e-6)

            a_cmd      = N * closing_vel * los_rate
            los_angle  = np.arctan2(my - iy, mx - ix)
            perp_angle = los_angle + np.pi / 2

            ax_pn = a_cmd * np.cos(perp_angle)
            ay_pn = a_cmd * np.sin(perp_angle)

            iax = (itx + i_dx) / i_mass + ax_pn
            iay = (ity + i_dy) / i_mass - G + ay_pn

            ix  += ivx * dt
            iy  += ivy * dt
            ivx += iax * dt
            ivy += iay * dt

            # Check for intercept
            dist = np.sqrt((mx - ix)**2 + (my - iy)**2)
            if dist < 30:
                intercept_time  = t
                intercept_point = (mx, my)
                m_traj.append({'time': t, 'x': mx, 'y': my, 'vx': mvx, 'vy': mvy})
                i_traj.append({'time': t, 'x': ix, 'y': iy, 'vx': ivx, 'vy': ivy})
                print(f"[t={t:.2f}s] INTERCEPT! "
                      f"Position: ({mx/1000:.2f} km, {my/1000:.2f} km) | "
                      f"Miss distance: {dist:.1f} m")
                break

        # Stop if missile hits ground
        if my < 0 and t > 0:
            print(f"[t={t:.1f}s] MISS — Missile hit ground at x={mx/1000:.2f} km")
            break

        m_traj.append({'time': t, 'x': mx, 'y': my, 'vx': mvx, 'vy': mvy})
        if interceptor_launched:
            i_traj.append({'time': t, 'x': ix, 'y': iy, 'vx': ivx, 'vy': ivy})

        t += dt

    return (
        pd.DataFrame(m_traj),
        pd.DataFrame(i_traj),
        intercept_time,
        intercept_point,
        radar_tracking_since,
        launch_time,
    )


if __name__ == "__main__":
    m_traj, i_traj, t_hit, p_hit, t_radar, t_launch = run_scenario()

    print(f"\n--- Summary ---")
    print(f"Missile trajectory points:     {len(m_traj)}")
    print(f"Interceptor trajectory points: {len(i_traj)}")
    if t_radar:
        print(f"Radar acquisition:             t={t_radar:.1f}s")
    if t_launch:
        print(f"Interceptor launch:            t={t_launch:.1f}s")
    if t_hit:
        print(f"Successful intercept at      t={t_hit:.2f}s")
        print(f" Location: ({p_hit[0]/1000:.2f} km, {p_hit[1]/1000:.2f} km)")
    else:
        print("Intercept failed — missile evaded successfully")