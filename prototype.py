import pygame as pyg
import pygame_gui as pygui
import random
import math

# Sim constants
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900
SCREEN_COLOUR = (0, 0, 0)
FPS = 60

# Boid constants
NUMBER_OF_BOIDS = 200
BOID_SIZE = 10
GENERATION_MARGIN = 12 # The larger the number, the smaller the margin
BOID_COLOUR = (255, 255, 255)
DEFAULT_VISUAL_RANGE = 100
DEFAULT_PROTECTED_RANGE = 20
MAX_SPEED = 1
MAX_ACC_REQUEST = 0.1
SEPERATION_FACTOR = 2
ALIGNMENT_FACTOR = 1
COHESION_FACTOR = 1

class GUI():
    def __init__(self):
        self.manager = pygui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.protected_range_slider = pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((350, 275), (100, 50)), start_value=DEFAULT_PROTECTED_RANGE, value_range=(10, 100), manager=self.manager)


    def process_gui_event(self, event):
        self.manager.process_events(event)

        if event.type == pygui.UI_HORIZONTAL_SLIDER_MOVED:
          if event.ui_element == self.protected_range_slider:
              print('current slider value:', event.value)

    def update_gui(self, time_delta):
        self.manager.update(time_delta)

    def render_gui(self, screen):
        self.manager.draw_ui(screen)

class Sim():
    def __init__(self):
        pyg.init()
        self.running = False
        self.screen = pyg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pyg.time.Clock()
        self.vec = pyg.math.Vector2
        self.window = self.screen.get_rect()

        # Title window
        pyg.display.set_caption("Boids Simulation")

        # TODO: add window icon here

        # Instantiate a container full of boids
        self.boid_container = [Boid(self) for _ in range(NUMBER_OF_BOIDS)]

    # Event handler
    def events(self, gui):
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    self.running = False

                gui.process_gui_event(event)
                
    def step(self):
        for boid in self.boid_container:
            boid.step()
        
    def render(self):
        # Wipe last screen
        self.screen.fill(SCREEN_COLOUR)

        for boid in self.boid_container:
            boid.draw(self.screen)
        

    def run(self, gui):
        self.running = True
        while self.running:
            # Tick clock to limit FPS
            time_delta = self.clock.tick(FPS)/1000.0

            # Check for any pygame events
            self.events(gui)

            # Update GUI
            gui.update_gui(time_delta)

            # Advance one step of simulation
            self.step()

            # Render boids and GUI
            self.render()
            gui.render_gui(self.screen)

            # Swap buffers
            pyg.display.flip()

            
# TODO: ABSTRACT CLASS?
class BoidObject():
    def __init__(self, sim, pos):
        self.sim = sim
        self.acc = sim.vec(0, 0)
        self.vel = sim.vec(0, 0)
        self.pos = sim.vec(pos)
        self.speed = 1

    def step(self):
        self.vel += self.acc
        self.pos += self.vel

        self.acc = self.sim.vec(0, 0)

        # Boids wrap around window
        if self.pos.x > self.sim.window.w:
            self.pos.x -= self.sim.window.w
        elif self.pos.x < 0:
            self.pos.x += self.sim.window.w

        if self.pos.y > self.sim.window.h:
            self.pos.y -= self.sim.window.h
        elif self.pos.y < 0:
            self.pos.y += self.sim.window.h
        

class Boid(BoidObject):
    def __init__(self, sim):
        pos = (random.randint(int(SCREEN_WIDTH / GENERATION_MARGIN), int((SCREEN_WIDTH / GENERATION_MARGIN) * (GENERATION_MARGIN - 1))), random.randint(int(SCREEN_HEIGHT / GENERATION_MARGIN), int((SCREEN_HEIGHT / GENERATION_MARGIN) * (GENERATION_MARGIN - 1))))
        super().__init__(sim, pos)
        self.speed = MAX_SPEED
        self.vel = sim.vec(1, 1)

        self.visual_range = DEFAULT_VISUAL_RANGE
        self.protected_range = DEFAULT_PROTECTED_RANGE

    def draw(self, screen):
        # Calculate points of the triangle
        phi = math.atan2(self.vel.y, self.vel.x)
        phi2 = 0.75 * math.pi

        pos1 = ((self.pos.x + (math.cos(phi) * BOID_SIZE), (self.pos.y + (math.sin(phi) * BOID_SIZE))))
        pos2 = ((self.pos.x + (math.cos(phi + phi2) * BOID_SIZE), (self.pos.y + (math.sin(phi + phi2) * BOID_SIZE))))
        pos3 = ((self.pos.x + (math.cos(phi - phi2) * BOID_SIZE), (self.pos.y + (math.sin(phi - phi2) * BOID_SIZE))))

        pyg.draw.polygon(screen, BOID_COLOUR, (pos1, pos2, pos3))


    def step(self):
        self.acc += self.seperation() * SEPERATION_FACTOR
        self.acc += self.alignment() * ALIGNMENT_FACTOR
        self.acc += self.cohesion() * COHESION_FACTOR

        super().step()

        # Increment positions by velocity
        self.move()
        

    def move(self):
        # Ensure velocity doesn't exceed max velocity
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        self.pos += self.vel

    def seperation(self):
        acc_request = self.sim.vec(0, 0)
        neighbouring_boids = self.boids_in_radius(self.protected_range)

        if len(neighbouring_boids) == 0:
            return acc_request

        for neighbour in neighbouring_boids:
            try:
                dist_delta = self.pos - neighbour.pos
                acc_request += (dist_delta) * (self.protected_range / self.pos.distance_to(neighbour.pos))
            except ZeroDivisionError:
                continue

        return self.limit_force(acc_request, neighbouring_boids)

    def alignment(self):
        force = self.sim.vec(0, 0)
        neighbouring_boids = self.boids_in_radius(self.visual_range)

        if len(neighbouring_boids) == 0:
            return force
        
        for neighbour in neighbouring_boids:
            force += neighbour.vel

        if force.length() == 0:
            return force
        
        return self.limit_force(force, neighbouring_boids)

    def cohesion(self):
        force = self.sim.vec(0, 0)
        neighbouring_boids = self.boids_in_radius(self.visual_range)

        if len(neighbouring_boids) == 0:
            return force
        
        for neighbour in neighbouring_boids:
            force += (neighbour.pos - self.pos)

        if force.length() == 0:
            return force
        
        return self.limit_force(force, neighbouring_boids)

    def boids_in_radius(self, radius):
        boids_present = []
        for surrounding_boid in self.sim.boid_container:
            if surrounding_boid == self:
                pass
            else:

                if self.pos.distance_to(surrounding_boid.pos) < radius:
                    boids_present.append(surrounding_boid)
            
        return boids_present

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
    gui = GUI()
    sim.run(gui)