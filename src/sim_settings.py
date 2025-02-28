import sys
import pymunk
import pygame
import math
import pymunk.pygame_util
from pymunk.vec2d import Vec2d
import src.particle_prop as particle_prop
import random

class Fluid_Sim:
    #Contains the main loop and the fluid simulation in general
    def __init__(self, num_p: int = 200, width: int = 640, height: int = 1040, fps: int = 60):
        # initialize pygame
        pygame.init()
        self.grid_size = 50
        self.radius = 5
        self.interact = False

        #set the number of particles in the simulation
        self.num_p = num_p
        self.particle_list = []
        self.grid_list = []
        self.grid_dict = {}
        self.density_list = []
        self.grid_width = int((width - 40) // self.grid_size)
        self.grid_height = int((height - 40) // self.grid_size)


        # standard pygame window setup
        self.WIDTH, self.HEIGHT = width, height
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        # pygame loop set up
        self.run = True
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.dt = 1 / self.fps

        # pymunk space set up
        self.space = pymunk.Space()
        self.draw_options = pymunk.pygame_util.DrawOptions(self.window)

    def pause(self) -> None:
        #pause the simulation
        paused = True
        while paused:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = False
                        break

    def setup_environment(self) -> None:
        #creates the walls/bounds of the environment
        walls = [
            [(self.WIDTH/2, self.HEIGHT - 10), (self.WIDTH, 20)],
            [(self.WIDTH/2, 10), (self.WIDTH, 20)],
            [(10, self.HEIGHT/2), (20, self.HEIGHT)],
            [(self.WIDTH - 10, self.HEIGHT/2), (20, self.HEIGHT)]
        ]

        for pos, size in walls:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = pos
            shape = pymunk.Poly.create_box(body, size)
            shape.elasticity = 0.5
            shape.friction = 0.5
            self.space.add(body, shape)

    def new_particle(self, x: int, y: int, radius: int) -> pymunk.Circle:
        #creates a new particle
        body = pymunk.Body()
        body.position = (x, y)
        shape = pymunk.Circle(body, radius)
        shape.mass = 100
        shape.color = (255, 0, 0, 100)
        shape.elasticity = 0.2
        shape.friction = 0.7
        #shape.filter = pymunk.ShapeFilter(categories = 1, mask = pymunk.ShapeFilter.ALL_MASKS() ^ 1)
        self.space.add(body, shape)
        self.particle_list.append(shape)
        return shape

    def reset_grid(self) -> None:
        #resets what particles are at current cells and resets the densities at each particle
        self.grid_list = []
        self.density_list = []
        loop = self.grid_height * self.grid_width
        for i in range(loop):
            self.grid_dict[i] = []

    def get_current_grid(self, x: float, y: float) -> int:
        #given the relative x and y positions, determine the cell that the point is in
        if x >= self.WIDTH - 40: x = int(self.grid_width * self.grid_size - 1)
        if y >= self.HEIGHT - 40: y = int(self.grid_height * self.grid_size - 1)
        if x < 0: x = 0
        if y < 0: y = 0
        return int((y // self.grid_size) * self.grid_width + (x // self.grid_size))

    def update_grid(self) -> None:
        #updates what particles are at what cell in the grid and the densities of each particle
        #start_time = time.time()
        for i in range(len(self.particle_list)):
            x, y = particle_prop.relative_position(self.particle_list[i])
            grid_num = self.get_current_grid(x, y)
            self.grid_list.append(grid_num)
            self.grid_dict[grid_num].append(i)
        self.update_particle_density()
        #print(time.time() - start_time)

    def grids_to_search(self, grid_num: int) -> list[int]:
        #finds the cells surrounding the current cell
        surrounding = [grid_num]

        # Convert 1D index to 2D coordinates
        row = grid_num // self.grid_width
        col = grid_num % self.grid_width

        # Check all 8 directions (including diagonals)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Top left, top, top right
            (0, -1), (0, 1),  # Left, right
            (1, -1), (1, 0), (1, 1)  # Bottom left, bottom, bottom right
        ]

        for d_row, d_col in directions:
            new_row = row + d_row
            new_col = col + d_col

            # Check if the new position is within bounds
            if (0 <= new_row < self.grid_height and
                    0 <= new_col < self.grid_width):
                # Convert back to 1D index
                new_index = new_row * self.grid_width + new_col
                surrounding.append(new_index)

        return surrounding

    def calculate_density(self, particle_num: int) -> float:
        density = 0
        search_grids = self.grids_to_search(self.grid_list[particle_num])
        mass = 1000
        #print(particle_num, search_grids)
        #start_time = time.time()
        for grid in search_grids:
            for particle in self.grid_dict[grid]:
                distance = particle_prop.distance(self.particle_list[particle], self.particle_list[particle_num])
                influence = particle_prop.smoothing_function(float(self.grid_size), distance)

                density += influence * mass
        #print(time.time() - start_time, density, particle_num)
        #self.pause()
        return density

    def calculate_pressure(self, particle_num: int) -> Vec2d:
        pressure = Vec2d(0, 0)
        search_grids = self.grids_to_search(self.grid_list[particle_num])
        mass = 1000
        # print(particle_num, search_grids)
        # start_time = time.time()
        for grid in search_grids:
            for particle in self.grid_dict[grid]:
                if particle != particle_num and self.density_list[particle] != 0:
                    distance = particle_prop.distance(self.particle_list[particle_num], self.particle_list[particle])
                    direction = (self.particle_list[particle].body.position - self.particle_list[particle_num].body.position) / distance
                    slope = particle_prop.smoothing_function_derivative(distance, self.grid_size)
                    pressure += particle_prop.shared_pressure(self.density_list[particle], self.density_list[particle_num]) * direction * slope * mass / self.density_list[particle]
        return pressure

    def interaction_pressure(self, x: int, y: int) -> None:
        for grid in self.grids_to_search(self.get_current_grid(x, y)):
            for i in self.grid_dict[grid]:
                distance = math.sqrt((self.particle_list[i].body.position[0] - x) ** 2 + (self.particle_list[i].body.position[1] - y) ** 2)
                direction = (self.particle_list[i].body.position - Vec2d(x, y)) / distance
                slope = particle_prop.smoothing_function_derivative(distance, self.grid_size)
                self.particle_list[i].body.velocity -= direction * slope * 10000000

    def update_particle_density(self) -> None:
        #updates the particle density and pressure
        for i in range(len(self.particle_list)):
            self.density_list.append(self.calculate_density(i))
        for i in range(len(self.particle_list)):
            pressure = self.calculate_pressure(i)
            self.particle_list[i].body.velocity += pressure

    def reset(self) -> None:
        #reset the simulation back to its starting positions
        for particle in self.particle_list:
            self.space.remove(particle)

        self.particle_list = []
        self.reset_grid()

    def update_new_frame(self) -> None:
        #basically the update call
        self.window.fill("black")
        self.space.debug_draw(self.draw_options)
        pygame.display.update()
        self.reset_grid()

    def particle_start_random(self) -> None:
        #Puts particles in random positions throughout the simulation
        for _ in range(self.num_p):
            self.new_particle(random.randint(20, self.WIDTH - 20), random.randint(20, self.HEIGHT-20), 5)

    def particle_start_organized(self) -> None:
        #Puts particles in an organized box in the center of the simulation box
        # Calculate the size of a perfectly square grid that would fit the particles
        grid_size = int(math.sqrt(self.num_p))

        # Calculate remaining particles that won't fit in the perfect square
        remaining = self.num_p - (grid_size * grid_size)

        # Calculate particle spacing (assuming radius is the space between particles)
        spacing = self.radius * 5

        # Calculate starting position to center the grid
        start_x = (self.WIDTH - (grid_size * spacing)) / 2 + self.radius
        start_y = (self.HEIGHT - (grid_size * spacing)) / 2 + self.radius

        # Create the main square grid
        for row in range(grid_size):
            for col in range(grid_size):
                x = start_x + (col * spacing)
                y = start_y + (row * spacing)
                self.new_particle(x, y, self.radius)

        # Handle remaining particles by adding them as additional rows on top
        if remaining > 0:
            extra_row_y = start_y - spacing
            extra_row_x = start_x
            particles_in_row = 0

            for i in range(remaining):
                if particles_in_row >= grid_size:
                    extra_row_y -= spacing
                    particles_in_row = 0
                    extra_row_x = start_x

                self.new_particle(extra_row_x, extra_row_y, self.radius)
                extra_row_x += spacing
                particles_in_row += 1

    def update_colors(self):
        for particle in self.particle_list:
            particle.color = particle_prop.color_change(particle.body.velocity)

    def start(self) -> None:
        # runs the main loop
        # set up environment/walls
        self.setup_environment()

        #create the particle grid
        self.particle_start_organized()

        #setting up grid dictionary
        self.reset_grid()

        # main loop to run the simulation including quit and pause functions
        while self.run:
            self.update_new_frame()
            self.update_grid()
            self.update_colors()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.interact:
                        self.interact = False
                    else:
                        self.interact = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.pause()
                    if event.key == pygame.K_z:
                        self.reset()
                        self.particle_start_random()
                    if event.key == pygame.K_x:
                        self.reset()
                        self.particle_start_organized()
            if self.interact:
                x, y = pygame.mouse.get_pos()
                self.interaction_pressure(x, y)

            #self.pause()

            self.space.step(self.dt)
            self.clock.tick(self.fps)

        pygame.quit()


