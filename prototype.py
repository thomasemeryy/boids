import pygame
import random
import math

# CONSTANTS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUMBER_OF_BOIDS = 30
SIZE = 5
GENERATION_MARGIN = 12 # The larger the number, the smaller the margin
BOID_COLOUR = (255, 255, 255)
LINEAR_VISUAL_RANGE = 50
LINEAR_PROTECTED_RANGE = 20
FPS = 60
MAX_VELOCITY = 5
SEPERATION_FACTOR = 0.1
MATCHING_FACTOR = 0.001
CENTERING_FACTOR = 0.00001

# Initialise Simulation class holding the pygame window data
class Simulation():

    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        vec = pygame.math.Vector2
        pygame.display.set_caption("Boids Simulation")


class Boid():
    def __init__(self):
        self.x = random.randint(int(SCREEN_WIDTH / GENERATION_MARGIN), int((SCREEN_WIDTH / GENERATION_MARGIN) * (GENERATION_MARGIN - 1)))
        self.y = random.randint(int(SCREEN_HEIGHT / GENERATION_MARGIN), int((SCREEN_HEIGHT / GENERATION_MARGIN) * (GENERATION_MARGIN - 1)))
        self.position = vec(self.x, self.y)
        self.vx = 1
        self.vy = 1
        self.velocity = vec(self.vx, self.vy)
        self.size = SIZE

    def get_position(self):
        return self.position

    def get_velocity(self):
        return self.velocity

    def get_size(self):
        return self.size


    def reverse_vx(self):
        self.velocity[0] = -self.velocity[0]

    def reverse_vy(self):
        self.velocity[1] = -self.velocity[1]

    def update_velocity(self, avg_velocity, avg_position, close_delta):
            self.velocity = self.velocity + ((avg_velocity - self.velocity) * MATCHING_FACTOR) + ((avg_position - self.position) * CENTERING_FACTOR)

            self.velocity += close_delta * SEPERATION_FACTOR

    def move(self):
        # Ensure velocity doesn't exceed max velocity
        if self.velocity.length() > MAX_VELOCITY:
            self.velocity.scale_to_length(MAX_VELOCITY)

        self.position += self.velocity

    def bounce(self, x, y, offset):
        # Boids wrap around edges of screen appearing on other side
        if x + offset >= SCREEN_WIDTH or x - offset <= 0:
            self.reverse_vx()
        if y + offset >= SCREEN_HEIGHT or y - offset <= 0:
            self.reverse_vy()
        

# Instantiate a container full of boids
boid_container = [Boid() for _ in range(NUMBER_OF_BOIDS)]

keep_running = True
while keep_running:

    # Set background colour
    screen.fill((0, 0, 0))

    # Event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            keep_running = False

    # Render boids
    for boid in boid_container:

        # Set all accumulator values to 0
        neighbours = 0
        close_delta = vec(0, 0)
        avg_velocity = vec(0, 0)
        avg_position = vec(0, 0)

        for other_boid in boid_container:
            
            # Ensure calculations are not done on matching boids
            if boid == other_boid:
                pass

            else:
                # Calculate difference in x and y coordinates 
                position_delta = boid.get_position() - other_boid.get_position()
                
                squared_distance = position_delta.length()
                squared_visual_range = math.sqrt((LINEAR_VISUAL_RANGE ** 2) * 2)

                # Check other boid is within visual range
                if squared_distance < squared_visual_range:

                    
                    avg_velocity += other_boid.get_velocity()
                    avg_position += other_boid.get_position()
                    neighbours += 1
                    
                    squared_protected_range = math.sqrt((LINEAR_PROTECTED_RANGE ** 2) * 2)

                    # Check other boid is within protected range
                    if squared_distance < squared_protected_range:

                        close_delta += position_delta

        # If there are any other boids in visual range
        if neighbours > 0:
            avg_velocity = avg_velocity / neighbours
            avg_position = avg_position / neighbours

        boid.update_velocity(avg_velocity, avg_position, close_delta)
            
        boid.bounce(boid.get_position()[0], boid.get_position()[1], SIZE)
        
        # Increment positions by velocity
        boid.move()

        # Render boid
        pygame.draw.circle(screen, BOID_COLOUR, boid.get_position(), boid.get_size())

    # Swap buffers
    pygame.display.flip()

    # Clock tick to limit FPS
    clock.tick(FPS)

pygame.quit()