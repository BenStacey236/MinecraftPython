import moderngl as mgl
from overrides import overrides

from settings import *
from Meshes.BaseMesh import BaseMesh
import Engine

class QuadMesh(BaseMesh):
    def __init__(self, app: 'Engine.Engine'):
        "Class that stores Quad Mesh Data"

        super().__init__()

        self.app = app
        self.context: mgl.Context = app.context
        self.shaderProgram = app.shaderProgram.quad

        self.vbo_format = "3f 3f"
        self.attrs = ("inPosition", "inColour")
        self.vao = self.get_vao()


    @overrides
    def get_vertex_data(self) -> np.array:
        "Returns the vertices for this mesh"
        
        vertices = [
            (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-0.5, -0.5, 0.0),
            (0.5, 0.5, 0.0), (-0.5, -0.5, 0.0), (0.5, -0.5, 0.0)
        ]

        colours = [
            (0, 1, 0), (0, 1, 0), (0, 1, 0),
            (0, 1, 0), (0, 1, 0), (0, 1, 0)
        ]

        vertexData = np.hstack([vertices, colours], dtype='float32')

        return vertexData