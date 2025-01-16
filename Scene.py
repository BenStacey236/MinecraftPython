from settings import *
from Meshes.QuadMesh import QuadMesh


class Scene:
    def __init__(self, app) -> None:
        "Class that stores and renders the current Scene"

        self.app = app
        self.quad = QuadMesh(self.app)


    def update(self) -> None:
        "Updates the current scene"

        pass


    def render(self) -> None:
        "Renders the current scene"
        
        self.quad.render()