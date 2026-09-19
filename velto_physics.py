class VeltoPhysicsError(Exception):
    pass


class PhysicsBody:
    def __init__(self, x=0, y=0, mass=1.0):
        self.x = float(x)
        self.y = float(y)
        self.mass = float(mass)

        if self.mass <= 0:
            raise VeltoPhysicsError(
                "Mass must be greater than zero"
            )

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.acceleration_x = 0.0
        self.acceleration_y = 0.0

        self.gravity = 0.0
        self.friction = 0.0

    def set_gravity(self, gravity):
        self.gravity = float(gravity)

    def set_friction(self, friction):
        friction = float(friction)

        if friction < 0 or friction > 1:
            raise VeltoPhysicsError(
                "Friction must be between 0 and 1"
            )

        self.friction = friction

    def apply_force(self, force_x, force_y):
        self.acceleration_x += (
            float(force_x) / self.mass
        )

        self.acceleration_y += (
            float(force_y) / self.mass
        )

    def set_velocity(self, x, y):
        self.velocity_x = float(x)
        self.velocity_y = float(y)

    def update(self, delta):
        delta = float(delta)

        self.acceleration_y += self.gravity

        self.velocity_x += (
            self.acceleration_x * delta
        )

        self.velocity_y += (
            self.acceleration_y * delta
        )

        friction_factor = 1.0 - self.friction

        self.velocity_x *= friction_factor
        self.velocity_y *= friction_factor

        self.x += self.velocity_x * delta
        self.y += self.velocity_y * delta

        self.acceleration_x = 0.0
        self.acceleration_y = 0.0

    def position(self):
        return {
            "x": self.x,
            "y": self.y
        }

    def velocity(self):
        return {
            "x": self.velocity_x,
            "y": self.velocity_y
        }

    def info(self):
        return {
            "x": self.x,
            "y": self.y,
            "mass": self.mass,
            "velocity_x": self.velocity_x,
            "velocity_y": self.velocity_y,
            "gravity": self.gravity,
            "friction": self.friction
        }
