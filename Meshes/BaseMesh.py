import numpy as np
import moderngl as mgl

from ShaderProgram import ShaderProgram


class BaseMesh:
    def __init__(self):
        "Base mesh class to which future mesh classes will inherit from"

        # OpenGL Context and Shader Program
        self.context: mgl.Context = None
        self.shaderProgram: ShaderProgram = None

        # Vertex Buffer Object format and attributes
        self.vboFormat = None
        self.attrs: tuple[str, ...] = None

        # Vertex Array Object
        self.vao: mgl.VertexArray = None


    def get_vertex_data(self) -> np.array:
        """
        Gets the vertex data for the mesh
        
        :returns: A numpy array of vertices in the mesh
        """

        return np.empty((1, 1))


    def get_vao(self) -> mgl.VertexArray:
        """
        Gets the vertex array object for the currrent mesh
        
        :returns: An OpenGL vertex array object
        """

        vertexData = self.get_vertex_data()
        vbo = self.context.buffer(vertexData)
        vao = self.context.vertex_array(self.shaderProgram, [(vbo, self.vboFormat, *self.attrs)], skip_errors=True)
        
        return vao
    

    def render(self) -> None:
        "Renders the current mesh"
        
        self.vao.render()

