from overrides import overrides

from settings import *
from Meshes.BaseMesh import BaseMesh
from Meshes.chunkMeshBuilder import build_chunk_mesh
import WorldObjects.Chunk


class ChunkMesh(BaseMesh):
    def __init__(self, chunk: 'WorldObjects.Chunk.Chunk') -> None:
        """
        Class that stores chunk mesh data

        :param Chunk chunk: The Chunk object to bulid mesh data from
        """

        super().__init__()

        self.chunk = chunk
        self.app = chunk.app
        self.context = self.app.context
        self.shaderProgram = self.app.shaderProgram.chunk

        self.vboFormat = "3u1 1u1 1u1"
        self.formatSize = sum(int(format[:1]) for format in self.vboFormat.split())
        self.attrs = ("inPosition", "voxelID", "faceID")
        self.vao = self.get_vao()


    @overrides
    def get_vertex_data(self) -> np.array:
        """
        Builds the chunk mesh and returns it as a numpy array
        
        :returns: A numpy array containing all of the mesh data for the chunk
        """
        
        mesh = build_chunk_mesh(
            chunkVoxels=self.chunk.voxels,
            formatSize=self.formatSize,
            chunkPos=self.chunk.position,
            worldVoxels=self.chunk.world.voxels)

        return mesh