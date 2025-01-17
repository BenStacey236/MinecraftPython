from numba import njit
import numpy as np
import glm
import math

# Definition of window resolution
WINDOW_RES = glm.vec2(1280, 720)

# Definition of OpenGL window depth
WINDOW_DEPTH = 24

# Camera settings
ASPECT_RATIO = WINDOW_RES.x / WINDOW_RES.y
FOV_DEGREES = 50
VERTICAL_FOV = glm.radians(FOV_DEGREES)
HORIZONTAL_FOV = 2 * math.atan(math.tan(VERTICAL_FOV * 0.5) * ASPECT_RATIO)
NEAR = 0.1
FAR = 2000.0
PITCH_MAX = glm.radians(89)

# Player settings
PLAYER_SPEED = 0.005
PLAYER_ROT_SPEED = 0.003
PLAYER_POS = glm.vec3(0, 0, 1)
MOUSE_SENITIVITY = 0.002

# Definition of colours
BG_COLOUR = glm.vec3(0.1, 0.1, 0.3)