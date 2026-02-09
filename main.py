import pygame as pyg
import pygame_gui as pygui
import math
import abc
import os
import datetime
import json
from enum import Enum

class Config:
    # File locations
    IMAGES_FOLDER = "images"
    MAPS_FOLDER = "maps"

    # Sim constants
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 800
    SCREEN_COLOUR = (0, 0, 0)
    FPS = 60

    # Boid constants
    NUMBER_OF_BOIDS = 150
    BOID_SIZE = 3
    ASSEMBLY_SIZE = 20
    EXIT_SIZE = 10
    DESTINATION_SIZE = 5
    BOUNDARY_THICKNESS = 3
    BOUNDARY_RADIUS = 5
    BOID_COLOUR = (255, 255, 255)
    BOUNDARY_COLOUR = (255, 255, 255)
    ASSEMBLY_COLOUR = (239, 71, 111)
    EXIT_COLOUR = (6, 214, 160)
    DESTINATION_COLOUR = (255, 209, 102)
    EDGE_COLOUR = (220, 220, 220)

    # Movement values
    MAX_SPEED = 0.7
    MAX_ACC_REQUEST = 0.15

    # Slider values
    DEFAULT_VISUAL_RANGE = 100
    DEFAULT_PROTECTED_RANGE = 10
    DEFAULT_BOUNDARY_RANGE = 5
    DEFAULT_SEPARATION_FACTOR = 2
    DEFAULT_SEEKING_FACTOR = 1
    DEFAULT_ALIGNMENT_FACTOR = 1
    DEFAULT_COHESION_FACTOR = 1
    DEFAULT_AVOIDANCE_FACTOR = 10
    ARRIVAL_SLOWING_RADIUS = 100
    ARRIVED_RADIUS = 5
    GRAPH_EDGE_RADIUS = 150

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
    TOOLS_X = 35
    TOOLS_Y = 130
    TOOLS_MARGIN = 80
    CONFIRM_X = SCREEN_WIDTH - 90
    CONFIRM_Y = SCREEN_HEIGHT - 80
    IMAGE_MARGIN_X = 120
    IMAGE_MARGIN_Y = 100
    ERASE_RADIUS = 12

    # Playback controls layout
    PLAYBACK_Y = SCREEN_HEIGHT - 80
    PLAYBACK_X = SCREEN_WIDTH - 90
    PLAYBACK_SPACING = 60

class GameState(Enum):
    MENU = "menu"
    MAP_BUILDER = "map_builder"
    SIMULATION = "simulation"

class PlaybackControls:
    def __init__(self, sim):
        self.__sim = sim
        self.__is_running = True

        self.__control_buttons = {}

        self.__control_buttons["play"] = Button(Config.PLAYBACK_X, Config.PLAYBACK_Y, f"{Config.IMAGES_FOLDER}/play_button.png", 0.3)
        self.__control_buttons["pause"] = Button(Config.PLAYBACK_X, Config.PLAYBACK_Y, f"{Config.IMAGES_FOLDER}/pause_button.png", 0.3)
        self.__control_buttons["step"] = Button(Config.PLAYBACK_X - Config.PLAYBACK_SPACING, Config.PLAYBACK_Y, f"{Config.IMAGES_FOLDER}/step_button.png", 0.3)

    def draw_buttons(self, screen):
        gui_active = self.__sim.get_gui().get_active()

        if self.__is_running:
            if self.__control_buttons["pause"].draw(screen, gui_active):
                self.pause()
        else:
            if self.__control_buttons["play"].draw(screen, gui_active):
                self.play()
            if self.__control_buttons["step"].draw(screen, gui_active):
                self.step()

    def is_running(self):
        return self.__is_running

    def play(self):
        self.__is_running = True

    def pause(self):
        self.__is_running = False

    def step(self):
        self.__sim.step()

class GUI:
    def __init__(self, sim):
        self.__sim = sim
        self.__window = self.__sim.get_window()
        self.__manager = pygui.UIManager((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))

        self.__gui_margin = (10, 20)
        self.__slider_size = (150, 40)
        self.__gui_sliders = 5
        self.__slider_moving = False
        
        self.__active_gui = False

        self.__slider_keys = ["protected_range", "visual_range", "separation", "alignment", "cohesion"]
        self.__sliders = {"protected_range": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_PROTECTED_RANGE, value_range=(2, 100), manager=self.__manager), 
                          "visual_range": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_VISUAL_RANGE, value_range=(50, 300), manager=self.__manager),
                          "separation": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_SEPARATION_FACTOR, value_range=(0.1, 5), manager=self.__manager),
                          "alignment": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_ALIGNMENT_FACTOR, value_range=(0.1, 5), manager=self.__manager),
                          "cohesion": pygui.elements.UIHorizontalSlider(relative_rect=pyg.Rect((0,0), self.__slider_size), start_value=Config.DEFAULT_COHESION_FACTOR, value_range=(0.1, 5), manager=self.__manager)}
        self.__slider_labels = {"protected_range": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Protected Range: {Config.DEFAULT_PROTECTED_RANGE}"),
                                 "visual_range": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Visual Range: {Config.DEFAULT_VISUAL_RANGE}"),
                                 "separation": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Separation: {Config.DEFAULT_SEPARATION_FACTOR:.2f}"),
                                 "alignment": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Alignment: {Config.DEFAULT_ALIGNMENT_FACTOR:.2f}"),
                                 "cohesion": pygui.elements.UILabel(relative_rect=pyg.Rect((0,0), self.__slider_size), text=f"Cohesion: {Config.DEFAULT_COHESION_FACTOR:.2f}")}

        self.set_gui_layout("menu")

    def process_gui_event(self, event):
        self.__manager.process_events(event)

    def update_gui(self, time_delta):
        self.__manager.update(time_delta)

    def render_gui(self, screen):
        self.__manager.draw_ui(screen)

    def get_active(self):
        return self.__active_gui
    
    def get_slider_label(self, slider):
        return self.__slider_labels[slider]
    
    def get_slider_size(self):
        return self.__slider_size

    def get_slider(self, slider):
        return self.__sliders[slider]

    def get_gui_manager(self):
        return self.__manager

    def enable_active_gui(self):
        self.__active_gui = True

    def disable_active_gui(self):
        self.__active_gui = False

    def check_slider_moving(self):
        return self.__slider_moving

    def set_gui_layout(self, state):
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
    
class Sim:
    def __init__(self):
        pyg.init()

        # Map state controls
        self.__current_game_state = GameState.MENU
        self.__running = False
        self.__map_loaded = False

        # Window / sim variables
        self.__screen = pyg.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.__window = self.__screen.get_rect()
        self.__clock = pyg.time.Clock()
        self.__gui = GUI(self)
        self.__tracing_img = None

        # Composite objects
        self.__menu = Menu(self)
        self.__map_builder = MapBuilder(self)
        self.__playback_controls = PlaybackControls(self)
        self.__graph = Graph()

        # Instantiate object containers
        self.__assembly_point = None
        self.__boid_container = []
        self.__boundary_container = []

        self.__config_values = {"visual_range": Config.DEFAULT_VISUAL_RANGE, 
                               "protected_range": Config.DEFAULT_PROTECTED_RANGE,
                               "boundary_range": Config.DEFAULT_BOUNDARY_RANGE,
                               "separation": Config.DEFAULT_SEPARATION_FACTOR,
                               "seeking": Config.DEFAULT_SEEKING_FACTOR,
                               "alignment": Config.DEFAULT_ALIGNMENT_FACTOR,
                               "cohesion": Config.DEFAULT_COHESION_FACTOR,
                               "avoidance": Config.DEFAULT_AVOIDANCE_FACTOR}

        # Title and icon
        pyg.display.set_caption("Boids Simulation")
        pyg.display.set_icon(pyg.image.load(f"{Config.IMAGES_FOLDER}/window_icon.png"))

    def import_graph(self, graph):
        self.__graph.load_json(graph)
    
    def import_objects_to_sim(self, boundaries, assembly, boids, img):
        self.reset_simulation()
        self.set_tracing_img(img)
        self.create_boundary_container(boundaries)
        self.create_boid_container(boids)
        self.create_assembly_point(assembly)

    def import_objects_to_builder(self, boundaries, assembly, boids, graph, img_path):
        self.__map_builder.reset()
        self.create_boundary_container(boundaries, True)
        self.create_boid_container(boids, True)
        self.create_assembly_point(assembly, True)
        if graph:
            self.__map_builder.get_builder_graph().load_json(graph)
        self.__map_builder.handle_image(img_path)

    def reset_simulation(self):
        self.__boid_container = []
        self.__boundary_container = []
        self.__assembly_point = None
        self.__graph.clear()

    def enable_pathfinding(self):
        graph = self.__graph

        for boid in self.__boid_container:
            boid.assign_path(graph)

    def mouse_in_boundary(self): 
        # Check mouse position does not exceed screen boundaries and does not fall in forbidden GUI zone
        mpos = pyg.mouse.get_pos()
        if mpos[1] < Config.MOUSE_BOUNDARY_MARGIN:
            return False
        elif mpos[0] == 0 or mpos[0] >= (Config.SCREEN_WIDTH - 1):
            return False
        elif mpos[1] >= (Config.SCREEN_HEIGHT - 1):
            return False
        
        return True
  
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

    def handle_events(self, gui):
            for event in pyg.event.get():
                active_gui = gui.get_active()

                # Check for program killed
                if event.type == pyg.QUIT:
                    self.__running = False

                if event.type == pyg.MOUSEBUTTONDOWN:
                    pass

                if self.__current_game_state == GameState.SIMULATION:
                    # Check left mouse button pressed
                    if pyg.mouse.get_pressed()[0]:
                        if self.mouse_in_boundary():
                            pass

                if self.__current_game_state == GameState.MAP_BUILDER:
                    if event.type == pyg.MOUSEBUTTONDOWN:
                        mouse_pos = pyg.mouse.get_pos()

                        for tool_id, button in self.__map_builder.get_tool_buttons().items():
                            if button.draw(self.__screen, active_gui):
                                self.__map_builder.tool_click(tool_id)
                                return

                        self.__map_builder.handle_click(mouse_pos, event.button)

                # File path selected
                if event.type == pygui.UI_FILE_DIALOG_PATH_PICKED:
                    if event.ui_object_id == "#file_explorer":
                        self.__map_builder.handle_image(event.text)
                    elif event.ui_object_id == "#load_map_dialog":
                        self.__menu.handle_load_path(event.text)

                elif event.type == pygui.UI_WINDOW_CLOSE:
                    gui.disable_active_gui()

                # Check for keypresses to place objects
                if event.type == pyg.KEYDOWN:
                    if active_gui:
                        gui.process_gui_event(event)
                        continue

                    if event.key == pyg.K_SPACE:
                        self.set_game_state("menu")

                    if self.__current_game_state == GameState.MAP_BUILDER:
                        if event.key == pyg.K_ESCAPE:
                            self.__map_builder.wall_end(pyg.mouse.get_pos(), True)

                    if self.__current_game_state == GameState.SIMULATION:
                        pass
                            
                gui.process_gui_event(event)

    def step(self):
        for boid in self.__boid_container:
            boid.step()

    def render(self):
        # Wipe last screen
        self.__screen.fill(Config.SCREEN_COLOUR)

        # Render image before other objects to have at back of screen
        if self.__tracing_img:
            img_rect = self.__tracing_img.get_rect(center=(Config.SCREEN_WIDTH // 2 + 60, Config.SCREEN_HEIGHT // 2))
            self.__screen.blit(self.__tracing_img, img_rect)

        for boid in self.__boid_container:
            boid.draw(self.__screen)

        for boundary in self.__boundary_container:
            boundary.draw(self.__screen)
            # boundary.draw_expanded(self.__screen)
            
        if self.__assembly_point is not None:
            pass
            # self.__assembly_point.draw(self.__screen)

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
                if self.__playback_controls.is_running():
                    self.step()

                self.render()
                self.__playback_controls.draw_buttons(self.__screen)
            
            # Update GUI values
            self.update_gui_values(self.__gui)

            if self.__current_game_state == GameState.MENU:
                self.__menu.render_menu(self.__screen)

            elif self.__current_game_state == GameState.MAP_BUILDER:
                self.__map_builder.render_builder(self.__screen)

            self.__gui.render_gui(self.__screen)
            
            # Swap buffers
            pyg.display.flip()

    def get_config_value(self, type):
        return self.__config_values[type]
    
    def get_graph(self):
        return self.__graph
    
    def get_map_builder(self):
        return self.__map_builder

    def get_window(self):
        return self.__window
    
    def get_gui_manager(self):
        return self.__gui.get_gui_manager()
    
    def get_gui(self):
        return self.__gui
    
    def get_map_loaded(self):
        return self.__map_loaded
    
    def get_assembly_point(self):
        return self.__assembly_point

    def get_boid_container(self):
        return self.__boid_container

    def get_boundary_container(self):
        return self.__boundary_container
    
    def create_assembly_point(self, point, json=False):
        if json:
            self.__map_builder.set_assembly(AssemblyPoint(pyg.math.Vector2(point)))
        else:
            self.__assembly_point = point

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

    def create_boundary_container(self, lst, json=False):
        if json:
            boundaries = []
            for pos in lst:
                boundaries.append(Boundary((pyg.math.Vector2(pos[0]), pyg.math.Vector2(pos[1]))))
            self.__map_builder.set_boundaries(boundaries)
        else:
            for boundary in lst:
                self.__boundary_container.append(boundary)

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

    def set_tracing_img(self, img):
        self.__tracing_img = img 

    def set_map_loaded(self):
        self.__map_loaded = True

    def set_map_unloaded(self):
        self.__map_loaded = False

class Node:
    def __init__(self, pos, type, id):
        self.__pos = pyg.math.Vector2(pos)
        self.__type = type
        self.__id = id
        self.__neighbours = {}

    def draw(self, screen):
        if self.__type == 'exit':
            pyg.draw.circle(screen, Config.EXIT_COLOUR, (int(self.__pos.x), int(self.__pos.y)), Config.EXIT_SIZE)
        elif self.__type == 'destination':
            pyg.draw.circle(screen, Config.DESTINATION_COLOUR, (int(self.__pos.x), int(self.__pos.y)), Config.DESTINATION_SIZE)
        else:
            pyg.draw.circle(screen, Config.ASSEMBLY_COLOUR, (int(self.__pos.x), int(self.__pos.y)), Config.ASSEMBLY_SIZE)

    def get_neighbours(self):
        return self.__neighbours
    
    def get_pos(self):
        return self.__pos
    
    def get_type(self):
        return self.__type
    
    def get_id(self):
        return self.__id
    
    def add_neighbour(self, id, distance):
        self.__neighbours[id] = distance

class Graph:
    def __init__(self):
        self.__nodes = {}
        self.__next_id = 0
        self.__adjacency_list = {}

    def add_node(self, pos, type):
        id = self.__next_id
        self.__next_id += 1

        node = Node(pos, type, id)
        self.__nodes[id] = node
        self.__adjacency_list[id] = {}

        return id

    def add_edge(self, id_a, id_b, bi = True):
        if id_a not in self.__nodes or id_b not in self.__nodes:
            return
        
        node_a = self.__nodes[id_a]
        node_b = self.__nodes[id_b]

        distance = node_a.get_pos().distance_to(node_b.get_pos())

        if not bi:
            self.__adjacency_list[id_a][id_b] = distance
            node_a.add_neighbour(id_b, distance)
        elif bi:
            self.__adjacency_list[id_a][id_b] = distance
            node_a.add_neighbour(id_b, distance)
            self.__adjacency_list[id_b][id_a] = distance
            node_b.add_neighbour(id_a, distance)

    def remove_node(self, id):
        if id in self.__nodes:
            self.__nodes.pop(id)
            self.__adjacency_list.pop(id)

            for neighbours in self.__adjacency_list.values():
                if id in neighbours:
                    neighbours.pop(id)

    def find_nearest_node(self, pos, type):
        remaining_checks = list(self.__nodes.values())

        if type:
            temp = remaining_checks.copy()
            for node in temp:
                if node.get_type() == type:
                    pass
                else:
                    remaining_checks.remove(node)

        if not remaining_checks:
            return None
        
        smallest_dist = float('inf')
        nearest = None
        for node in remaining_checks:
            dist_squared = pos.distance_squared_to(node.get_pos())
            if dist_squared < smallest_dist:
                smallest_dist = dist_squared
                nearest = node

        return nearest.get_id()

    def to_json(self):
        json_dict = {
            "nodes": [{"id": node.get_id(), "pos": (node.get_pos().x, node.get_pos().y), "type": node.get_type()} for node in self.__nodes.values()],
            "edges": [{"start": node_id, "end": neighbour_id, "distance": distance} for node_id, neighbours in self.__adjacency_list.items() for neighbour_id, distance in neighbours.items()],
        }

        return json_dict

    def load_json(self, data):
        self.clear()

        node_map = {}
        for node_data in data["nodes"]:
            id = self.add_node(pyg.math.Vector2(node_data["pos"]), node_data["type"])
            node_map[node_data['id']] = id
        
        edges_done = []
        for edge_data in data["edges"]:
            old_start = edge_data["start"]
            old_end = edge_data["end"]

            start = node_map.get(old_start)
            end = node_map.get(old_end)

            edge_key = (min(start, end), max(start, end))
            if edge_key not in edges_done:
                self.add_edge(start, end, True)
                edges_done.append(edge_key)

    def dijkstra(self, start, end):        
        distances = [float('inf')] * len(self.__nodes)
        previous = [None] * len(self.__nodes)
        distances[start] = 0
        visited = [False] * len(self.__nodes)

        for i in range(len(self.__nodes)):
            min_distance = float('inf')
            u = None
            for j in range(len(self.__nodes)):
                if not visited[j] and distances[j] < min_distance:
                    min_distance = distances[j]
                    u = j

            if u is None:
                break

            visited[u] = True

            for v in range(len(self.__nodes)):
                if v in self.__adjacency_list[u] and not visited[v]:
                    new_dist = distances[u] + self.__adjacency_list[u][v]
                    if new_dist < distances[v]:
                        distances[v] = new_dist
                        previous[v] = u

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
            if current == start:
                path.append(start)
                break

        path.reverse()
        return path
    
    def draw(self, screen):
        for node_id, neighbours in self.__adjacency_list.items():
            node = self.__nodes[node_id]
            for neighbour_id in neighbours:
                neighbour = self.__nodes[neighbour_id]
                pyg.draw.line(screen, Config.EDGE_COLOUR, (int(node.get_pos().x), int(node.get_pos().y)), (int(neighbour.get_pos().x), int(neighbour.get_pos().y)), 2)
                
        for node in self.__nodes.values():
            node.draw(screen)

    def clear(self):
        self.__nodes.clear()
        self.__adjacency_list.clear()
        self.__next_id = 0

    def get_node(self, id):
        try:
            node = self.__nodes[id]
            return node
        except KeyError:
            return None
        
    def get_adjacency_list(self):
        return self.__adjacency_list
        
    def get_nodes_by_type(self, type):
        filtered_nodes = []
        for node in self.__nodes.values():
            if node.get_type() == type:
                filtered_nodes.append(node)

        return filtered_nodes

    def get_all_nodes(self):
        return self.__nodes
    
class Pathfinding:
    def __init__(self, path, graph):
        self.__path = path
        self.__graph = graph
        self.__current_destination_index = 0
        self.__completed = False

    def advance_destination(self):
        self.__current_destination_index += 1

        if self.__current_destination_index >= len(self.__path):
            self.__completed = True

    def get_completed(self):
        return self.__completed
    
    def get_current_destination(self):
        if self.__completed or not self.__path:
            return None
        
        if self.__current_destination_index >= len(self.__path):
            self.__completed = True
            return None
        
        id = self.__path[self.__current_destination_index]
        node = self.__graph.get_node(id)

        if node:
            return node.get_pos()
        else:
            return None

    def get_path(self):
        return self.__path

class Menu:
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
            if not self.__sim.get_map_loaded():
                print("No map loaded")
                return
            self.__sim.enable_pathfinding()
            self.__sim.set_game_state("simulation")
        elif button_id == "create_map":
            self.__sim.get_map_builder().reset()
            self.__sim.set_game_state("map_builder")
            self.__sim.get_map_builder().set_unchanged()
        elif button_id == "load_map":
            self.__open_load_dialog()
            # Show file selector
            
        elif button_id == "title":
            pass
        else:
            print("Button ID not matched")

    def __open_load_dialog(self):
        if self.__load_dialog is not None and self.__load_dialog.alive():
            self.__load_dialog.kill()

        gui_manager = self.__sim.get_gui_manager()

        dialog_rect = pyg.Rect((Config.SCREEN_WIDTH // 2 - 400, Config.SCREEN_HEIGHT // 2 - 180), Config.LOAD_DIALOG_SIZE)

        maps_path = os.path.join(os.getcwd(), Config.MAPS_FOLDER)

        self.__sim.get_gui().enable_active_gui()
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
            self.__sim.set_map_loaded()
            self.__sim.get_gui().disable_active_gui()
            self.__sim.set_game_state("map_builder")
            self.__sim.get_map_builder().set_unchanged()

        else:
            print(f"A loading error occurred: {error}")

        self.__sim.get_gui().disable_active_gui()

    def render_menu(self, screen):
        screen.fill(Config.SCREEN_COLOUR)

        gui_active = self.__sim.get_gui().get_active()

        # Draw all buttons
        for button_id, button in self.__buttons_dict.items():
            if button.draw(screen, gui_active):
                self.__button_action(button_id)

class Button:
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

    def draw(self, surface, disabled=False):
        action = False

        if not disabled:
            mouse_pos = pyg.mouse.get_pos()

            if self.__rect.collidepoint(mouse_pos):
                if pyg.mouse.get_pressed()[0] == 1 and self.__clicked == False:
                    self.__clicked = True
                    action = True

            if pyg.mouse.get_pressed()[0] == 0:
                self.__clicked = False

        surface.blit(self.__image, (self.__rect.x, self.__rect.y))
        return action

    def set_selected(self, selected):
        self.__image = self.__selected_img if selected else self.__normal_img

class MapBuilder:
    def __init__(self, sim):
        self.__sim = sim
        self.__jsonmanager = JSONManager(sim)

        # Imported image
        self.__tracing_img = None
        self.__tracing_img_path = None

        # Create temporary object containers 
        self.__builder_boundaries = []
        self.__builder_assembly = None
        self.__builder_boids = []
        self.__builder_graph = Graph()

        # Manage tool states
        self.__current_tool = None
        self.__drawing_wall = False
        self.__wall_start = None

        # Edge drawing
        self.__edge_start = None

        # UI buttons
        self.__tool_buttons = {}
        self.__confirm_buttons = {}
        self.__create_map_buttons()

        # Instantiate file manager
        self.__file_manager = FileManager(self.__sim)

        # Dialog manager
        self.__save_dialog = None
        
        self.__changes_made = False

    def __create_map_buttons(self):
            tools_list = [
                ("import_img", f"{Config.IMAGES_FOLDER}/add_image_tool.png", 0),
                ("wall", f"{Config.IMAGES_FOLDER}/wall_tool.png", 1),
                ("assembly", f"{Config.IMAGES_FOLDER}/assembly_tool.png", 2),
                ("exit", f"{Config.IMAGES_FOLDER}/exit_tool.png", 3),
                ("destination", f"{Config.IMAGES_FOLDER}/destination_tool.png", 4),
                ("boid", f"{Config.IMAGES_FOLDER}/boid_tool.png", 5),
                ("eraser", f"{Config.IMAGES_FOLDER}/eraser_tool.png", 6)
            ]
            
            for id, img, i in tools_list:
                y = Config.TOOLS_Y + (i * Config.TOOLS_MARGIN)
                self.__tool_buttons[id] = Button(Config.TOOLS_X, y, img, 0.5, selected_path=f"{img.split('.')[0]}_selected.png")

            self.__confirm_buttons["confirm"] = Button(Config.CONFIRM_X, Config.CONFIRM_Y, f"{Config.IMAGES_FOLDER}/confirm_button.png", 0.3)
            self.__confirm_buttons["cancel"] = Button(Config.CONFIRM_X - 55, Config.CONFIRM_Y, f"{Config.IMAGES_FOLDER}/cancel_button.png", 0.3)

    def __import_graph_to_sim(self):
        sim_graph = self.__sim.get_graph()
        sim_graph.clear()

        node_map = {}
        for node in self.__builder_graph.get_all_nodes().values():
            new_id = sim_graph.add_node(node.get_pos(), node.get_type())
            node_map[node.get_id()] = new_id

        for id, neighbours in self.__builder_graph.get_adjacency_list().items():
            for neighbour_id in neighbours.keys():
                new_id = node_map[id]
                new_neighbour_id = node_map[neighbour_id]
                sim_graph.add_edge(new_id, new_neighbour_id, True)

    def __open_save_dialog(self, placeholder="map.json"):
        if self.__save_dialog is not None:
            self.__save_dialog.kill()

        gui_manager = self.__sim.get_gui_manager()
        self.__sim.get_gui().enable_active_gui()

        dialog_rect = pyg.Rect((Config.SCREEN_WIDTH // 2 + 208, Config.SCREEN_HEIGHT - 78), Config.SAVE_DIALOG_SIZE)
        self.__save_dialog = pygui.elements.UITextEntryLine(relative_rect=dialog_rect, manager=gui_manager, object_id="#save_file_path")
        self.__save_dialog.set_text(placeholder)

    def __handle_save_path(self, path):
        if self.__save_dialog is None:
            print("No path entered")
            return

        if path[-5:] != ".json":
            path += ".json"

        save_location = os.path.join(os.getcwd(), Config.MAPS_FOLDER)
        path = os.path.join(save_location, path)
            
        graph = self.__builder_graph.to_json()
        self.__sim.import_graph(graph)

        success, error = self.__jsonmanager.save_map(path, self.__builder_boundaries, self.__builder_assembly, self.__builder_boids, self.__tracing_img_path, graph)

        self.__save_dialog.kill()
        self.__sim.get_gui().disable_active_gui()

        self.__sim.set_map_loaded()

        if success:
            self.__sim.set_game_state('menu')
        else:
            print(f"A save error occurred: {error}")
            self.__sim.set_game_state("menu")

    def __import_image(self):
        self.__file_manager.create_file_explorer()

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

    def __use_wall_tool(self, pos, button):
        if button == 1:
            if not self.__drawing_wall:
                self.__wall_start = pyg.math.Vector2(pos)
                self.__drawing_wall = True
            else:
                self.wall_end(pyg.math.Vector2(pos))
                self.__wall_start = pyg.math.Vector2(pos)
                self.__drawing_wall = True

    def __use_assembly_tool(self, pos):
        if self.__builder_assembly:
            for id, node in list(self.__builder_graph.get_all_nodes().items()):
                if node.get_type() == 'assembly':
                    self.__builder_graph.remove_node(id)

        self.__builder_assembly = AssemblyPoint(pos)
        self.__builder_graph.add_node(pos, 'assembly')

    def __use_boid_tool(self, pos):
        new_boid = Boid(self.__sim)
        new_boid.set_pos(pyg.math.Vector2(pos))
        self.__builder_boids.append(new_boid)

    def __use_exit_tool(self, pos):
        id = self.__builder_graph.add_node(pos, 'exit')

    def __use_destination_tool(self, pos):
        id = self.__builder_graph.add_node(pos, 'destination')

    def __create_edges(self):
        """
        clicked_id = self.__find_node_at_pos(pos, 20)

        if clicked_id is None:
            self.__edge_start = None
            return
        
        if self.__edge_start is None:
            self.__edge_start = clicked_id

        else:
            if self.__edge_start != clicked_id:
                self.__builder_graph.add_edge(self.__edge_start, clicked_id, True)

            self.__edge_start = None
        """

        all_nodes = self.__builder_graph.get_all_nodes().items()
        for id_a, node_a in all_nodes:
            for id_b, node_b in all_nodes:
                if node_a != node_b:
                    if node_a.get_pos().distance_to(node_b.get_pos()) < Config.GRAPH_EDGE_RADIUS:
                        if Helper.clear_path(node_a, node_b, self.__builder_boundaries):
                            self.__builder_graph.add_edge(id_a, id_b, True)

    def __use_erase_tool(self, pos):
        node_id = self.__find_node_at_pos(pos, Config.ERASE_RADIUS)
        if node_id is not None:
            self.__builder_graph.remove_node(node_id)
            return 

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

    def __find_node_at_pos(self, pos, radius):
        pos_vector = pyg.math.Vector2(pos)

        for node in self.__builder_graph.get_all_nodes().values():
            if node.get_pos().distance_squared_to(pos_vector) < radius ** 2:
                return node.get_id()
            
        return None

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

    def reset(self):
        self.__builder_boundaries = []
        self.__builder_assembly = None
        self.__builder_boids = []
        self.__builder_graph.clear()
        self.__tracing_img = None
        self.__tracing_img_path = None
        self.__current_tool = None
        self.__drawing_wall = False
        self.__wall_start = None

        self.__edge_start = None

        self.__save_dialog = None
        self.__sim.set_map_unloaded()

    def tool_click(self, id):
        self.__changes_made = True

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
            
            self.__create_edges()
            self.__sim.import_objects_to_sim(self.__builder_boundaries, self.__builder_assembly, self.__builder_boids, self.__tracing_img)
            self.__import_graph_to_sim()

            if self.__sim.get_map_loaded():
                if self.__changes_made is False:
                    self.__sim.set_game_state("menu")
                    return
                else:
                    if self.__save_dialog is None:
                        self.__open_save_dialog("updated_map.json")
                        return
            
            if self.__save_dialog is None:
                self.__open_save_dialog()
                return

            file_input = self.__save_dialog.get_text().strip()
            self.__handle_save_path(file_input)
        
        elif id == "cancel":
            if self.__sim.get_gui().get_active() is False:
                self.reset()
                self.__sim.set_map_unloaded()
                self.__sim.set_game_state("menu")

    def handle_image(self, path):
        self.__sim.get_gui().disable_active_gui()

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

            except Exception as e:
                print(f"An image error occurred: {e}")

    def handle_click(self, pos, button):
        if self.__sim.get_gui().get_active() is False:
            if self.__current_tool == "wall":
                self.__use_wall_tool(pos, button)

            elif self.__current_tool == "assembly":
                self.__use_assembly_tool(pos)

            elif self.__current_tool == "exit":
                self.__use_exit_tool(pos)

            elif self.__current_tool == "destination":
                self.__use_destination_tool(pos)

            elif self.__current_tool == "boid":
                self.__use_boid_tool(pos)

            elif self.__current_tool == "eraser":
                self.__use_erase_tool(pos)

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

    def render_builder(self, screen):
        screen.fill(Config.SCREEN_COLOUR)

        gui_active = self.__sim.get_gui().get_active()

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

        self.__builder_graph.draw(screen)

        if self.__edge_start is not None:
            node = self.__builder_graph.get_node(self.__edge_start)
            if node:
                pyg.draw.circle(screen, (255, 255, 0), (int(node.get_pos().x), int(node.get_pos().y)), 20, 3)

        # Draw buttons
        for button_id, button in self.__tool_buttons.items():
            button.set_selected(button_id == self.__current_tool)
            if button.draw(screen, gui_active):
                self.tool_click(button_id)

        for button_id, button in self.__confirm_buttons.items():
            if button.draw(screen):
                self.confirm_click(button_id)

    def get_builder_graph(self):
        return self.__builder_graph

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

    def set_boundaries(self, lst):
        self.__builder_boundaries = lst

    def set_assembly(self, point):
        self.__builder_assembly = point
        self.__builder_graph.add_node(point.get_pos(), 'assembly')

    def set_boids(self, lst):
        self.__builder_boids = lst

    def set_unchanged(self):
        self.__changes_made = False

class FileManager:
    def __init__(self, sim):
        self.__sim = sim

    def create_file_explorer(self):
        gui_manager = self.__sim.get_gui_manager()
        file_rect = pyg.Rect((260, 215), (600, 380))
        file_explorer = pygui.windows.ui_file_dialog.UIFileDialog(rect=file_rect, manager=gui_manager, window_title="Choose a map image", initial_file_path=".", allowed_suffixes={'.png', '.jpeg ', '.jpg'}, object_id="#file_explorer")
        file_explorer.resizable = False
        self.__sim.get_gui().enable_active_gui()

        return None

class JSONManager:
    def __init__(self, sim):
        self.__sim = sim

    @staticmethod
    def __validate_data(data):
        required_fields = ["assembly_point", "boundaries", "boids", "graph"]
        
        for field in required_fields:
            if field not in data:
                return (False, f"Missing required field: {field}")

        return (True, None)
    
    @staticmethod
    def save_map(path, boundaries, assembly, boids, img_path=None, graph=None):
        try:
            if not path.lower().endswith('.json'):
                path += '.json'

            map_data = {
                "map_name": os.path.basename(path).split(".")[0], "created": datetime.datetime.now().isoformat(),
                "map_image": img_path,
                "assembly_point": {"x": int(assembly.get_pos()[0]), "y": int(assembly.get_pos()[1])},
                "boundaries": [], "boids": [], 
                "graph": graph if graph else None}

            # Add boundaries to JSON
            for boundary in boundaries:
                start, end = boundary.get_pos()
                map_data["boundaries"].append({
                    "start": {"x": int(start[0]), "y": int(start[1])},
                    "end": {"x": int(end[0]), "y": int(end[1])}})

            # Add boids to JSON
            for boid in boids:
                pos = boid.get_pos()
                map_data["boids"].append({"x": int(pos[0]), "y": int(pos[1])})

            with open(path, 'w') as file:
                json.dump(map_data, file)

            return (True, None)

        except Exception as e:
            return (False, f"A saving error occurred: {str(e)}")
        
    @staticmethod
    def load_map(path):
        try:
            with open(path, 'r') as file:
                data = json.load(file)

            # Validate loaded data
            is_valid = JSONManager.__validate_data(data)
            if not is_valid[0]:
                return (False, None, is_valid[1])
            
            parsed = {
                "boundaries": [], "assembly_point": None, "boids": [],
                "graph": data.get("graph", None),
                "map_image": data.get("map_image", None)}

            # Assembly point
            parsed["assembly_point"] = (data["assembly_point"]["x"], data["assembly_point"]["y"])

            # Boundaries
            for boundary in data["boundaries"]:
                start = (boundary["start"]["x"], boundary["start"]["y"])
                end = (boundary["end"]["x"], boundary["end"]["y"])
                parsed["boundaries"].append((start, end))

            # Boids
            for boid in data["boids"]:
                parsed["boids"].append((boid["x"], boid["y"]))

            return (True, parsed, None)

        except Exception as e:
            return (False, None, f"A loading error occurred: {str(e)}")
        
    def import_map(self, data):
        boundaries = data["boundaries"]
        assembly = data["assembly_point"]
        boids = data["boids"]
        graph = data["graph"]
        tracing_image = data["map_image"]
        self.__sim.import_objects_to_builder(boundaries, assembly, boids, graph, tracing_image)
            
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
        # self._pos += self._vel

        self._acc = pyg.math.Vector2(0, 0)

        # Boids bounce against window
        window = self._sim.get_window()

        pos = self.get_pos()

        """ Wrapping logic
        if pos.x > window.w:
            pos.x -= window.w
        elif pos.x < 0:
            pos.x += window.w

        if pos.y > window.h:
            pos.y -= window.h
        elif pos.y < 0:
            pos.y += window.h
        """

        # Bounce logic
        if pos.x >= window.w or pos.x <= 0:
            self._vel[0] = -self._vel[0]
        if pos.y >= window.h or pos.y <= 0:
            self._vel[1] = -self._vel[1]

        
class Boid(BoidObject):
    def __init__(self, sim):
        pos = (0, 0)
        super().__init__(sim, pos)
        self._max_speed = Config.MAX_SPEED
        self._vel = pyg.math.Vector2(1, 1)

        self._reached_target = False
        self.__pathfinding = None
    
    def __move(self):
        # Ensure velocity doesn't exceed max velocity
        if self._vel.length_squared() > (Config.MAX_SPEED ** 2):
            self._vel.scale_to_length(Config.MAX_SPEED)

        self.set_pos(self.get_pos() + self._vel)
    
    def __seeking_destination(self, destination):
        acc_request = pyg.math.Vector2(0, 0)

        if destination is None:
            return acc_request
        
        destination_vector = destination - self.get_pos()
        dist = destination_vector.length()

        if dist < Config.ARRIVED_RADIUS:
            return acc_request

        """
        if dist < Config.ARRIVAL_SLOWING_RADIUS:
            speed = self._max_speed * (dist / Config.ARRIVAL_SLOWING_RADIUS)
        else:
            speed = self._max_speed
        """

        speed = self._max_speed

        # Normalise to create a direction vector
        if destination_vector.length_squared() > 0:
            destination_vector.normalize_ip()
        else:
            return acc_request
        
        # Scale to maximum speed value
        acc_request = destination_vector * speed

        # Subtract current velocity for steering force
        acc_request -= self._vel

        return acc_request
        
    def __avoid_boundary(self):
        acc_request = pyg.math.Vector2(0, 0)
        nearby_boundaries = self.__boundaries_in_radius()

        if len(nearby_boundaries) == 0:
            return acc_request

        for boundary in nearby_boundaries:
            will_collide, collision_point = boundary.will_collide(self)

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
                closest_point = self.__distance_to_closest_boundary(boundary)

                try:
                    dist_delta = self.get_pos() - closest_point
                    distance = self.get_pos().distance_to(closest_point)

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
    
    def __boids_in_radius(self, radius):
        boids_present = []
        for surrounding_boid in self._sim.get_boid_container():
            if surrounding_boid == self:
                pass
            else:
                if self.get_pos().distance_to(surrounding_boid.get_pos()) < radius:
                    boids_present.append(surrounding_boid)
            
        return boids_present
    
    def __boundaries_in_radius(self):
        boundaries_present = []
        for boundary in self._sim.get_boundary_container():
            if boundary.check_collision(self):
                boundaries_present.append(boundary)

        return boundaries_present
    
    def __distance_to_closest_boundary(self, boundary):
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

    def draw(self, screen):
        if self.__pathfinding:
            path = self.__pathfinding.get_path()
            graph = self._sim.get_graph()

            if graph and len(path) > 1:
                points = []
                for id in path:
                    node = graph.get_node(id)
                    if node:
                        points.append((int(node.get_pos().x), int(node.get_pos().y)))  

        # Calculate points of the triangle
        phi = math.atan2(self._vel.y, self._vel.x)
        phi2 = 0.75 * math.pi

        pos = self.get_pos()

        pos1 = ((pos.x + (math.cos(phi) * Config.BOID_SIZE), (pos.y + (math.sin(phi) * Config.BOID_SIZE))))
        pos2 = ((pos.x + (math.cos(phi + phi2) * Config.BOID_SIZE), (pos.y + (math.sin(phi + phi2) * Config.BOID_SIZE))))
        pos3 = ((pos.x + (math.cos(phi - phi2) * Config.BOID_SIZE), (pos.y + (math.sin(phi - phi2) * Config.BOID_SIZE))))

        pyg.draw.polygon(screen, Config.BOID_COLOUR, (pos1, pos2, pos3))

    def step(self):
        current_destination = None

        if self.__pathfinding:
            if not self.__pathfinding.get_completed():
                current_destination = self.__pathfinding.get_current_destination()

                if current_destination:
                    distance_to_target = self.get_pos().distance_to(current_destination)

                    if distance_to_target < Config.ARRIVED_RADIUS:
                        self.__pathfinding.advance_destination()
                        current_destination = self.__pathfinding.get_current_destination()
        
        self._acc += self.__avoid_boundary() * self._sim.get_config_value("avoidance")
        self._acc += self.__separation() * self._sim.get_config_value("separation")
        self._acc += self.__alignment() * self._sim.get_config_value("alignment")
        self._acc += self.__cohesion() * self._sim.get_config_value("cohesion")

        if current_destination is not None:
            self._acc += self.__seeking_destination(current_destination) * Config.DEFAULT_SEEKING_FACTOR
        else:
            self._acc += self.__seeking_destination(self._sim.get_assembly_point().get_pos()) * 0.1

        super().step()

        # Increment positions by velocity
        self.__move()

    def assign_path(self, graph):
        exit_id = graph.find_nearest_node(self.get_pos(), 'exit')
        assembly_nodes = graph.get_nodes_by_type('assembly')

        assembly_id = assembly_nodes[0].get_id()
        path = graph.dijkstra(exit_id, assembly_id)

        if path:
            self.__pathfinding = Pathfinding(path, graph)

    def get_pos(self):
        return self._pos
    
    def get_vel(self):
        return self._vel

    def set_pos(self, value):
        self._pos = value

class Boundary:
    def __init__(self, pos):
        self.__pos = pos
        self.__expanded_points = []

        self.expand(Config.BOUNDARY_RADIUS)
        
    def draw(self, screen):
        pyg.draw.line(screen, Config.BOUNDARY_COLOUR, self.__pos[0], self.__pos[1], Config.BOUNDARY_THICKNESS)

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

            intersect = Helper.lines_intersect(current_pos, next_pos, line_start, line_end)

            if intersect is not None:
                distance = boid.get_pos().distance_squared_to(intersect)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = intersect

        # Check whether the boid path for the next frame intersects a line 
        return (closest_point is not None, closest_point)

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
    
class AssemblyPoint:
    def __init__(self, pos):
        self.__pos = pos

    def draw(self, screen):
        pyg.draw.circle(screen, Config.ASSEMBLY_COLOUR, self.__pos, Config.ASSEMBLY_SIZE)

    def get_pos(self):
        return self.__pos

class Helper:
    @staticmethod
    def lines_intersect(p1, p2, p3, p4):
        # P1/P2 = projected motion
        # P3/P4 = boundary edge

        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if den == 0:
            return
 
        ua = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        if ua < 0 or ua > 1:
            return None
        
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
        if ub < 0 or ub > 1:
            return None

        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)

        return pyg.Vector2(x, y)
        
    @staticmethod
    def clear_path(node_a, node_b, walls):
        for wall in walls:
            if Helper.lines_intersect(node_a.get_pos(), node_b.get_pos(), wall.get_pos()[0], wall.get_pos()[1]) is not None:
                return False
            
        return True
            
if __name__ == '__main__':
    sim = Sim()
    sim.run()