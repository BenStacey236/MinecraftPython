from numba import njit
import numpy as np
import glm
import math

# Definition of Window Resolution
WINDOW_RES = glm.vec2(1600, 900)

# Definition of OpenGL window depth
WINDOW_DEPTH = 24

# Definition of colours
BG_COLOUR = glm.vec3(0.1, 0.1, 0.3)