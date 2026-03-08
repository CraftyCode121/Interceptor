import numpy as np

class Interceptor:
    def __init__(self):
        # Mass (kg)
        self.mass = 300
        self.dry_mass = 200
        
        # Engine
        self.thrust = 40000
        self.burn_time = 8
        
        # Aerodynamics
        self.drag_coeff = 0.2
        self.cross_area = 0.03
        
        # Launch
        self.launch_angle = 70
        self.launch_speed = 50
        
        # Position
        self.defense_x = 10000
        self.defense_y = 0

    def get_current_mass(self, t):
        if t >= self.burn_time:
            return self.dry_mass
        fuel_mass = self.mass - self.dry_mass
        burn_rate = fuel_mass / self.burn_time
        return self.mass - (burn_rate * t)

    def get_thrust_vector(self, t, vx, vy):
        if t >= self.burn_time:
            return 0.0, 0.0
        speed = np.sqrt(vx**2 + vy**2)
        if speed == 0:
            return 0.0, self.thrust
        tx = self.thrust * (vx / speed)
        ty = self.thrust * (vy / speed)
        return tx, ty

    def get_drag_force(self, vx, vy):
        rho = 1.225
        speed = np.sqrt(vx**2 + vy**2)
        drag_magnitude = 0.5 * self.drag_coeff * rho * self.cross_area * speed**2
        if speed == 0:
            return 0.0, 0.0
        dx = -drag_magnitude * (vx / speed)
        dy = -drag_magnitude * (vy / speed)
        return dx, dy

    def get_initial_velocity(self):
        angle_rad = np.radians(self.launch_angle)
        vx0 = self.launch_speed * np.cos(angle_rad)
        vy0 = self.launch_speed * np.sin(angle_rad)
        return vx0, vy0
