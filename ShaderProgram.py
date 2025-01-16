import sys
import moderngl as mgl

from settings import *


class ShaderProgram:
    def __init__(self, app) -> None:
        """
        Class that loads and stores an OpenGL shader file
        
        :param Engine app: The Engine object which contains the OpenGL context shader should be loaded into
        """

        self.app = app
        self.context = app.context
        self.quad = self.get_program('quad')

    
    def set_uniforms_on_init(self) -> None:
        pass


    def update(self) -> None:
        "Updates the Shader Program"

        pass


    def get_program(self, shaderName: str) -> mgl.Program:
        """
        Loads the vertex and fragment shader files into a shader program and returns it

        :param str shaderName: The filename for the shader file within the shaders file

        :return: An OpenGL shader program with the loaded vertex and fragment shaders
        """
        
        # Removes irrelevant areas of the path and file extension if accidentally provided
        shaderName = shaderName.split('Shaders/')[-1]
        shaderName = shaderName.split('.')[0]
        
        # Load the vertex shader
        try:
            with open(f'Shaders/{shaderName}.vert') as vertFile:
                vertexShader = vertFile.read()

        except FileNotFoundError:
            print(f"File not found: Shaders/{shaderName}.vert")
            sys.exit()
        
        # Load the fragment shader
        try:
            with open(f'Shaders/{shaderName}.frag') as fragFile:
                fragmentShader = fragFile.read()

        except FileNotFoundError:
            print(f"File not found: Shaders/{shaderName}.frag")
            sys.exit()

        program = self.context.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)
        
        return program