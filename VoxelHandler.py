from settings import *
from Meshes.chunkMeshBuilder import get_chunk_index
import World
from WorldObjects.Chunk import Chunk


class VoxelHandler:
    def __init__(self, world: 'World.World') -> None:
        """
        Class that handles interaction between player and world voxels
        
        :param World world: The world object that the VoxelHandler will work in
        """

        self.app = world.app
        self.chunks = world.chunks

        # Results of ray casting
        self.chunk: Chunk = None
        self.voxelID = None
        self.voxelIndex = None
        self.voxelLocalPos = None
        self.voxelWorldPos = None
        self.voxelNormal = None
        
        # Interaction modes:
        # 0: Break blocks
        # 1: Place blocks
        self.interactionMode = 0
        self.newVoxelID = 1


    def update(self) -> None:
        "Updates the VoxelHandler"

        self.ray_cast()


    def switch_interaction_mode(self, interactionMode: int = -1) -> None:
        """
        Switches the interaction mode (by default swaps between mode 0 and 1)
        
        :param int interactionMode: A specific interaction mode to switch to
        """
        
        if interactionMode != -1:
            self.interactionMode = interactionMode
        else:
            self.interactionMode = not self.interactionMode

    
    def set_voxel(self) -> None:
        """
        Either places or removes a block depending on the interaction Mode
        
        :raises: Exception when interaction mode is invalid
        """

        if self.interactionMode == 1:
            self.add_voxel()
        
        elif self.interactionMode == 0:
            self.remove_voxel()

        else:
            raise Exception(f"Invalid interaction mode when setting voxel: {self.interactionMode}")


    def add_voxel(self) -> None:
        "Places a block against the face of block that is currently being looked at"

        if self.voxelID:
            # Check that the place we are going to place at is empty
            result = self.get_voxel_id(self.voxelWorldPos + self.voxelNormal)
            if not result[0]:
                _, voxelIndex, _, chunk = result
                chunk.voxels[voxelIndex] = self.newVoxelID
                chunk.mesh.rebuild_mesh()
                self.check_chunk_rebuilds()

                # Marks empty chunks as not empty so they get rendered
                if chunk.isEmpty:
                    chunk.isEmpty = False


    def remove_voxel(self) -> None:
        "Breaks the block that a raycast intersects with"

        # Only remove a block if a block is in raycast
        if self.voxelID:
            self.chunk.voxels[self.voxelIndex] = 0
            self.chunk.mesh.rebuild_mesh()
            self.check_chunk_rebuilds()


    def rebuild_adjacent_chunk(self, adjVoxelPos: tuple[int, int, int]) -> None:
        """
        Rebuilds the mesh of an adjacent chunk
        
        :param tuple adjVoxelPos: The (x, y, z) coordinate of a voxel in the chunk that needs rebuilding
        """
        
        index = get_chunk_index(adjVoxelPos)
        if index != -1:
            self.chunks[index].mesh.rebuild_mesh()


    def check_chunk_rebuilds(self) -> None:
        "Checks to see which chunks need rebuilding around a certain block if it is on chunk boundaries"

        localX, localY, localZ = self.voxelLocalPos
        worldX, worldY, worldZ = self.voxelWorldPos

        if localX == 0:
            self.rebuild_adjacent_chunk((worldX - 1, worldY, worldZ))
        elif localX == CHUNK_SIZE - 1:
            self.rebuild_adjacent_chunk((worldX + 1, worldY, worldZ))

        if localY == 0:
            self.rebuild_adjacent_chunk((worldX, worldY - 1, worldZ))
        elif localY == CHUNK_SIZE - 1:
            self.rebuild_adjacent_chunk((worldX, worldY + 1, worldZ))

        if localZ == 0:
            self.rebuild_adjacent_chunk((worldX, worldY, worldZ - 1))
        elif localZ == CHUNK_SIZE - 1:
            self.rebuild_adjacent_chunk((worldX, worldY, worldZ + 1))


    def ray_cast(self) -> bool:
        """
        Casts a ray into the world and determines if the ray intersects a voxel in the world within player reach
        
        :returns: True if raycast instersects a voxel, otherwise False
        """

        x1, y1, z1 = self.app.player.pos                                                # Start position of ray
        x2, y2, z2 = self.app.player.pos + self.app.player.forward * MAX_PLAYER_REACH   # Maximum end position of ray

        currentVoxelPos = glm.ivec3(x1, y1, z1)
        self.voxelID = 0
        self.voxelNormal = glm.ivec3(0)
        stepDirection = -1

        dx = glm.sign(x2 - x1)
        deltaX = min(dx / (x2 - x1), 10000000.0) if dx != 0 else 10000000.0
        maxX = deltaX * (1.0 - glm.fract(x1)) if dx > 0 else deltaX * glm.fract(x1)

        dy = glm.sign(y2 - y1)
        deltaY = min(dy / (y2 - y1), 10000000.0) if dy != 0 else 10000000.0
        maxY = deltaY * (1.0 - glm.fract(y1)) if dy > 0 else deltaY * glm.fract(y1)

        dz = glm.sign(z2 - z1)
        deltaZ = min(dz / (z2 - z1), 10000000.0) if dz != 0 else 10000000.0
        maxZ = deltaZ * (1.0 - glm.fract(z1)) if dz > 0 else deltaZ * glm.fract(z1)

        while not (maxX > 1.0 and maxY > 1.0 and maxZ > 1.0):
            # Updates voxel information for the collided voxel
            result = self.get_voxel_id(currentVoxelPos)
            if result[0]:
                self.voxelID, self.voxelIndex, self.voxelLocalPos, self.chunk = result
                self.voxelWorldPos = currentVoxelPos

                if stepDirection == 0:
                    self.voxelNormal.x = -dx
                elif stepDirection == 1:
                    self.voxelNormal.y = -dy
                else:
                    self.voxelNormal.z = -dz

                return True
            
            if maxX < maxY:
                if maxX < maxZ:
                    currentVoxelPos.x += dx
                    maxX += deltaX
                    stepDirection = 0
                else:
                    currentVoxelPos.z += dz
                    maxZ += deltaZ
                    stepDirection = 2

            else:
                if maxY < maxZ:
                    currentVoxelPos.y += dy
                    maxY += deltaY
                    stepDirection = 1
                else:
                    currentVoxelPos.z += dz
                    maxZ += deltaZ
                    stepDirection = 2

        return False
    

    def get_voxel_id(self, voxelWorldPos: tuple[int, int, int]) -> tuple[int, int, int, 'Chunk']:
        """
        Returns voxel information for a voxel at a given world position
        
        :param tuple voxelWorldPos: The (x, y, z) coordinate of the voxel to get information of
        
        :returns: VoxelID, voxelIndex, voxelLocalPos, chunk
        """

        chunkX, chunkY, chunkZ = chunkPos = voxelWorldPos / CHUNK_SIZE

        if 0 <= chunkX < WORLD_WIDTH and 0 <= chunkY < WORLD_HEIGHT and 0 <= chunkZ < WORLD_DEPTH:
            chunkIndex = chunkX + WORLD_WIDTH * chunkZ + WORLD_AREA * chunkY
            chunk: Chunk = self.chunks[chunkIndex]

            localX, localY, localZ = voxelLocalPos = voxelWorldPos - chunkPos * CHUNK_SIZE
            
            voxelIndex = localX + CHUNK_SIZE * localZ + CHUNK_AREA * localY
            voxelID = chunk.voxels[voxelIndex]

            return voxelID, voxelIndex, voxelLocalPos, chunk
        
        return 0, 0, 0, 0