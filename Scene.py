from settings import *
from World import World
import Engine


class Scene:
    def __init__(self, app: 'Engine.Engine') -> None:
        "Class that stores and renders the current Scene"

        self.app = app
        self.world = World(self.app)


    def update(self) -> None:
        "Updates the current scene"

        self.world.update()


    def render(self) -> None:
        "Renders the current scene"
        
        self.world.render()