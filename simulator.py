import numpy as np
from scipy.integrate import solve_ivp
import pandas as pd
from missile import Missile

# gravity constant
G = 9.81 

def equations_of_motion(t, state, missile):
    """
    This function describes HOW the state changes at every instant.
    scipy will call this hundreds of times to integrate the trajectory.
    
    state = [x, y, vx, vy]
    returns = [dx/dt, dy/dt, dvx/dt, dvy/dt]
             = [vx, vy, ax, ay]
    """
    x, y, vx, vy = state

    if y < 0:
        return [0, 0, 0, 0]

    # get current mass
    mass = missile.get_current_mass(t)

    # get all forces
    tx, ty = missile.get_thrust_vector(t, vx, vy)
    dx, dy = missile.get_drag_force(vx, vy)

    ax = (tx + dx) / mass
    ay = (ty + dy) / mass - G    

    # return derivatives of state
    # [how x changes, how y changes, how vx changes, how vy changes]
    return [vx, vy, ax, ay]


def simulate(missile):
    """
    Runs the full flight simulation for one missile.
    Returns a dataframe of the trajectory.
    """

    # --- Initial conditions ---
    angle_rad = np.radians(missile.launch_angle)
    vx0 = missile.launch_speed * np.cos(angle_rad)
    vy0 = missile.launch_speed * np.sin(angle_rad)
    
    initial_state = [0, 0, vx0, vy0]   

    # --- Time range ---
    t_span = (0, 300)                 
    t_eval = np.arange(0, 300, 0.1)    

    # --- Run the solver ---
    solution = solve_ivp(
        fun=lambda t, s: equations_of_motion(t, s, missile),
        t_span=t_span,
        y0=initial_state,
        t_eval=t_eval,
        max_step=0.1                    
    )

    # --- Package results into a dataframe ---
    df = pd.DataFrame({
        'time': solution.t,
        'x':    solution.y[0],
        'y':    solution.y[1],
        'vx':   solution.y[2],
        'vy':   solution.y[3],
    })

    # --- Cut off when missile hits ground (y < 0) ---
    df = df[df['y'] >= 0].reset_index(drop=True)

    return df


if __name__ == "__main__":
    m = Missile()
    trajectory = simulate(m)
    
    print(trajectory.head(10))         
    print(f"\nMax height: {trajectory['y'].max():.1f} m")
    print(f"Total range: {trajectory['x'].max():.1f} m")
    print(f"Flight time: {trajectory['time'].max():.1f} s")