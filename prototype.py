import pygame
import random
import math

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
LINEAR_VISUAL_RANGE = 50
LINEAR_PROTECTED_RANGE = 20
MAX_SPEED = 5
SEPERATION_FACTOR = 0.1
MATCHING_FACTOR = 0.001
CENTERING_FACTOR = 0.00001

class Sim():
    def __init__(self):
        pygame.init()
        self.running = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.vec = pygame.math.Vector2

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
            boid.step(self)
        
    def render(self):
        # Wipe last screen
        self.screen.fill(SCREEN_COLOUR)

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


class BoidObject():
    def __init__(self, sim, pos):
        self.sim = sim
        self.acc = sim.vec(0, 0)
        self.vel = sim.vec(0, 0)
        self.pos = sim.vec(pos)
        self.speed = 1

class Boid(BoidObject):
    def __init__(self, sim):
        pos = (random.randint(int(SCREEN_WIDTH / GENERATION_MARGIN), int((SCREEN_WIDTH / GENERATION_MARGIN) * (GENERATION_MARGIN - 1))), random.randint(int(SCREEN_HEIGHT / GENERATION_MARGIN), int((SCREEN_HEIGHT / GENERATION_MARGIN) * (GENERATION_MARGIN - 1))))
        super().__init__(sim, pos)
        self.speed = MAX_SPEED
        self.vel = sim.vec(1, 1)

    def draw(self, screen):
        pygame.draw.circle(screen, BOID_COLOUR, self.pos, BOID_SIZE)

    def step(self, sim):
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

    def bounce(self, x, y, offset):
        # Boids wrap around edges of screen appearing on other side
        if x + offset >= SCREEN_WIDTH or x - offset <= 0:
            self.vel[0] = -self.vel[0]
        if y + offset >= SCREEN_HEIGHT or y - offset <= 0:
            self.vel[1] = -self.vel[1]

    def seperation(self):
        pass

    def alignment(self):
        pass

    def cohesion(self):
        pass
        

if __name__ == '__main__':
    sim = Sim()
    sim.run()