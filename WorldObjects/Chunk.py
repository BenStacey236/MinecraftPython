import random

from settings import *
from Meshes.ChunkMesh import ChunkMesh
import World


class Chunk:
    def __init__(self, world: 'World.World', position: tuple[int, int, int]) -> None:
        """
        Class that stores all of the data for a chunk

        :param World world: The world that the chunk is in
        :param tuple position: The (x, y, z) position of the chunk in the world
        """

        self.world = world
        self.app = world.app
        self.position = position
        self.modelMatrix = self.get_model_matrix()
        self.voxels: np.array = None
        self.mesh: ChunkMesh = None
        self.isEmpty = True

    
    def build_voxels(self) -> np.array:
        """
        Builds the voxel data for a chunk

        :returns: A numpy array of block types stored as 8-bit integers
        """

        # Empty Chunk for now
        voxels = np.zeros(CHUNK_VOLUME, dtype='uint8')

        # fill chunk
        chunkX, chunkY, chunkZ = glm.ivec3(self.position) * CHUNK_SIZE
        chunkBlockType = random.randrange(1, 100)

        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                worldX = x + chunkX
                worldZ = z + chunkZ
                worldHeight = int(glm.simplex(glm.vec2(worldX, worldZ) * 0.01) * 32 + 32)
                localHeight = min(worldHeight - chunkY, CHUNK_SIZE)

                for y in range(localHeight):
                    worldY = y + chunkY
                    voxels[x + CHUNK_SIZE * z + CHUNK_AREA * y] = chunkBlockType

        if np.any(voxels):
            self.isEmpty = False

        return voxels
    

    def build_mesh(self) -> None:
        "Builds the mesh for the current chunk"

        self.mesh = ChunkMesh(self)


    def get_model_matrix(self) -> np.array:
        """
        Gets the model matrix for the current chunk
        
        :returns: A numpy array representing the model matrix
        """

        modelMatrix = glm.translate(glm.mat4(), glm.vec3(self.position) * CHUNK_SIZE)
        
        return modelMatrix
    

    def set_uniform(self) -> None:
        "Sets the uniforms for the chunk mesh"

        self.mesh.shaderProgram['modelMatrix'].write(self.modelMatrix)


    def render(self) -> None:
        "Renders the current chunk"
        
        if not self.isEmpty:
            self.set_uniform()
            self.mesh.render()