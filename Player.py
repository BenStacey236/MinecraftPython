import pygame

from settings import *
from Camera import Camera
import Engine


class Player(Camera):
    def __init__(self, app: 'Engine.Engine', position=PLAYER_POS, yaw=-90, pitch=0):
        "Class that stores player data and related camera data"

        super().__init__(position, yaw, pitch)
        
        self.app = app


    def update(self):
        "Updates camera information based on mouse movements and keyboard inputs"

        self.handle_keyboard()
        self.handle_mouse()

        super().update()


    def handle_keyboard(self):
        "Handles all keyboard input"

        keysPressed = pygame.key.get_pressed()
        velocity = PLAYER_SPEED * self.app.deltaTime

        if keysPressed[pygame.K_w]:
            self.move_forward(velocity)

        if keysPressed[pygame.K_a]:
            self.move_left(velocity)

        if keysPressed[pygame.K_s]:
            self.move_backward(velocity)

        if keysPressed[pygame.K_d]:
            self.move_right(velocity)

        if keysPressed[pygame.K_SPACE]:
            self.move_up(velocity)

        if keysPressed[pygame.K_f]:
            self.move_down(velocity)


    def handle_mouse(self):
        "Handles all mouse input"

        changeX, changeY = pygame.mouse.get_rel()

        if changeX:
            self.change_yaw(changeX * MOUSE_SENITIVITY)

        if changeY:
            self.change_pitch(changeY * MOUSE_SENITIVITY)

    
    def handle_event(self, event: pygame.event):
        """
        Handles a pygame event
        
        :param pygame.event event: The event to be handled
        """

        if event.type == pygame.MOUSEBUTTONDOWN:
            voxelHandler = self.app.scene.world.voxelHandler

            if event.button == 1:
                voxelHandler.switch_interaction_mode(0)
                voxelHandler.set_voxel()
            
            if event.button == 3:
                voxelHandler.switch_interaction_mode(1)
                voxelHandler.set_voxel()