from visualize import animate_scenario, run_scenario, plot_trajectory, plot_scenario
from simulator import simulate
from missile import Missile

if __name__ == "__main__":
    m_traj, i_traj, t_hit, p_hit, _, _ = run_scenario()
    plot_scenario(m_traj, i_traj, intercept_time=t_hit, intercept_point=p_hit)
    # m_traj, i_traj, t_hit, p_hit, t_radar, t_launch = run_scenario()
    # animate_scenario(m_traj, i_traj,
    #                  intercept_time=t_hit,
    #                  intercept_point=p_hit,
    #                  radar_time=t_radar,
    #                  launch_time=t_launch)