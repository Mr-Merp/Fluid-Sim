import sys
import pymunk
import pygame
import math
import pymunk.pygame_util
import particle_prop
import time
import random

class Fluid_Sim:
    #Contains the main loop and the fluid simulation in general
    def __init__(self, num_p: int = 400, width: int = 1540, height: int = 1040, fps: int = 60):
        # initialize pygame
        pygame.init()
        self.grid_size = 50

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
            shape.elasticity = 0.7
            shape.friction = 0.7
            self.space.add(body, shape)

    def new_particle(self, x: int, y: int, radius: int) -> pymunk.Circle:
        #creates a new particle
        body = pymunk.Body()
        body.position = (x, y)
        shape = pymunk.Circle(body, radius)
        shape.mass = 100
        shape.color = (255, 0, 0, 100)
        shape.elasticity = 0.7
        shape.friction = 0.7
        shape.filter = pymunk.ShapeFilter(categories = 1, mask = pymunk.ShapeFilter.ALL_MASKS() ^ 1)
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

    def get_current_grid(self, x: int, y: int) -> int:
        #given the relative x and y positions, determine the cell that the point is in
        if x >= self.WIDTH - 40: x = int(self.grid_width * self.grid_size - 1)
        if y >= self.HEIGHT - 40: y = int(self.grid_height * self.grid_size - 1)
        if x < 0: x = 0
        if y < 0: y = 0
        return int((y // self.grid_size) * self.grid_width + (x // self.grid_size))

    def update_grid(self) -> None:
        #updates what particles are at what cell in the grid and the densities of each particle
        start_time = time.time()
        for i in range(len(self.particle_list)):
            x, y = particle_prop.relative_position(self.particle_list[i])
            grid_num = self.get_current_grid(x, y)
            self.grid_list.append(grid_num)
            self.grid_dict[grid_num].append(i)
        self.update_particle_density()
        print(time.time() - start_time)

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
        mass = 100
        #print(particle_num, search_grids)
        #start_time = time.time()
        for grid in search_grids:
            for particle in self.grid_dict[grid]:
                if particle != particle_num:
                    distance = particle_prop.distance(self.particle_list[particle], self.particle_list[particle_num])
                    influence = particle_prop.smoothing_function(float(self.grid_size), distance)

                    density += influence * mass

        #print(time.time() - start_time, density)
        #self.pause()
        return density

    def update_particle_density(self) -> None:
        for i in range(len(self.particle_list)):
            self.density_list.append(self.calculate_density(i))

    def reset(self) -> None:
        #reset the simulation back to its starting positions
        for particle in self.particle_list:
            self.space.remove(particle)

        self.particle_list = []
        self.reset_grid()
        self.particle_start()

    def update_new_frame(self) -> None:
        #basically the update call
        self.window.fill("black")
        self.space.debug_draw(self.draw_options)
        pygame.display.update()
        self.reset_grid()

    def particle_start(self) -> None:
        for _ in range(self.num_p):
            self.new_particle(random.randint(20, self.WIDTH - 20), random.randint(20, self.HEIGHT-20), 5)


    def start(self) -> None:
        # runs the main loop

        # set up environment/walls
        self.setup_environment()

        #setting the gravity
        self.space.gravity = (0, 981)

        #create the particle grid
        self.particle_start()

        #setting up grid dictionary
        self.reset_grid()

        # main loop to run the simulation including quit and pause functions
        while self.run:
            self.update_grid()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    x -= 20
                    y -= 20
                    for grid in self.grids_to_search(self.get_current_grid(x, y)):
                        for i in self.grid_dict[grid]:
                            self.particle_list[i].color = (0, 255, 0, 100)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.pause()
                    if event.key == pygame.K_z:
                        self.reset()
            self.pause()

            self.update_new_frame()
            self.space.step(self.dt)
            self.clock.tick(self.fps)

        pygame.quit()


if __name__ == "__main__":
    fluid = Fluid_Sim()
    fluid.start()

