import pygame as pyg
import pygame_gui as pygui
import random
import math
import abc

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
DEFAULT_SEPERATION_FACTOR = 2
DEFAULT_ALIGNMENT_FACTOR = 1
DEFAULT_COHESION_FACTOR = 1

class GUI():
    def __init__(self, sim):
        self.__manager = pygui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__gui_margin = (10, 20)
        self.__slider_size = (150, 40)
        self.__gui_sliders = 5
        self.__sim = sim

        window = self.__sim.get_window()

        self.__sliders = {"protected_range": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 0), self.__slider_size), start_value=DEFAULT_PROTECTED_RANGE, value_range=(10, 100), manager=self.__manager), 
                          "visual_range": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 1), self.__slider_size), start_value=DEFAULT_VISUAL_RANGE, value_range=(50, 300), manager=self.__manager),
                          "seperation": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 2), self.__slider_size), start_value=DEFAULT_SEPERATION_FACTOR, value_range=(0.1, 3), manager=self.__manager),
                          "alignment": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 3), self.__slider_size), start_value=DEFAULT_ALIGNMENT_FACTOR, value_range=(0.1, 3), manager=self.__manager),
                          "cohesion": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 4), self.__slider_size), start_value=DEFAULT_COHESION_FACTOR, value_range=(0.1, 3), manager=self.__manager)}

        self.__slider_labels = {"protected_range": pygui.elements.UILabel(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 0, "label"), self.__slider_size), text=f"Protected Range: {DEFAULT_PROTECTED_RANGE}"),
                                 "visual_range": pygui.elements.UILabel(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 1, "label"), self.__slider_size), text=f"Visual Range: {DEFAULT_VISUAL_RANGE}"),
                                 "seperation": pygui.elements.UILabel(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 2, "label"), self.__slider_size), text=f"Seperation: {DEFAULT_SEPERATION_FACTOR:.2f}"),
                                 "alignment": pygui.elements.UILabel(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 3, "label"), self.__slider_size), text=f"Alignment: {DEFAULT_ALIGNMENT_FACTOR:.2f}"),
                                 "cohesion": pygui.elements.UILabel(relative_rect=pyg.Rect(self.__calculate_gui_pos(window, 4, "label"), self.__slider_size), text=f"Cohesion: {DEFAULT_COHESION_FACTOR:.2f}")}

    def __calculate_gui_pos(self, window, n, type = "slider"):
        x = (window.w - (self.__gui_sliders * self.__slider_size[0]) - ((self.__gui_sliders - 1) * self.__gui_margin[0])) / 2 + (n * (self.__slider_size[0] + self.__gui_margin[0]))
        if type == "slider":
            y = window.y + self.__gui_margin[1]
        elif type == "label":
            y = window.y + self.__gui_margin[1] + 35

        return (x, y)

    def get_slider(self, slider):
        return self.__sliders[slider]
    
    def get_slider_label(self, slider):
        return self.__slider_labels[slider]

    def process_gui_event(self, event):
        self.__manager.process_events(event)

        if event.type == pygui.UI_HORIZONTAL_SLIDER_MOVED:
          pass

    def update_gui(self, time_delta):
        self.__manager.update(time_delta)

    def render_gui(self, screen):
        self.__manager.draw_ui(screen)

class Sim():
    def __init__(self):
        pyg.init()
        self.__running = False
        self.__screen = pyg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__clock = pyg.time.Clock()
        self.__window = self.__screen.get_rect()
        self.__gui = GUI(self)

        self._config_values = {"visual_range": DEFAULT_VISUAL_RANGE, 
                               "protected_range": DEFAULT_PROTECTED_RANGE,
                               "seperation": DEFAULT_SEPERATION_FACTOR,
                               "alignment": DEFAULT_ALIGNMENT_FACTOR,
                               "cohesion": DEFAULT_COHESION_FACTOR}

        # Title window
        pyg.display.set_caption("Boids Simulation")

        # TODO: add window icon here

        # Instantiate a container full of boids
        self.boid_container = [Boid(self) for _ in range(NUMBER_OF_BOIDS)]

    def get_config_value(self, type):
        return self._config_values[type]

    def get_window(self):
        return self.__window

    # Event handler
    def handle_events(self, gui):
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    self.__running = False

                gui.process_gui_event(event)
                
    def step(self):
        for boid in self.boid_container:
            boid.step()
        
    def render(self):
        # Wipe last screen
        self.__screen.fill(SCREEN_COLOUR)

        for boid in self.boid_container:
            boid.draw(self.__screen)
        
    def update_gui_values(self, gui):
        # Add values from sliders to simulation instance

        self._config_values["protected_range"] = gui.get_slider("protected_range").get_current_value()
        self._config_values["visual_range"] = gui.get_slider("visual_range").get_current_value()
        self._config_values["seperation"] = gui.get_slider("seperation").get_current_value()
        self._config_values["alignment"] = gui.get_slider("alignment").get_current_value()
        self._config_values["cohesion"] = gui.get_slider("cohesion").get_current_value()

        gui.get_slider_label("protected_range").set_text(f"Protected Range: {self._config_values['protected_range']}")
        gui.get_slider_label("visual_range").set_text(f"Visual Range: {self._config_values['visual_range']}")
        gui.get_slider_label("seperation").set_text(f"Seperation: {self._config_values['seperation']:.2f}")
        gui.get_slider_label("alignment").set_text(f"Alignment: {self._config_values['alignment']:.2f}")
        gui.get_slider_label("cohesion").set_text(f"Cohesion: {self._config_values['cohesion']:.2f}")

    def run(self):
        self.__running = True
        while self.__running:
            # Tick clock to limit FPS
            time_delta = self.__clock.tick(FPS)/1000.0

            # Check for any pygame events
            self.handle_events(self.__gui)

            # Update GUI
            self.__gui.update_gui(time_delta)

            # Advance one step of simulation
            self.step()
            self.update_gui_values(self.__gui)

            # Render boids and GUI
            self.render()
            self.__gui.render_gui(self.__screen)

            # Swap buffers
            pyg.display.flip()

# Abstract class so it cannot be instantiated
class BoidObject(abc.ABC):
    def __init__(self, sim, pos):
        self._sim = sim
        self._acc = pyg.math.Vector2(0, 0)
        self._vel = pyg.math.Vector2(0, 0)
        self._pos = pyg.math.Vector2(pos)
        self._max_speed = 1

    @abc.abstractmethod
    def step(self):
        self._vel += self._acc
        self._pos += self._vel

        self._acc = pyg.math.Vector2(0, 0)

        # Boids wrap around window
        window = self._sim.get_window()
        if self._pos.x > window.w:
            self._pos.x -= window.w
        elif self._pos.x < 0:
            self._pos.x += window.w

        if self._pos.y > window.h:
            self._pos.y -= window.h
        elif self._pos.y < 0:
            self._pos.y += window.h
        

class Boid(BoidObject):
    def __init__(self, sim):
        pos = (random.randint(int(SCREEN_WIDTH / GENERATION_MARGIN), int((SCREEN_WIDTH / GENERATION_MARGIN) * (GENERATION_MARGIN - 1))), random.randint(int(SCREEN_HEIGHT / GENERATION_MARGIN), int((SCREEN_HEIGHT / GENERATION_MARGIN) * (GENERATION_MARGIN - 1))))
        super().__init__(sim, pos)
        self._max_speed = MAX_SPEED
        self._vel = pyg.math.Vector2(1, 1)

    def draw(self, screen):
        # Calculate points of the triangle
        phi = math.atan2(self._vel.y, self._vel.x)
        phi2 = 0.75 * math.pi

        pos1 = ((self._pos.x + (math.cos(phi) * BOID_SIZE), (self._pos.y + (math.sin(phi) * BOID_SIZE))))
        pos2 = ((self._pos.x + (math.cos(phi + phi2) * BOID_SIZE), (self._pos.y + (math.sin(phi + phi2) * BOID_SIZE))))
        pos3 = ((self._pos.x + (math.cos(phi - phi2) * BOID_SIZE), (self._pos.y + (math.sin(phi - phi2) * BOID_SIZE))))

        pyg.draw.polygon(screen, BOID_COLOUR, (pos1, pos2, pos3))


    def step(self):
        self._acc += self.__seperation() * self._sim.get_config_value("seperation")
        self._acc += self.__alignment() * self._sim.get_config_value("alignment")
        self._acc += self.__cohesion() * self._sim.get_config_value("cohesion")
        super().step()

        # Increment positions by velocity
        self.__move()
        

    def __move(self):
        # Ensure velocity doesn't exceed max velocity
        if self._vel.length() > MAX_SPEED:
            self._vel.scale_to_length(MAX_SPEED)

        self._pos += self._vel

    def __seperation(self):
        acc_request = pyg.math.Vector2(0, 0)
        neighbouring_boids = self.__boids_in_radius(self._sim.get_config_value("protected_range"))

        if len(neighbouring_boids) == 0:
            return acc_request

        for neighbour in neighbouring_boids:
            try:
                dist_delta = self._pos - neighbour._pos
                acc_request += (dist_delta) * (self._sim.get_config_value("protected_range") / self._pos.distance_to(neighbour._pos))
            except ZeroDivisionError:
                continue

        return self.__limit_force(acc_request, neighbouring_boids)

    def __alignment(self):
        force = pyg.math.Vector2(0, 0)
        neighbouring_boids = self.__boids_in_radius(self._sim.get_config_value("visual_range"))

        if len(neighbouring_boids) == 0:
            return force
        
        for neighbour in neighbouring_boids:
            force += neighbour._vel

        if force.length() == 0:
            return force
        
        return self.__limit_force(force, neighbouring_boids)

    def __cohesion(self):
        force = pyg.math.Vector2(0, 0)
        neighbouring_boids = self.__boids_in_radius(self._sim.get_config_value("visual_range"))

        if len(neighbouring_boids) == 0:
            return force
        
        for neighbour in neighbouring_boids:
            force += (neighbour._pos - self._pos)

        if force.length() == 0:
            return force
        
        return self.__limit_force(force, neighbouring_boids)

    def __boids_in_radius(self, radius):
        boids_present = []
        for surrounding_boid in self._sim.boid_container:
            if surrounding_boid == self:
                pass
            else:

                if self._pos.distance_to(surrounding_boid._pos) < radius:
                    boids_present.append(surrounding_boid)
            
        return boids_present

    def __limit_force(self, force, boids_in_radius):
        force /= len(boids_in_radius)
        if round(force.length(), 3) <= 0:
            return force
        
        print(force.length())

        force.scale_to_length(1)
        force = force * self._max_speed - self._vel

        if force.length() > MAX_ACC_REQUEST:
            force.scale_to_length(MAX_ACC_REQUEST)
        
        return force

        
if __name__ == '__main__':
    sim = Sim()
    sim.run()