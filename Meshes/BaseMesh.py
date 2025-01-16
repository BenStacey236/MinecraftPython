import numpy as np
import moderngl as mgl

from ShaderProgram import ShaderProgram


class BaseMesh:
    def __init__(self):
        # OpenGL Context and Shader Program
        self.context: mgl.Context = None
        self.shaderProgram: ShaderProgram = None

        # Vertex Buffer Object format and attributes
        self.vboFormat = None
        self.attrs: tuple[str, ...] = None

        # Vertex Array Object
        self.vao: mgl.VertexArray = None


    def get_vertex_data(self) -> np.array:
        pass


    def get_vao(self) -> mgl.VertexArray:
        vertexData = self.get_vertex_data()
        vbo = self.context.buffer(vertexData)
        vao = self.context.vertex_array(self.shaderProgram, [(vbo, self.vboFormat, *self.attrs)], skip_errors=True)
        
        return vao
    

    def render(self) -> None:
        self.vao.render()

