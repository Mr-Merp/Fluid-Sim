import sys
import pymunk
import pygame
import math
import pymunk.pygame_util
import particle_prop

class Fluid_Sim:
    #Contains the main loop and the fluid simulation in general
    def __init__(self, num_p: int = 100, width: int = 640, height: int = 1040, fps: int = 60):
        # initialize pygame
        pygame.init()

        #set the number of particles in the simulation
        self.num_p = num_p
        self.particle_list = []
        self.grid_dict = {}
        self.grid_width = int((width - 40) // 100)
        self.grid_height = int((height - 40) // 100)

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
        body = pymunk.Body()
        body.position = (x, y)
        shape = pymunk.Circle(body, radius)
        shape.mass = 10
        shape.color = (255, 0, 0, 100)
        shape.elasticity = 0.7
        shape.friction = 0.7
        shape.filter = pymunk.ShapeFilter(categories = 1, mask = pymunk.ShapeFilter.ALL_MASKS() ^ 1)
        self.space.add(body, shape)
        self.particle_list.append(shape)
        return shape

    def reset_grid(self) -> None:
        loop = self.grid_height * self.grid_width
        for i in range(loop):
            self.grid_dict[i] = []

    def update_grid(self) -> None:
        for i in range(len(self.particle_list)):
            x, y = particle_prop.relative_position(self.particle_list[i])
            if x >= self.WIDTH - 40: x = int(self.grid_width * 100 - 1)
            if y >= self.HEIGHT - 40: y = int(self.grid_height * 100 - 1)
            grid_num = int((y // 100) * self.grid_width + (x // 100))
            self.grid_dict[grid_num].append(i)

    def calculate_density(self, shape: pymunk.Circle) -> float:
        pass

    def reset(self) -> None:
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
        radius = 5
        # Calculate the size of a perfectly square grid that would fit the particles
        grid_size = int(math.sqrt(self.num_p))

        # Calculate remaining particles that won't fit in the perfect square
        remaining = self.num_p - (grid_size * grid_size)

        # Calculate particle spacing (assuming radius is the space between particles)
        spacing = radius * 3

        # Calculate starting position to center the grid
        start_x = (self.WIDTH - (grid_size * spacing)) / 2 + radius
        start_y = (self.HEIGHT - (grid_size * spacing)) / 2 + radius

        # Create the main square grid
        for row in range(grid_size):
            for col in range(grid_size):
                x = start_x + (col * spacing)
                y = start_y + (row * spacing)
                self.new_particle(int(x), int(y), radius)

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

                self.new_particle(int(extra_row_x), int(extra_row_y), radius)
                extra_row_x += spacing
                particles_in_row += 1

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
                    print(self.grid_width, self.grid_height)
                    for grid, particle in self.grid_dict.items():
                        print(grid, ": ", particle)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.pause()
                    if event.key == pygame.K_z:
                        self.reset()

            self.update_new_frame()
            self.space.step(self.dt)
            self.clock.tick(self.fps)

        pygame.quit()


if __name__ == "__main__":
    fluid = Fluid_Sim(1000)
    fluid.start()

