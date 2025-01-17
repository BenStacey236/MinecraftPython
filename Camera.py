from settings import *


class Camera:
    def __init__(self, position, yaw, pitch) -> None:
        "Class that stores camera data"

        self.pos = glm.vec3(position)
        self.yaw = glm.radians(yaw)
        self.pitch = glm.radians(pitch)

        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)

        self.projectionMatrix = glm.perspective(VERTICAL_FOV, ASPECT_RATIO, NEAR, FAR)
        self.viewMatrix = glm.mat4()


    def change_pitch(self, pitchChange: float) -> None:
        """
        Changes the pitch by the pitchChange value
        
        :param float pitchChange: The change in pitch in degrees
        """

        self.pitch -= pitchChange
        self.pitch = glm.clamp(self.pitch, -PITCH_MAX, PITCH_MAX)


    def change_yaw(self, yawChange: float) -> None:
        """
        Changes the yaw by the yawChange value
        
        :param float yawChange: The change in yaw in degrees
        """

        self.yaw += yawChange


    def move_right(self, velocity: float) -> None:
        """
        Moves the camera right in space
        
        :param float velocity: The velocity of movement
        """

        self.pos += self.right * velocity


    def move_left(self, velocity: float) -> None:
        """
        Moves the camera left in space
        
        :param float velocity: The velocity of movement
        """

        self.pos -= self.right * velocity


    def move_up(self, velocity: float) -> None:
        """
        Moves the camera up in space
        
        :param float velocity: The velocity of movement
        """

        self.pos += self.up * velocity


    def move_down(self, velocity: float) -> None:
        """
        Moves the camera down in space
        
        :param float velocity: The velocity of movement
        """

        self.pos -= self.up * velocity


    def move_forward(self, velocity: float) -> None:
        """
        Moves the camera forward in space
        
        :param float velocity: The velocity of movement
        """

        self.pos += self.forward * velocity

    
    def move_backward(self, velocity: float) -> None:
        """
        Moves the camera backwards in space
        
        :param float velocity: The velocity of movement
        """

        self.pos -= self.forward * velocity


    def update(self) -> None:
        "Master update method that calls other update methods"

        self.update_vectors()
        self.update_view_matrix()


    def update_vectors(self) -> None:
        "Updates the camera direction vecotrs based on yaw and pitch values"

        self.forward.x = glm.cos(self.yaw) * glm.cos(self.pitch)
        self.forward.y = glm.sin(self.pitch)
        self.forward.z = glm.sin(self.yaw) * glm.cos(self.pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))


    def update_view_matrix(self) -> None:
        "Updates the view matrix based on the position and direction camera is looking"

        self.viewMatrix = glm.lookAt(self.pos, self.pos + self.forward, self.up)