from settings import *
from WorldObjects.Chunk import Chunk
import Engine


class World:
    def __init__(self, app: 'Engine.Engine') -> None:
        """
        Class that stores all of the data for the world
        
        :param Engine app: The current engine that the world is associated to
        """

        self.app = app

        self.chunks: list[Chunk] = [None for _ in range(WORLD_VOLUME)]
        self.voxels = np.empty([WORLD_VOLUME, CHUNK_VOLUME], dtype='uint8')
        self.build_chunks()
        self.build_chunk_meshes()


    def build_chunks(self) -> None:
        "Builds the voxels for all of the chunks in the world"

        for x in range(WORLD_WIDTH):
            for y in range(WORLD_HEIGHT):
                for z in range(WORLD_DEPTH):
                    chunk = Chunk(self, position=(x, y, z))

                    chunk_index = x + WORLD_HEIGHT * z + WORLD_AREA * y
                    
                    self.chunks[chunk_index] = chunk
                    self.voxels[chunk_index] = chunk.build_voxels()

                    chunk.voxels = self.voxels[chunk_index]


    def build_chunk_meshes(self) -> None:
        "Builds the meshes for all of the chunks"

        for chunk in self.chunks:
            chunk.build_mesh()


    def update(self) -> None:
        "Updates the world"

        pass


    def render(self) -> None:
        "Renders all of the chunks in the world"

        for chunk in self.chunks:
            chunk.render()