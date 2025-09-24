import pygame
import random

# Sim constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_COLOUR = (0, 0, 0)
FPS = 60

# Boid constants
NUMBER_OF_BOIDS = 30
BOID_SIZE = 5
GENERATION_MARGIN = 12 # The larger the number, the smaller the margin
BOID_COLOUR = (255, 255, 255)
LINEAR_VISUAL_RANGE = 100
LINEAR_PROTECTED_RANGE = 60
MAX_SPEED = 3
MAX_ACC_REQUEST = 0.3
SEPERATION_FACTOR = 2
MATCHING_FACTOR = 0.001
CENTERING_FACTOR = 0.00001

class Sim():
    def __init__(self):
        pygame.init()
        self.running = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.vec = pygame.math.Vector2
        self.window = self.screen.get_rect()

        # Title window
        pygame.display.set_caption("Boids Simulation")

        # TODO: add window icon here

        # Instantiate a container full of boids
        self.boid_container = [Boid(self) for _ in range(NUMBER_OF_BOIDS)]

    # Event handler
    def events(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

    def step(self):
        for boid in self.boid_container:
            boid.step()
        
    def render(self):
        # Wipe last screen
        self.screen.fill(SCREEN_COLOUR)

        print(len(self.boid_container))

        for boid in self.boid_container:
            boid.draw(self.screen)
        

    def run(self):
        self.running = True
        while self.running:
            # Tick clock to limit FPS
            self.clock.tick(FPS)

            # Check for any pygame events
            self.events()

            # Advance one step of simulation
            self.step()

            # Render boids
            self.render()

            # Swap buffers
            pygame.display.flip()

            for boid in self.boid_container:
                print(boid.pos)

# TODO: ABSTRACT CLASS?
class BoidObject():
    def __init__(self, sim, pos):
        self.sim = sim
        self.acc = sim.vec(0, 0)
        self.vel = sim.vec(0, 0)
        self.pos = sim.vec(pos)
        self.speed = 1

    def step(self):
        print(f"Vel: {self.vel} // Acc: {self.acc} // Pos: {self.pos}")
        self.vel += self.acc
        self.pos += self.vel

        self.acc = self.sim.vec(0, 0)

        if self.pos.x >= self.sim.window.w or self.pos.x <= 0:
            self.vel[0] = -self.vel[0]
        if self.pos.y >= self.sim.window.h or self.pos.y <= 0:
            self.vel[1] = -self.vel[1]

class Boid(BoidObject):
    def __init__(self, sim):
        pos = (random.randint(int(SCREEN_WIDTH / GENERATION_MARGIN), int((SCREEN_WIDTH / GENERATION_MARGIN) * (GENERATION_MARGIN - 1))), random.randint(int(SCREEN_HEIGHT / GENERATION_MARGIN), int((SCREEN_HEIGHT / GENERATION_MARGIN) * (GENERATION_MARGIN - 1))))
        super().__init__(sim, pos)
        self.speed = MAX_SPEED
        self.vel = sim.vec(1, 1)

    def draw(self, screen):
        pygame.draw.circle(screen, BOID_COLOUR, self.pos, BOID_SIZE)


    def step(self):
        # self.acc += self.limit_acceleration(self.seperation())
        # self.acc += self.limit_acceleration(self.alignment())
        # self.acc += self.limit_acceleration(self.cohesion())

        self.acc += self.seperation()

        super().step()

        """
        # Set all accumulator values to 0
        neighbours = 0
        close_delta = sim.vec(0, 0)
        avg_velocity = sim.vec(0, 0)
        avg_position = sim.vec(0, 0)

        for other_boid in sim.boid_container:
            
            # Ensure calculations are not done on matching boids
            if self == other_boid:
                pass

            else:
                # Calculate difference in x and y coordinates 
                position_delta = self.pos - other_boid.pos
                
                squared_distance = position_delta.length()
                squared_visual_range = math.sqrt((LINEAR_VISUAL_RANGE ** 2) * 2)

                # Check other boid is within visual range
                if squared_distance < squared_visual_range:

                    
                    avg_velocity += other_boid.vel
                    avg_position += other_boid.pos
                    neighbours += 1
                    
                    squared_protected_range = math.sqrt((LINEAR_PROTECTED_RANGE ** 2) * 2)

                    # Check other boid is within protected range
                    if squared_distance < squared_protected_range:

                        close_delta += position_delta

        # If there are any other boids in visual range
        if neighbours > 0:
            avg_velocity = avg_velocity / neighbours
            avg_position = avg_position / neighbours

        self.update_velocity(avg_velocity, avg_position, close_delta)
            
        self.bounce(self.pos[0], self.pos[1], BOID_SIZE)
        """

        # Increment positions by velocity
        self.move()
        

    def update_velocity(self, avg_velocity, avg_position, close_delta):
            self.vel = self.vel + ((avg_velocity - self.vel) * MATCHING_FACTOR) + ((avg_position - self.pos) * CENTERING_FACTOR)

            self.vel += close_delta * SEPERATION_FACTOR

    def move(self):
        # Ensure velocity doesn't exceed max velocity
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        self.pos += self.vel

    def seperation(self):
        acc_request = self.sim.vec(0,0)
        neighbouring_boids = self.boids_in_radius(LINEAR_PROTECTED_RANGE)

        if len(neighbouring_boids) == 0:
            return acc_request

        for neighbour in neighbouring_boids:
            try:
                dist_delta = self.pos - neighbour.pos
                acc_request += (dist_delta) * (LINEAR_PROTECTED_RANGE / self.pos.distance_to(neighbour.pos))
            except ZeroDivisionError:
                continue

        return self.limit_force(acc_request, neighbouring_boids)

    def alignment(self):
        pass

    def cohesion(self):
        pass

    def boids_in_radius(self, radius):
        boids_present = []
        for surrounding_boid in self.sim.boid_container:
            if surrounding_boid == self:
                pass
            else:
                print(f"dist to: {self.pos.distance_to(surrounding_boid.pos)} // radius: {radius}")

                if self.pos.distance_to(surrounding_boid.pos) < radius:
                    boids_present.append(surrounding_boid)
            
        print(f"BOIDS IN RANGE: {len(boids_present)}")
        return boids_present
    
    """
    # TODO: sort why acceleration always seems to be 0 and get it to limit properly
    def limit_acceleration(self, acc_vector):
        print("limiting acc")
        potential_acc = self.acc + acc_vector
        print(f"mag: {potential_acc.magnitude()} // max: {MAX_ACC_REQUEST}")
        if potential_acc.magnitude() <= MAX_ACC_REQUEST:
            return acc_vector
        else:
            return acc_vector.scale_to_length(MAX_ACC_REQUEST - self.acc.magnitude())
    """

    def limit_force(self, force, boids_in_radius):
        force /= len(boids_in_radius)
        if force.length() <= 0:
            return force
        
        force.scale_to_length(1)
        force = force * self.speed - self.vel

        if force.length() > MAX_ACC_REQUEST:
            force.scale_to_length(MAX_ACC_REQUEST)
        
        return force

        
if __name__ == '__main__':
    sim = Sim()
    sim.run()