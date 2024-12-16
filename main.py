import sys
import pymunk
import pygame
import math
import pymunk.pygame_util
import particle_prop

class Fluid_Sim:
    #Contains the main loop and the fluid simulation in general
    def __init__(self, num_p: int = 100, width: int = 1500, height: int = 1000, fps: int = 60):
        # initialize pygame
        pygame.init()

        #set the number of particles in the simulation
        self.num_p = num_p
        self.particle_list = []
        self.quad_list = []

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
        self.space.add(body, shape)
        return shape

    def reset(self) -> None:
        for particle in self.particle_list:
            self.space.remove(particle)

        self.particle_list = []
        self.quad_list = []

    def update_new_frame(self) -> None:
        #basically the update call
        self.window.fill("black")
        self.space.debug_draw(self.draw_options)
        pygame.display.update()

    def start(self) -> None:
        # runs the main loop

        # set up environment/walls
        self.setup_environment()

        #setting the gravity
        self.space.gravity = (0, 981)

        # main loop to run the simulation including quit and pause functions
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.pause()
                    if event.key == pygame.K_c:
                        self.particle_list.append(self.new_particle(300, 300, 5))
                    if event.key == pygame.K_z:
                        self.reset()

            self.update_new_frame()
            self.space.step(self.dt)
            self.clock.tick(self.fps)

        pygame.quit()


if __name__ == "__main__":
    fluid = Fluid_Sim()
    fluid.start()

