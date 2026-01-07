import pygame as pyg
import pygame_gui as pygui
import random
import math
import abc
import os
import datetime
import json
from enum import Enum


class Config():
    IMAGES_FOLDER = "images"
    MAPS_FOLDER = "maps"

    # Sim constants
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 800
    SCREEN_COLOUR = (0, 0, 0)
    FPS = 60
    NUMBER_OF_GRIDS_WIDE = 3
    NUMBER_OF_GRIDS_HIGH = 3
    DISPLAY_GRIDS = True

    # Boid constants
    NUMBER_OF_BOIDS = 150
    GENERATION_MARGIN = 12 # The larger the number, the smaller the margin
    BOID_SIZE = 5
    PREDATOR_SIZE = 10
    ASSEMBLY_SIZE = 25
    BOUNDARY_THICKNESS = 3
    BOUNDARY_RADIUS = 20
    BOID_COLOUR = (255, 255, 255)
    PREDATOR_COLOUR = (255, 0, 0)
    ASSEMBLY_COLOUR = (255, 255, 0)
    DEFAULT_VISUAL_RANGE = 100
    DEFAULT_PROTECTED_RANGE = 20
    DEFAULT_PREDATOR_RANGE = 30
    DEFAULT_BOUNDARY_RANGE = 5
    DEFAULT_SEPARATION_FACTOR = 2
    DEFAULT_SEEKING_FACTOR = 0.3
    DEFAULT_ALIGNMENT_FACTOR = 1
    DEFAULT_COHESION_FACTOR = 1
    DEFAULT_AVOIDANCE_FACTOR = 5
    ARRIVAL_SLOWING_RADIUS = 100
    ARRIVED_RADIUS = 5
    MAX_SPEED = 2
    MAX_ACC_REQUEST = 0.1

    # Menu layout
    MOUSE_BOUNDARY_MARGIN = 90
    MENU_TITLE_X = 112
    MENU_TITLE_Y = 80
    MENU_HEADERS_Y = 275
    MENU_CONTROLS_Y = 345
    MENU_CONTROLS_HEIGHT = 300
    MENU_CONTROLS_WIDTH = 400
    MENU_CONTROLS_MARGIN = 50
    MENU_RUN_Y = 560
    LOAD_DIALOG_SIZE = (800, 400)
    SAVE_DIALOG_SIZE = (200, 50)

    # Map builder layout
    TOOLS_X = 40
    TOOLS_Y = 200
    TOOLS_MARGIN = 80
    CONFIRM_X = SCREEN_WIDTH - 90
    CONFIRM_Y = SCREEN_HEIGHT - 80
    IMAGE_MARGIN_X = 120
    IMAGE_MARGIN_Y = 100
    ERASE_RADIUS = 12

class GameState(Enum):
    MENU = "menu"
    MAP_BUILDER = "map_builder"
    SIMULATION = "simulation"

class GUI():
    def __init__(self, sim):
        self.__manager = pygui.UIManager((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.__gui_margin = (10, 20)
        self.__slider_size = (150, 40)
        self.__gui_sliders = 5
        self.__sim = sim
        self.__slider_moving = False
        self.__window = self.__sim.get_window()

        self.__slider_keys = ["protected_range", "visual_range", "separation", "alignment", "cohesion"]

        self.__sliders = {"protected_range": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_PROTECTED_RANGE, value_range=(10, 100), manager=self.__manager), 
                          "visual_range": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_VISUAL_RANGE, value_range=(50, 300), manager=self.__manager),
                          "separation": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_SEPARATION_FACTOR, value_range=(0.1, 3), manager=self.__manager),
                          "alignment": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_ALIGNMENT_FACTOR, value_range=(0.1, 3), manager=self.__manager),
                          "cohesion": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_COHESION_FACTOR, value_range=(0.1, 3), manager=self.__manager)}

        self.__slider_labels = {"protected_range": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Protected Range: {Config.DEFAULT_PROTECTED_RANGE}"),
                                 "visual_range": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Visual Range: {Config.DEFAULT_VISUAL_RANGE}"),
                                 "separation": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Separation: {Config.DEFAULT_SEPARATION_FACTOR:.2f}"),
                                 "alignment": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Alignment: {Config.DEFAULT_ALIGNMENT_FACTOR:.2f}"),
                                 "cohesion": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Cohesion: {Config.DEFAULT_COHESION_FACTOR:.2f}")}

        self.set_gui_layout("menu")

    def set_gui_layout(self, state): # TODO: Create sliders on main menu screen (see Gemini)
        for i, slider_key in enumerate(self.__slider_keys):
            
            if state == "menu":
                if slider_key in ["protected_range", "visual_range"]:
                    x = (Config.SCREEN_WIDTH // 2) + 50
                    y = Config.MENU_CONTROLS_Y + (0 * Config.MENU_CONTROLS_MARGIN)

                    if i == 1:
                        x += (self.__slider_size[0] + 20 + 10)

                    self.__sliders[slider_key].set_dimensions((self.__slider_size[0] + 20, self.__slider_size[1] + 20))
                else:
                    x = (Config.SCREEN_WIDTH // 2) + 50
                    y = Config.MENU_CONTROLS_Y + (2 * Config.MENU_CONTROLS_MARGIN) - 5

                    x += (((self.__slider_size[0] - 29) * (i % 3)))

                    self.__sliders[slider_key].set_dimensions((self.__slider_size[0] - 40, self.__slider_size[1] + 20))

                self.__sliders[slider_key].set_relative_position((x, y + 7))

                # Position labels correctly
                slider_rect = self.__sliders[slider_key].get_relative_rect()
                label_rect = self.__slider_labels[slider_key].get_relative_rect()

                label_x = slider_rect.centerx - label_rect.width // 2
                label_y = slider_rect.bottom

                self.__slider_labels[slider_key].set_relative_position((label_x, label_y - 8))
                
            elif state == "game" or state == "map_builder":
                x = (self.__window.w - (self.__gui_sliders * self.__slider_size[0]) - ((self.__gui_sliders - 1) * self.__gui_margin[0])) / 2 + (i * (self.__slider_size[0] + self.__gui_margin[0]))
                y = self.__window.y + self.__gui_margin[1]

                self.__sliders[slider_key].set_dimensions((self.__slider_size[0], self.__slider_size[1]))
                self.__slider_labels[slider_key].set_relative_position((x, y + self.__slider_size[1] - 10))
                self.__sliders[slider_key].set_relative_position((x, y))

            elif state == "TODO":
                pass # TODO: Hide GUI elements
    

    def get_slider(self, slider):
        return self.__sliders[slider]

    def get_slider_label(self, slider):
        return self.__slider_labels[slider]
    
    def get_slider_size(self):
        return self.__slider_size

    def process_gui_event(self, event):
        self.__manager.process_events(event)

        if event.type == pygui.UI_HORIZONTAL_SLIDER_MOVED:
            pass

    def check_slider_moving(self):
        return self.__slider_moving

    def update_gui(self, time_delta):
        self.__manager.update(time_delta)

    def render_gui(self, screen):
        self.__manager.draw_ui(screen)

    def get_gui_manager(self):
        return self.__manager

class Sim():
    def __init__(self):
        pyg.init()
        self.__current_game_state = GameState.MENU
        self.__running = False
        self.__screen = pyg.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.__window = self.__screen.get_rect()
        self.__clock = pyg.time.Clock()
        self.__gui = GUI(self)
        self.__menu = Menu(self)
        self.__map_builder = MapBuilder(self)
        self.__boundary_manager = BoundaryManager(self)
        self.__assembly_point = None
        self.__map_loaded = False

        self.__config_values = {"visual_range": Config.DEFAULT_VISUAL_RANGE, 
                               "protected_range": Config.DEFAULT_PROTECTED_RANGE,
                               "predator_range": Config.DEFAULT_PREDATOR_RANGE,
                               "boundary_range": Config.DEFAULT_BOUNDARY_RANGE,
                               "separation": Config.DEFAULT_SEPARATION_FACTOR,
                               "seeking": Config.DEFAULT_SEEKING_FACTOR,
                               "alignment": Config.DEFAULT_ALIGNMENT_FACTOR,
                               "cohesion": Config.DEFAULT_COHESION_FACTOR,
                               "avoidance": Config.DEFAULT_AVOIDANCE_FACTOR}

        # Title window
        pyg.display.set_caption("Boids Simulation")

        # TODO: add window icon here

        # Instantiate a container full of boids
        # self.__boid_container = [Boid(self) for _ in range(Config.NUMBER_OF_BOIDS)]
        self.__boid_container = []

        # Create predator container
        self.__predator_container = []

        # Create boundary containers
        self.__boundary_container = []

    def get_config_value(self, type):
        return self.__config_values[type]
    
    def get_map_builder(self):
        return self.__map_builder

    def get_window(self):
        return self.__window
    
    def get_boid_container(self):
        return self.__boid_container
    
    def is_map_loaded(self):
        return self.__map_loaded
    
    def map_loaded(self):
        self.__map_loaded = True

    def map_unloaded(self):
        self.__map_loaded = False
    
    def create_boid_container(self, lst, json=False):
        if json:
            boids = []
            for pos in lst:
                boid = Boid(self)
                boid.set_pos(pyg.math.Vector2(pos))
                boids.append(boid)
            self.__map_builder.set_boids(boids)

        else:
            for boid in lst:
                self.__boid_container.append(boid)
    
    def get_predator_container(self):
        return self.__predator_container
    
    def get_boundary_container(self):
        return self.__boundary_container
    
    def create_boundary_container(self, lst, json=False):
        if json:
            boundaries = []
            for pos in lst:
                boundaries.append(Boundary((pyg.math.Vector2(pos[0]), pyg.math.Vector2(pos[1]))))
            self.__map_builder.set_boundaries(boundaries)
        else:
            for boundary in lst:
                self.__boundary_container.append(boundary)
    
    def get_assembly_point(self):
        return self.__assembly_point

    def reset_simulation(self):
        self.__boid_container = []
        self.__boundary_container = []
        self.__predator_container = []
        self.__assembly_point = None
    
    def create_assembly_point(self, point, json=False):
        if json:
            self.__map_builder.set_assembly(AssemblyPoint(pyg.math.Vector2(point)))
        else:
            self.__assembly_point = point

    def import_objects_to_sim(self, boundaries, assembly, boids):
        self.reset_simulation()
        self.create_boundary_container(boundaries)
        self.create_boid_container(boids)
        self.create_assembly_point(assembly)

    def import_objects_to_builder(self, boundaries, assembly, boids, img_path):
        self.__map_builder.reset()
        self.create_boundary_container(boundaries, True)
        self.create_boid_container(boids, True)
        self.create_assembly_point(assembly, True)
        self.__map_builder.handle_image(img_path)
    
    def get_gui_manager(self):
        return self.__gui.get_gui_manager()
    
    def set_game_state(self, state):
        if state == "menu":
            self.__current_game_state = GameState.MENU
            self.__gui.set_gui_layout("menu")
        elif state == "map_builder":
            self.__current_game_state = GameState.MAP_BUILDER
            self.__gui.set_gui_layout("map_builder")
            # Clear previous maps by calling reset function
        elif state == "simulation":
            # Get data from map builder - boundaries, assembly point and boids
            self.__current_game_state = GameState.SIMULATION
            self.__gui.set_gui_layout("game")
        else:
            pass

    # Event handler
    def handle_events(self, gui):
            for event in pyg.event.get():

                # Check for program killed
                if event.type == pyg.QUIT:
                    self.__running = False

                if self.__current_game_state == GameState.SIMULATION:
                    # Check left mouse button pressed
                    if pyg.mouse.get_pressed()[0]:
                        if self.mouse_in_boundary():
                            self.__predator_container.append(Predator(self, pyg.mouse.get_pos()))

                if self.__current_game_state == GameState.MAP_BUILDER:
                    if event.type == pyg.MOUSEBUTTONDOWN:
                        mouse_pos = pyg.mouse.get_pos()

                        for tool_id, button in self.__map_builder.get_tool_buttons().items():
                            if button.draw(self.__screen):
                                self.__map_builder.tool_click(tool_id)
                                return

                        self.__map_builder.handle_click(mouse_pos, event.button)

                # File path selected
                if event.type == pygui.UI_FILE_DIALOG_PATH_PICKED:
                    if event.ui_object_id == "#file_explorer":
                        self.__map_builder.handle_image(event.text)
                    elif event.ui_object_id == "#load_map_dialog":
                        self.__menu.handle_load_path(event.text)
                    

                # Check for keypresses to place objects
                if event.type == pyg.KEYDOWN:

                    if event.key == pyg.K_SPACE:
                        self.set_game_state("menu")

                    if self.__current_game_state == GameState.MAP_BUILDER:
                        if event.key == pyg.K_ESCAPE:
                            self.__map_builder.wall_end(pyg.mouse.get_pos(), True)

                    if self.__current_game_state == GameState.SIMULATION:
                        if event.key == pyg.K_1:
                            if self.mouse_in_boundary():
                                self.__boundary_manager.set_start_pos(pyg.mouse.get_pos())
                            else:
                                print("Mouse out of bounds")

                        elif event.key == pyg.K_2:
                            start_pos = self.__boundary_manager.get_start_pos()
                            if start_pos is not None:
                                    if self.mouse_in_boundary():
                                        end_pos = pyg.mouse.get_pos()
                                        if (start_pos[0] - end_pos[0])**2 + (start_pos[1] - end_pos[1])**2 > 0.01:
                                            new_boundary = Boundary((pyg.math.Vector2(start_pos), pyg.math.Vector2(end_pos)))
                                            self.__boundary_container.append(new_boundary)
                                            print(f"Start: {start_pos} // End: {end_pos}")
                                            self.__boundary_manager.clear_start_pos()
                                        else:
                                            print("Cannot have length zero")

                                    else:
                                        print("Mouse out of bounds")
                            else:
                                print("Must set start position first!")
                        elif event.key == pyg.K_3:
                            self.__assembly_point = AssemblyPoint(pyg.mouse.get_pos())
                            
                gui.process_gui_event(event)

    # Check mouse position does not exceed screen boundaries and does not fall in forbidden GUI zone
    def mouse_in_boundary(self):
        mpos = pyg.mouse.get_pos()
        if mpos[1] < Config.MOUSE_BOUNDARY_MARGIN:
            return False
        elif mpos[0] == 0 or mpos[0] >= (Config.SCREEN_WIDTH - 1):
            return False
        elif mpos[1] >= (Config.SCREEN_HEIGHT - 1):
            return False
        
        return True
  
    def step(self):
        for boid in self.__boid_container:
            boid.step()

    def render(self):
        # Wipe last screen
        self.__screen.fill(Config.SCREEN_COLOUR)

        self.create_grids()

        for boid in self.__boid_container:
            boid.draw(self.__screen)

        for predator in self.__predator_container:
            predator.draw(self.__screen)

        for boundary in self.__boundary_container:
            boundary.draw(self.__screen)
            # boundary.draw_expanded(self.__screen)
            
        if self.__assembly_point is not None:
            self.__assembly_point.draw(self.__screen)

    def create_grids(self): # TODO: Unfinished - use for spacial hashing
        self.standard_grid_dimensions = (Config.SCREEN_WIDTH // Config.NUMBER_OF_GRIDS_WIDE, Config.SCREEN_HEIGHT // Config.NUMBER_OF_GRIDS_HIGH)

        self.vertical_edge_grid_dimensions = (Config.SCREEN_WIDTH % (self.standard_grid_dimensions[0]), self.standard_grid_dimensions[1])
        self.horizontal_edge_grid_dimensions = (self.standard_grid_dimensions[0], Config.SCREEN_HEIGHT % (self.standard_grid_dimensions[1]))
        self.corner_grid_dimensions = ()

    def update_gui_values(self, gui):
        # Add values from sliders to simulation instance
        self.__config_values["protected_range"] = gui.get_slider("protected_range").get_current_value()
        self.__config_values["visual_range"] = gui.get_slider("visual_range").get_current_value()
        self.__config_values["separation"] = gui.get_slider("separation").get_current_value()
        self.__config_values["alignment"] = gui.get_slider("alignment").get_current_value()
        self.__config_values["cohesion"] = gui.get_slider("cohesion").get_current_value()

        gui.get_slider_label("protected_range").set_text(f"Protected Range: {self.__config_values['protected_range']}")
        gui.get_slider_label("visual_range").set_text(f"Visual Range: {self.__config_values['visual_range']}")
        gui.get_slider_label("separation").set_text(f"Separation: {self.__config_values['separation']:.2f}")
        gui.get_slider_label("alignment").set_text(f"Alignment: {self.__config_values['alignment']:.2f}")
        gui.get_slider_label("cohesion").set_text(f"Cohesion: {self.__config_values['cohesion']:.2f}")

    def run(self):
        self.__running = True
        while self.__running:
            # Tick clock to limit FPS
            time_delta = self.__clock.tick(Config.FPS) / 1000.0
            # print(self.__clock.get_fps())

            # Check for any pygame events
            self.handle_events(self.__gui)

            # Update GUI
            self.__gui.update_gui(time_delta)

            # Advance one step of simulation and render
            if self.__current_game_state == GameState.SIMULATION:
                self.step()
                self.render()
            
            # Update GUI values
            self.update_gui_values(self.__gui)

            if self.__current_game_state == GameState.MENU:
                self.__menu.render_menu(self.__screen)

            elif self.__current_game_state == GameState.MAP_BUILDER:
                self.__map_builder.render_builder(self.__screen)

            self.__gui.render_gui(self.__screen)
            
            # Swap buffers
            pyg.display.flip()

class Menu():
    def __init__(self, sim):
        self.__sim = sim
        self.__buttons_dict = {}

        self.__load_dialog = None

        self.__initialise_buttons()

    def __initialise_buttons(self):
        screen_w = Config.SCREEN_WIDTH
        maps_section_x = (screen_w // 2) - Config.MENU_CONTROLS_WIDTH
        config_section_x = (screen_w // 2) + 40
        
        # Title
        self.__buttons_dict["title"] = Button(Config.MENU_TITLE_X, Config.MENU_TITLE_Y, f"{Config.IMAGES_FOLDER}/title.png", 1)

        # Section headers
        self.__buttons_dict["maps_title"] = Button(maps_section_x, Config.MENU_HEADERS_Y, f"{Config.IMAGES_FOLDER}/maps_title.png", 0.5)
        self.__buttons_dict["config_title"] = Button(config_section_x, Config.MENU_HEADERS_Y, f"{Config.IMAGES_FOLDER}/config_title.png", 0.5)

        # Map section
        self.__buttons_dict["create_map"] = Button(maps_section_x, Config.MENU_CONTROLS_Y, f"{Config.IMAGES_FOLDER}/create_map_button.png", 0.4)
        self.__buttons_dict["load_map"] = Button(maps_section_x, Config.MENU_CONTROLS_Y + 90, f"{Config.IMAGES_FOLDER}/load_map_button.png", 0.4)

        # Run button
        self.__buttons_dict["run"] = Button((screen_w // 2) - 114, Config.MENU_RUN_Y + 100, f"{Config.IMAGES_FOLDER}/run_button.png", 0.3)

    def __button_action(self, button_id):
        if button_id == "run":
            if not self.__sim.is_map_loaded():
                print("No map loaded")
            self.__sim.set_game_state("simulation")
        elif button_id == "create_map":
            self.__sim.get_map_builder().reset()
            self.__sim.set_game_state("map_builder")
        elif button_id == "load_map":
            self.__open_load_dialog()
            # Show file selector
            
            
        elif button_id == "title":
            pass
        else:
            print("Button ID not matched")

    def __open_load_dialog(self):
        if self.__load_dialog is not None:
            self.__load_dialog.kill()

        gui_manager = self.__sim.get_gui_manager()

        dialog_rect = pyg.Rect((Config.SCREEN_WIDTH // 2 - 400, Config.SCREEN_HEIGHT // 2 - 180), Config.LOAD_DIALOG_SIZE)

        maps_path = os.path.join(os.getcwd(), Config.MAPS_FOLDER)

        self.__load_dialog = pygui.windows.ui_file_dialog.UIFileDialog(
            rect=dialog_rect,
            manager=gui_manager,
            window_title="Load Map",
            initial_file_path=os.path.join(maps_path, ""),
            allow_picking_directories=False,
            allow_existing_files_only=True, 
            allowed_suffixes={'.json'},
            object_id="#load_map_dialog"
        )

    def handle_load_path(self, path):
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return
        
        if not path.lower().endswith('.json'):
            print("Select a .json file")
            return
        
        success, data, error = JSONManager.load_map(path)

        if success:
            json_manager = JSONManager(self.__sim)
            json_manager.import_map(data)
            self.__sim.map_loaded()
            self.__sim.set_game_state("map_builder")

        else:
            print(f"Load failed with: {error}")

    def render_menu(self, screen):
        screen.fill(Config.SCREEN_COLOUR)

        # Draw all buttons
        for button_id, button in self.__buttons_dict.items():
            if button.draw(screen):
                self.__button_action(button_id)

class Button():
    def __init__(self, x, y, normal_path, scale, selected_path=None):
        self.__normal_img = self.__load_img(normal_path, scale)
        self.__selected_img = self.__load_img(selected_path, scale) if selected_path else self.__normal_img
        
        self.__image = self.__normal_img
        self.__rect = self.__image.get_rect()
        self.__rect.topleft = (x, y)
        self.__clicked = False

    def __load_img(self, path, scale):
        image = pyg.image.load(path).convert_alpha()
        w = image.get_width()
        h = image.get_height()
        return pyg.transform.scale(image, (int(w * scale), int(h * scale)))

    def set_selected(self, selected):
        self.__image = self.__selected_img if selected else self.__normal_img

    def draw(self, surface):
        action = False
        mouse_pos = pyg.mouse.get_pos()

        if self.__rect.collidepoint(mouse_pos):
            if pyg.mouse.get_pressed()[0] == 1 and self.__clicked == False:
                self.__clicked = True
                action = True

        if pyg.mouse.get_pressed()[0] == 0:
            self.__clicked = False

        surface.blit(self.__image, (self.__rect.x, self.__rect.y))
        return action

class MapBuilder():
    def __init__(self, sim):
        self.__sim = sim
        self.__jsonmanager = JSONManager(sim)

        self.__tracing_img = None
        self.__tracing_img_path = None

        # Create temporary object containers 
        self.__builder_boundaries = []
        self.__builder_assembly = None
        self.__builder_boids = []

        # Manage tool states
        self.__current_tool = None
        self.__drawing_wall = False
        self.__wall_start = None

        # UI buttons? TODO
        self.__tool_buttons = {}
        self.__confirm_buttons = {}
        self.__create_map_buttons()

        # Instantiate file manager
        self.__file_manager = FileManager(self.__sim)

        # Dialog managers
        self.__save_dialog = None
        self.__load_dialog = None

    # Resets map builder variables
    def reset(self):
        self.__builder_boundaries = []
        self.__builder_assembly = None
        self.__builder_boids = []
        self.__tracing_img = None
        self.__tracing_img_path = None
        self.__current_tool = None
        self.__drawing_wall = False
        self.__wall_start = None

        self.__save_dialog = None
        self.__sim.map_unloaded()

    def set_boundaries(self, lst):
        self.__builder_boundaries = lst

    def set_assembly(self, point):
        self.__builder_assembly = point

    def set_boids(self, lst):
        self.__builder_boids = lst

    def __create_map_buttons(self):
        tools_list = [
            ("import_img", f"{Config.IMAGES_FOLDER}/add_image_tool.png", 0),
            ("wall", f"{Config.IMAGES_FOLDER}/wall_tool.png", 1),
            ("assembly", f"{Config.IMAGES_FOLDER}/assembly_tool.png", 2),
            ("boid", f"{Config.IMAGES_FOLDER}/boid_tool.png", 3),
            ("eraser", f"{Config.IMAGES_FOLDER}/eraser_tool.png", 4)
        ]
        
        for id, img, i in tools_list:
            y = Config.TOOLS_Y + (i * Config.TOOLS_MARGIN)
            self.__tool_buttons[id] = Button(Config.TOOLS_X, y, img, 0.5, selected_path=f"{img.split('.')[0]}_selected.png")

        self.__confirm_buttons["confirm"] = Button(Config.CONFIRM_X, Config.CONFIRM_Y, f"{Config.IMAGES_FOLDER}/confirm_button.png", 0.3)
        self.__confirm_buttons["cancel"] = Button(Config.CONFIRM_X - 55, Config.CONFIRM_Y, f"{Config.IMAGES_FOLDER}/cancel_button.png", 0.3)

    def tool_click(self, id):
        if id == "import_img":
            self.__import_image()

        elif id == self.__current_tool:
            self.__current_tool = None
            self.__drawing_wall = False

        else:
            self.__current_tool = id
            self.__drawing_wall = False

    def confirm_click(self, id):
        if id == "confirm":
            if not self.__builder_assembly:
                print("Must place assembly point")
                return
            
            elif len(self.__builder_boids) == 0:
                print("Must place at least one boid")
                return
            
            self.__sim.import_objects_to_sim(self.__builder_boundaries, self.__builder_assembly, self.__builder_boids)

            if self.__sim.is_map_loaded():
                self.__sim.set_game_state("menu")
                return
            
            if self.__save_dialog is None:
                self.__open_save_dialog()
                return
        
            file_input = self.__save_dialog.get_text().strip()
            self.__handle_save_path(file_input)


        elif id == "cancel":
            self.reset()
            self.__sim.map_unloaded()
            self.__sim.set_game_state("menu")

    def __open_save_dialog(self):
        if self.__save_dialog is not None:
            self.__save_dialog.kill()

        gui_manager = self.__sim.get_gui_manager()

        dialog_rect = pyg.Rect((Config.SCREEN_WIDTH // 2 + 208, Config.SCREEN_HEIGHT - 78), Config.SAVE_DIALOG_SIZE)
        self.__save_dialog = pygui.elements.UITextEntryLine(relative_rect=dialog_rect, manager=gui_manager, object_id="#save_file_path")
        self.__save_dialog.set_text("map.json")

    def __handle_save_path(self, path):
        if self.__save_dialog is None:
            print("No path entered")
            return

        if not path.endswith('.json'):
            path += '.json'

        maps_dir = os.path.join(os.getcwd(), Config.MAPS_FOLDER)
        if maps_dir and not os.path.exists(maps_dir):
            try:
                os.makedirs(maps_dir)
            except Exception as e:
                print(f"Error creating directory:\n{str(e)}")
                return
            
        path = os.path.join(maps_dir, path)
            
        success, error = self.__jsonmanager.save_map(path, self.__builder_boundaries, self.__builder_assembly, self.__builder_boids, self.__tracing_img_path)

        self.__save_dialog.kill()

        if success:
            self.__sim.set_game_state('menu')
        else:
            print(f"Save failed: {error}")
            self.__sim.set_game_state("menu")

    def __import_image(self):
        self.__file_manager.create_file_explorer()

    def handle_image(self, path):
        if path:
            self.__tracing_img_path = path
            try:
                # Original image file
                original = pyg.image.load(path).convert_alpha()

                # Image file scaled to fit on screen
                scaled = self.__scale_image(original)

                # Filter applied to image
                filtered = self.__apply_filter(scaled)
                self.__tracing_img = filtered

            except Exception as exception:
                print(f"Error loading image with error: {exception}")

    def __scale_image(self, img):
        img_w, img_h = img.get_size()
        
        max_w = Config.SCREEN_WIDTH - (2 * Config.IMAGE_MARGIN_X)
        max_h = Config.SCREEN_HEIGHT - (2 * Config.IMAGE_MARGIN_Y)

        scale_w = max_w / img_w
        scale_h = max_h / img_h
        scale = min(scale_w, scale_h)

        width = int(img_w * scale)
        height = int(img_h * scale)

        return pyg.transform.smoothscale(img, (width, height))

    def __apply_filter(self, img):
        traced_img = img.copy()

        overlay = pyg.Surface(traced_img.get_size(), pyg.SRCALPHA)
        overlay.fill((255, 255, 255, 120))
        traced_img.blit(overlay, (0, 0))

        traced_img.set_alpha(180)

        return traced_img

        # TODO: Add filter over image for 'tracing paper' effect

    def handle_click(self, pos, button):
        if self.__current_tool == "wall":
            self.__use_wall_tool(pos, button)

        elif self.__current_tool == "assembly":
            self.__use_assembly_tool(pos)

        elif self.__current_tool == "boid":
            self.__use_boid_tool(pos)

        elif self.__current_tool == "eraser":
            self.__use_erase_tool(pos)

    def __use_wall_tool(self, pos, button):
        if button == 1:
            if not self.__drawing_wall:
                self.__wall_start = pyg.math.Vector2(pos)
                self.__drawing_wall = True
            else:
                self.wall_end(pyg.math.Vector2(pos))
                self.__wall_start = pyg.math.Vector2(pos)
                self.__drawing_wall = True

    def wall_end(self, pos, esc=False):
        if self.__drawing_wall and self.__wall_start is not None:
            if not esc:
                wall_end = pyg.math.Vector2(pos)

                if self.__wall_start.distance_squared_to(wall_end) > 5 ** 2: # Squared function for efficiency
                    new_boundary = Boundary((self.__wall_start, wall_end))
                    self.__builder_boundaries.append(new_boundary)
                else:
                    print("Wall too short")

            self.__drawing_wall = False
            self.__wall_start = None

    def __use_assembly_tool(self, pos):
        self.__builder_assembly = AssemblyPoint(pos)

    def __use_boid_tool(self, pos):
        new_boid = Boid(self.__sim)
        new_boid.set_pos(pyg.math.Vector2(pos))
        self.__builder_boids.append(new_boid)

    def __use_erase_tool(self, pos):
        for boundary in self.__builder_boundaries[:]:
            if self.__near_boundary(pos, boundary, Config.ERASE_RADIUS):
                self.__builder_boundaries.remove(boundary)
                return
        
        if self.__builder_assembly:
            if pyg.math.Vector2(pos).distance_squared_to(self.__builder_assembly.get_pos()) < (Config.ERASE_RADIUS ** 2):
                self.__builder_assembly = None
                return
            
        for boid in self.__builder_boids[:]:
            if boid.get_pos().distance_squared_to(pyg.math.Vector2(pos)) < (Config.ERASE_RADIUS ** 2):
                self.__builder_boids.remove(boid)
                return

    def __near_boundary(self, point, boundary, radius):
        start, end = boundary.get_pos()
        line = end - start
        point = pyg.math.Vector2(point) - start

        length_squared = line.length_squared()
        if length_squared < 0.01:
            return start.distance_to(pyg.math.Vector2(point)) < radius
        
        t = max(0, min(1, point.dot(line) / length_squared))
        closest = line * t

        return closest.distance_to(pyg.math.Vector2(point)) < radius

    def render_builder(self, screen):
        screen.fill(Config.SCREEN_COLOUR)

        # Render image to trace
        if self.__tracing_img:
            img_rect = self.__tracing_img.get_rect(center=(Config.SCREEN_WIDTH // 2 + 60, Config.SCREEN_HEIGHT // 2))
            screen.blit(self.__tracing_img, img_rect)

        for boundary in self.__builder_boundaries:
            boundary.draw(screen)
            # boundary.draw_expanded(screen)

        if self.__builder_assembly:
            self.__builder_assembly.draw(screen)

        for boid in self.__builder_boids:
            boid.draw(screen)

        # Draw buttons
        for button_id, button in self.__tool_buttons.items():
            button.set_selected(button_id == self.__current_tool)
            if button.draw(screen):
                self.tool_click(button_id)

        for button_id, button in self.__confirm_buttons.items():
            if button.draw(screen):
                self.confirm_click(button_id)

    def get_tool_buttons(self):
        return self.__tool_buttons

    def get_boundaries(self):
        return self.__builder_boundaries

    def get_assembly_point(self):
        return self.__builder_assembly
    
    def get_boids(self):
        return self.__builder_boids
    
    def set_tracing_image(self, img):
        self.__tracing_img = img

class FileManager():
    def __init__(self, sim):
        self.__sim = sim

    def create_file_explorer(self):
        gui_manager = self.__sim.get_gui_manager()
        file_rect = pyg.Rect((260, 215), (600, 380))
        file_explorer = pygui.windows.ui_file_dialog.UIFileDialog(rect=file_rect, manager=gui_manager, window_title="Choose a map image", initial_file_path=".", allowed_suffixes={'.png', '.jpeg ', '.jpg'}, object_id="#file_explorer")
        file_explorer.resizable = False

        return None

class JSONManager():
    def __init__(self, sim):
        self.__sim = sim

    @staticmethod
    def save_map(path, boundaries, assembly, boids, img_path=None):
        try:
            if not path.lower().endswith('.json'):
                path += '.json'

            map_data = {
                "map_name": os.path.basename(path).split(".")[0],
                "created": datetime.datetime.now().isoformat(),
                "map_image": img_path,
                "assembly_point": {
                    "x": int(assembly.get_pos()[0]),
                    "y": int(assembly.get_pos()[1]),
                },
                "boundaries": [],
                "boids": []
            }

            # Add boundaries to JSON
            for boundary in boundaries:
                start, end = boundary.get_pos()
                map_data["boundaries"].append({
                    "start": {
                        "x": int(start[0]),
                        "y": int(start[1])
                    },
                    "end": {
                        "x": int(end[0]),
                        "y": int(end[1])
                    }
                })

            # Add boids to JSON
            for boid in boids:
                pos = boid.get_pos()
                map_data["boids"].append({
                    "x": int(pos[0]),
                    "y": int(pos[1])
                })

            # Write to file
            with open(path, 'w') as file:
                json.dump(map_data, file)

            return (True, None)

        except PermissionError:
            return (False, f"Insufficient permission to write to {path}")
        except IOError as e:
            return (False, f"File write error: {str(e)}")
        except Exception as e:
            return (False, f"An unexpected error occurred: {str(e)}")
        
    @staticmethod
    def load_map(path):
        try:
            if not os.path.exists(path):
                return (False, None, f"File could not be found at: {path}")

            if not path.lower().endswith('.json'):
                return (False, None, f"File must end with .json")
            
            with open(path, 'r') as file:
                map_data = json.load(file)

            # Validate loaded data
            is_valid = JSONManager.__validate_data(map_data)
            if not is_valid[0]:
                return (False, None, is_valid[1]) # Return error message
            
            # Parse data
            parsed_data = {
                "boundaries": [],
                "assembly_point": None,
                "boids": [],
                "map_image": map_data.get("map_image", None)
            }

            # Assembly point
            parsed_data["assembly_point"] = (map_data["assembly_point"]["x"], map_data["assembly_point"]["y"])

            # Boundaries
            for boundary in map_data["boundaries"]:
                start = (boundary["start"]["x"], boundary["start"]["y"])
                end = (boundary["end"]["x"], boundary["end"]["y"])
                parsed_data["boundaries"].append((start, end))


            # Boids
            for boid in map_data["boids"]:
                parsed_data["boids"].append((boid["x"], boid["y"]))

            return (True, parsed_data, None)

        except json.JSONDecodeError as e:
            return (False, None, f"Invalid JSON format: {str(e)}")
        except PermissionError:
            return (False, None, f"Insufficient permission to read from {path}")
        except IOError as e:
            return (False, None, f"File read error: {str(e)}")
        except Exception as e:
            return (False, None, f"An unexpected error occurred: {str(e)}")
        
    @staticmethod
    def __validate_data(data):
        return (True, None)
    
    def import_map(self, data):
        boundaries = data["boundaries"]
        assembly = data["assembly_point"]
        boids = data["boids"]
        tracing_image = data["map_image"]
        self.__sim.import_objects_to_builder(boundaries,  assembly, boids, tracing_image)

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

        pos = self.get_pos()

        if pos.x > window.w:
            pos.x -= window.w
        elif pos.x < 0:
            pos.x += window.w

        if pos.y > window.h:
            pos.y -= window.h
        elif pos.y < 0:
            pos.y += window.h
        
class Boid(BoidObject):
    def __init__(self, sim):
        pos = (random.randint(int(Config.SCREEN_WIDTH / Config.GENERATION_MARGIN), int((Config.SCREEN_WIDTH / Config.GENERATION_MARGIN) * (Config.GENERATION_MARGIN - 1))), random.randint(int(Config.SCREEN_HEIGHT / Config.GENERATION_MARGIN), int((Config.SCREEN_HEIGHT / Config.GENERATION_MARGIN) * (Config.GENERATION_MARGIN - 1))))
        super().__init__(sim, pos)
        self._max_speed = Config.MAX_SPEED
        self._vel = pyg.math.Vector2(1, 1)
        self._reached_target = False

    def get_pos(self):
        return self._pos
    
    def set_pos(self, value):
        self._pos = value

    def get_vel(self):
        return self._vel

    def draw(self, screen):
        # Calculate points of the triangle
        phi = math.atan2(self._vel.y, self._vel.x)
        phi2 = 0.75 * math.pi

        pos = self.get_pos()

        pos1 = ((pos.x + (math.cos(phi) * Config.BOID_SIZE), (pos.y + (math.sin(phi) * Config.BOID_SIZE))))
        pos2 = ((pos.x + (math.cos(phi + phi2) * Config.BOID_SIZE), (pos.y + (math.sin(phi + phi2) * Config.BOID_SIZE))))
        pos3 = ((pos.x + (math.cos(phi - phi2) * Config.BOID_SIZE), (pos.y + (math.sin(phi - phi2) * Config.BOID_SIZE))))

        pyg.draw.polygon(screen, Config.BOID_COLOUR, (pos1, pos2, pos3))


    def step(self):
        seeking_factor = 0
        if self._sim.get_assembly_point() is not None:
            # Check target position
            target = self._sim.get_assembly_point().get_pos()
            # Find distance from target
            target_vector = target - self.get_pos()
            distance_to_target = target_vector.length()
        
            # If great distance from target, reduce seeking 
            # If near to target, increase seeking
            if distance_to_target > 300:
                seeking_factor = 0.2
            elif distance_to_target > 100:
                seeking_factor = 0.4
            else:
                seeking_factor = 0.8

        self._acc += self.__avoid_boundary() * self._sim.get_config_value("avoidance")
        self._acc += self.__avoid_predator() * self._sim.get_config_value("avoidance")
        self._acc += self.__separation() * self._sim.get_config_value("separation")
        self._acc += self.__seeking() * seeking_factor
        self._acc += self.__alignment() * self._sim.get_config_value("alignment")
        self._acc += self.__cohesion() * self._sim.get_config_value("cohesion")
        super().step()

        # Increment positions by velocity
        self.__move()
        
    def __move(self):
        # Ensure velocity doesn't exceed max velocity
        if self._vel.length_squared() > (Config.MAX_SPEED ** 2):
            self._vel.scale_to_length(Config.MAX_SPEED)

        self.set_pos(self.get_pos() + self._vel)

    def __avoid_predator(self):
        acc_request = pyg.math.Vector2(0, 0)
        nearby_predators = self.__predators_in_radius(self._sim.get_config_value("predator_range"))

        if len(nearby_predators) == 0:
            return acc_request
        
        for predator in nearby_predators:
            try:
                dist_delta = self.get_pos() - predator.get_pos()
                acc_request += (dist_delta) * (self._sim.get_config_value("predator_range") / self.get_pos().distance_to(predator.get_pos()))
            except ZeroDivisionError:
                return acc_request
            
        return self.__limit_force(acc_request, nearby_predators)
    
    def __avoid_boundary(self):
        acc_request = pyg.math.Vector2(0, 0)
        nearby_boundaries = self.__boundaries_in_radius()

        if len(nearby_boundaries) == 0:
            return acc_request

        for boundary in nearby_boundaries:
            will_collide, collision_point = boundary.will_collide(self)

            print(f"Will collide: {will_collide} // Collision point: {collision_point}")

            # Check if a collision is due in the next frame
            if will_collide:
                reverse_vector = self.get_pos() - collision_point

                try:
                    reverse_vector.normalize_ip()
                    acc_request += reverse_vector * (self._sim.get_config_value("boundary_range") * 5)

                except ZeroDivisionError:
                    acc_request += boundary.get_perpendicular_vector() * self._sim.get_config_value("boundary_range")

                return self.__limit_force(acc_request, nearby_boundaries)
            
            else:
                closest_point = self.__distance_to_closest_boundary_point(boundary)

                try:
                    dist_delta = self.get_pos() - closest_point
                    distance = self.get_pos().distance_to(closest_point)

                    print(f"Delta: {dist_delta} // Distance: {distance}")
                    acc_request += dist_delta * (self._sim.get_config_value("boundary_range") / distance)

                except ZeroDivisionError:
                    acc_request += boundary.get_perpendicular_vector() * self._sim.get_config_value("boundary_range")
            
                return self.__limit_force(acc_request, nearby_boundaries)

    def __separation(self):
        acc_request = pyg.math.Vector2(0, 0)
        neighbouring_boids = self.__boids_in_radius(self._sim.get_config_value("protected_range"))

        if len(neighbouring_boids) == 0:
            return acc_request

        for neighbour in neighbouring_boids:
            try:
                dist_delta = self.get_pos() - neighbour.get_pos()
                acc_request += (dist_delta) * (self._sim.get_config_value("protected_range") / self.get_pos().distance_to(neighbour.get_pos()))
            except ZeroDivisionError:
                continue

        return self.__limit_force(acc_request, neighbouring_boids)

    def __alignment(self):
        acc_request = pyg.math.Vector2(0, 0)
        neighbouring_boids = self.__boids_in_radius(self._sim.get_config_value("visual_range"))

        if len(neighbouring_boids) == 0:
            return acc_request
        
        for neighbour in neighbouring_boids:
            acc_request += neighbour._vel

        if acc_request.length_squared() == 0:
            return acc_request
        
        return self.__limit_force(acc_request, neighbouring_boids)

    def __cohesion(self):
        acc_request = pyg.math.Vector2(0, 0)
        neighbouring_boids = self.__boids_in_radius(self._sim.get_config_value("visual_range"))

        if len(neighbouring_boids) == 0:
            return acc_request
        
        for neighbour in neighbouring_boids:
            acc_request += (neighbour.get_pos() - self.get_pos())

        if acc_request.length_squared() == 0:
            return acc_request
        
        return self.__limit_force(acc_request, neighbouring_boids)
    
    def __seeking(self):
        acc_request = pyg.math.Vector2(0, 0)
        assembly_point = self._sim.get_assembly_point()

        if assembly_point is None:
            return acc_request
        
        assembly_vector = assembly_point.get_pos() - self.get_pos()
        dist = assembly_vector.length()

        if dist < Config.ARRIVED_RADIUS:
            self._reached_target = True
            return acc_request

        if dist < Config.ARRIVAL_SLOWING_RADIUS:
            speed = self._max_speed * (dist / Config.ARRIVAL_SLOWING_RADIUS)
        else:
            speed = self._max_speed

        # Normalise to create a direction vector
        if assembly_vector.length_squared() > 0:
            assembly_vector.normalize_ip()
        else:
            return self.__limit_force(acc_request, [self])
        
        # Scale to maximum speed value
        acc_request = assembly_vector * (speed * 0.2)

        # Subtract current velocity for steering force
        acc_request -= self._vel

        return acc_request * Config.DEFAULT_SEEKING_FACTOR

    def __boids_in_radius(self, radius):
        boids_present = []
        for surrounding_boid in self._sim.get_boid_container():
            if surrounding_boid == self:
                pass
            else:
                if self.get_pos().distance_to(surrounding_boid.get_pos()) < radius:
                    boids_present.append(surrounding_boid)
            
        return boids_present
    
    def __predators_in_radius(self, radius):
        predators_present = []
        for potential_predator in self._sim.get_predator_container():
          if self.get_pos().distance_to(potential_predator.get_pos()) < radius:
                    predators_present.append(potential_predator)
            
        return predators_present
    
    def __boundaries_in_radius(self):
        boundaries_present = []
        for boundary in self._sim.get_boundary_container():
            if boundary.check_collision(self):
                boundaries_present.append(boundary)

        return boundaries_present
    
    def __distance_to_closest_boundary_point(self, boundary):
        boundary_vector = boundary.get_boundary_vector()
        point_vector = boundary.get_point_vector(self.get_pos())

        boundary_length_squared = boundary_vector.length_squared()

        if boundary_length_squared < 0.01:
            return boundary.get_pos()[0]
        
        t = point_vector.dot(boundary_vector) / boundary_length_squared
        t = max(0, min(1, t)) # Ensure t remains between 0 and 1

        return boundary.get_pos()[0] + (boundary_vector * t)

    def __limit_force(self, force, boids_in_radius):
        force /= len(boids_in_radius)
        if round(force.length(), 3) <= 0:
            return force

        force.scale_to_length(1)
        force = force * self._max_speed - self._vel

        if force.length_squared() > (Config.MAX_ACC_REQUEST ** 2):
            force.scale_to_length(Config.MAX_ACC_REQUEST)
        
        return force

class Predator(BoidObject):
    def __init__(self, sim, pos):
        super().__init__(sim, pos)

    def draw(self, screen):
        pyg.draw.circle(screen, Config.PREDATOR_COLOUR, self.get_pos(), Config.PREDATOR_SIZE)

    def step(self):
        pass

    def get_pos(self):
        return self._pos

class BoundaryManager():
    def __init__(self, sim):
        self.__current_start_pos = None
        self.__sim = sim

    def set_start_pos(self, pos):
        self.__current_start_pos = pos

    def get_start_pos(self):
        return self.__current_start_pos
    
    def clear_start_pos(self):
        self.__current_start_pos = None

class Boundary():
    def __init__(self, pos):
        self.__pos = pos
        self.__expanded_points = []

        self.expand(Config.BOUNDARY_RADIUS)
        
    def draw(self, screen):
        self.__rect = pyg.draw.line(screen, Config.PREDATOR_COLOUR, self.__pos[0], self.__pos[1], Config.BOUNDARY_THICKNESS)

    def draw_expanded(self, screen):
        pyg.draw.polygon(screen, Config.BOID_COLOUR, self.__expanded_points, 1)

        expanded_rect = pyg.Rect(1, 1, 1, 1)
        expanded_rect.topleft = self.__expanded_points[0]
        expanded_rect.topright = self.__expanded_points[1]
        expanded_rect.bottomright = self.__expanded_points[2]
        expanded_rect.bottomleft = self.__expanded_points[3]

        # pyg.draw.rect(screen, Config.BOID_COLOUR, expanded_rect, 1)

    def expand(self, radius):
        start_vector = self.__pos[0]
        end_vector = self.__pos[1]
        direction_vector = (end_vector - start_vector).normalize()

        perpendicular_vector = pyg.math.Vector2.rotate(direction_vector, 90)

        offset = perpendicular_vector * radius
        top_left = start_vector + pyg.math.Vector2.rotate(offset, 45)
        top_right = end_vector + pyg.math.Vector2.rotate(offset, -45)
        bottom_left = start_vector - pyg.math.Vector2.rotate(offset, -45)
        bottom_right = end_vector - pyg.math.Vector2.rotate(offset, 45)

        self.__expanded_points = [top_left, top_right, bottom_right, bottom_left]

    def get_expanded_points(self):
        return self.__expanded_points

    def get_pos(self):
        return self.__pos
    
    def get_boundary_vector(self):
        return self.__pos[1] - self.__pos[0]
    
    def get_point_vector(self, point):
        return point - self.__pos[0]
    
    def get_perpendicular_vector(self):
        return pyg.math.Vector2.rotate(self.get_boundary_vector().normalize(), 90)
    
    def check_collision(self, boid):
        point = boid.get_pos()

        # Confirm boundary has been expanded
        if len(self.__expanded_points) != 4:
            return False
        
        for i in range(4):
            vertex_a = self.__expanded_points[i]
            vertex_b = self.__expanded_points[(i + 1) % 4]

            boundary_edge_vector = vertex_b - vertex_a
            point_vector = point - vertex_a

            cross_product = (boundary_edge_vector.x * point_vector.y) - (boundary_edge_vector.y * point_vector.x)
            
            if cross_product > 0:
                return False

        return True
    
    def will_collide(self, boid):
        current_pos = boid.get_pos()
        next_pos = boid.get_pos() + boid.get_vel()

        closest_point = None
        min_distance = float('inf')

        for i in range(4):
            line_start = self.__expanded_points[i]
            line_end = self.__expanded_points[(i + 1) % 4]

            intersect = self.__lines_intersect(current_pos, next_pos, line_start, line_end)

            if intersect is not None:
                distance = boid.get_pos().distance_squared_to(intersect)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = intersect

        # Check whether the boid path for the next frame intersects a line 
        return (closest_point is not None, closest_point)
    
    def __lines_intersect(self, p1, p2, p3, p4):
        # Check boundary has been expanded
        if len(self.__expanded_points) != 4:
            return (False, None)
        
        # P1/P2 = projected motion
        # P3/P4 = boundary edge

        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if den == 0:
            return
 
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den

        if 0 < t < 1 and 0 < u < 1:
            return pyg.Vector2(x1 + t * (x2 - x1), y1 + t * (y2 - y1))

class AssemblyPoint():
    def __init__(self, pos):
        self.__pos = pos

    def get_pos(self):
        return self.__pos

    def draw(self, screen):
        pyg.draw.circle(screen, Config.ASSEMBLY_COLOUR, self.__pos, Config.ASSEMBLY_SIZE)

if __name__ == '__main__':
    sim = Sim()
    sim.run()