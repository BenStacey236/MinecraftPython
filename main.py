import moderngl as mgl
import pygame
import sys

from settings import *

pygame.init()


class Engine:
    def __init__(self) -> None:
        "Engine Class that runs the main game"

        # Initialise OpenGL Context
        try:
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
            pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

            pygame.display.set_mode(WINDOW_RES, flags=pygame.OPENGL | pygame.DOUBLEBUF)
            pygame.display.set_caption("MinecraftPython")
            
            self.context = mgl.create_context()
            self.context.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
            self.context.gc_mode = "auto"

        except Exception as e:
            print(f"Error initialising OpenGL Context: {e}")
            sys.exit()

        # Initialise Engine variables
        self.clock = pygame.time.Clock()
        self.deltaTime = 0
        self.time = 0

        self.isRunning = True


    def update(self) -> None:
        "Updates information for the engine"

        self.deltaTime = self.clock.tick()
        self.time = pygame.time.get_ticks() * 0.001
        pygame.display.set_caption(f'FPS: {self.clock.get_fps():.0f}')


    def render(self) -> None:
        "Function that renders the engine"

        self.context.clear(color=BG_COLOUR)
        pygame.display.flip()


    def handle_events(self) -> None:
        "Function that handles all events taking place in the engine"

        for event in pygame.event.get():
            # Quits if the 'X' is pressed or ESC key pressed
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.isRunning = False


    def run(self) -> None:
        "Main function that runs the engine"

        # Runs main game loop while running
        while self.isRunning:
            self.handle_events()
            self.update()
            self.render()

        # Quits properly after running
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    minecraftEngine = Engine()
    minecraftEngine.run()