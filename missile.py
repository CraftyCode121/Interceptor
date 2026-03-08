import numpy as np

class Missile:
    def __init__(self):
        # Mass (kg)
        self.mass = 500
        self.dry_mass = 300
        
        # Engine
        self.thrust = 20000
        self.burn_time = 10
        
        # Aerodynamics
        self.drag_coeff = 0.3
        self.cross_area = 0.05
        
        # Launch
        self.launch_angle = 45
        self.launch_speed = 100

    def get_current_mass(self, t):
        """Mass decreases as fuel burns"""
        if t >= self.burn_time:
            return self.dry_mass
        
        fuel_mass = self.mass - self.dry_mass
        burn_rate = fuel_mass / self.burn_time
        return self.mass - (burn_rate * t)

    def get_thrust_vector(self, t, vx, vy):
        """Thrust only during burn, pointing in direction of motion"""
        if t >= self.burn_time:
            return 0.0, 0.0                     
        
        speed = np.sqrt(vx**2 + vy**2)
        if speed == 0:
            return 0.0, self.thrust             
        
        # thrust points in direction missile is moving
        tx = self.thrust * (vx / speed)
        ty = self.thrust * (vy / speed)
        return tx, ty

    def get_drag_force(self, vx, vy):
        """Drag opposes motion, grows with v^2"""
        rho = 1.225                              # air density kg/m^3 (sea level)
        speed = np.sqrt(vx**2 + vy**2)
        
        drag_magnitude = 0.5 * self.drag_coeff * rho * self.cross_area * speed**2
        
        if speed == 0:
            return 0.0, 0.0
        
        # drag points opposite to velocity
        dx = -drag_magnitude * (vx / speed)
        dy = -drag_magnitude * (vy / speed)
        return dx, dy