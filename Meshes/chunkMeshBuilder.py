from settings import *
from numba import uint8


""" 
FACE ID's ARE AS FOLLOWS:
0 - TOP FACE
1 - BOTTOM FACE
2 - RIGHT FACE
3 - LEFT FACE
4 - BACK FACE
5 - FRONT FACE
"""


@njit
def to_uint8(x, y, z, voxelID, faceID):
    "Converts all arguments to uint8"
    
    return uint8(x), uint8(y), uint8(z), uint8(voxelID), uint8(faceID)


@njit
def get_chunk_index(worldVoxelPos: tuple[int, int, int]) -> int:
    """
    Calculates the chunk index of a chunk the provided voxel is in

    :param tuple worldVoxelPos: The voxel position of the voxel in the world
    
    :returns: The index of the chunk the provided voxel is in (Or -1 if the voxel is ouside of the world)
    """

    worldX, worldY, worldZ = worldVoxelPos
    chunkX = worldX // CHUNK_SIZE
    chunkY = worldY // CHUNK_SIZE
    chunkZ = worldZ // CHUNK_SIZE

    # Checks first if coordinate is in bounds of the world
    if not (0 <= chunkX < WORLD_WIDTH and 0 <= chunkY < WORLD_HEIGHT and 0 <= chunkZ < WORLD_DEPTH):
        return -1
    
    chunkIndex = chunkX + WORLD_WIDTH * chunkZ + WORLD_AREA * chunkY

    return chunkIndex


@njit
def is_void(voxelPos: tuple[int, int, int], worldVoxelPos: tuple[int, int, int], worldVoxels: np.array) -> bool:
    """
    Checks to see if the voxel at the given coordinate is a solid block

    :param tuple voxelPos: A tuple containing the (x, y, z) coordinate to check whether is solid
    :param tuple worldVoxelPos: A tuple containing the world (x, y, z) coordinate to check whether is solid
    :param np.array worldVoxels: An array of the voxels in the given chunk

    :returns: True if provided coordinate is a void block, otherwise False
    """

    chunkIndex = get_chunk_index(worldVoxelPos)
    if chunkIndex == -1:
        return False

    chunkVoxels = worldVoxels[chunkIndex]

    x, y, z = voxelPos
    voxelIndex = x % CHUNK_SIZE + z % CHUNK_SIZE * CHUNK_SIZE + y % CHUNK_SIZE * CHUNK_AREA

    # Checks if there is a voxel present at the coordinate
    if chunkVoxels[voxelIndex]:
        return False
    
    return True


@njit
def add_data(vertexData: np.array, index: int, *vertices: tuple[tuple[int, ...]]) -> int:
    """
    Adds any vertices provided to the vertexData array and updates the index pointer

    :param np.array vertexData: The array of vertices in the mesh
    :param int index: The index of the end of the data in the array
    :param *vertices: Any number of vertices to add to the vertexData array

    :returns: The updated index of the end of the data in the vertexData array
    """

    for vertex in vertices:
        for attribute in vertex:
            vertexData[index] = attribute
            index += 1

    return index


@njit
def build_chunk_mesh(chunkVoxels: np.array, formatSize: int, chunkPos: tuple[int, int, int], worldVoxels: np.array) -> np.array:
    """
    Builds the mesh for a chunk from an array of voxels
    
    :param np.array chunkVoxels: The array of voxels to build mesh from
    :param int formatSize: The number of items representing each vertex
    :param tuple chunkPos: The position of the chunk in the world
    :param np.array worldVoxels: A numpy array storing all of the voxels present in the world
    
    :returns: A numpy array of vertices
    """

    # 18 Comes from the maximum number of vertices visible on one voxel at any time
    vertexData = np.empty(CHUNK_VOLUME * 18 * formatSize, dtype = 'uint8')
    index = 0


    for x in range(CHUNK_SIZE):
        for y in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                voxelID = chunkVoxels[x + CHUNK_SIZE * z + CHUNK_AREA * y]

                if not voxelID:
                    continue
                
                # Calculate voxel's world position
                chunkX, chunkY, chunkZ = chunkPos
                worldX = x + chunkX * CHUNK_SIZE
                worldY = y + chunkY * CHUNK_SIZE
                worldZ = z + chunkZ * CHUNK_SIZE

                # Checks whether to add top face to mesh
                if is_void((x, y + 1, z), (worldX, worldY + 1, worldZ), worldVoxels):
                    v0 = to_uint8(x    , y + 1, z    , voxelID, 0)
                    v1 = to_uint8(x + 1, y + 1, z    , voxelID, 0)
                    v2 = to_uint8(x + 1, y + 1, z + 1, voxelID, 0)
                    v3 = to_uint8(x    , y + 1, z + 1, voxelID, 0)

                    # Adding vertices for 2 triangles clockwise
                    index = add_data(vertexData, index, v0, v3, v2, v0, v2, v1)

                # Checks whether to add bottom face to mesh
                if is_void((x, y - 1, z), (worldX, worldY - 1, worldZ), worldVoxels):
                    v0 = to_uint8(x    , y, z    , voxelID, 1)
                    v1 = to_uint8(x + 1, y, z    , voxelID, 1)
                    v2 = to_uint8(x + 1, y, z + 1, voxelID, 1)
                    v3 = to_uint8(x    , y, z + 1, voxelID, 1)

                    # Adding vertices for 2 triangles clockwise
                    index = add_data(vertexData, index, v0, v2, v3, v0, v1, v2)

                # Checks whether to add right face to mesh
                if is_void((x + 1, y, z), (worldX + 1, worldY, worldZ), worldVoxels):
                    v0 = to_uint8(x + 1, y    , z    , voxelID, 2)
                    v1 = to_uint8(x + 1, y + 1, z    , voxelID, 2)
                    v2 = to_uint8(x + 1, y + 1, z + 1, voxelID, 2)
                    v3 = to_uint8(x + 1, y    , z + 1, voxelID, 2)

                    # Adding vertices for 2 triangles clockwise
                    index = add_data(vertexData, index, v0, v1, v2, v0, v2, v3)

                # Checks whether to add left face to mesh
                if is_void((x - 1, y, z), (worldX - 1, worldY, worldZ), worldVoxels):
                    v0 = to_uint8(x, y    , z    , voxelID, 3)
                    v1 = to_uint8(x, y + 1, z    , voxelID, 3)
                    v2 = to_uint8(x, y + 1, z + 1, voxelID, 3)
                    v3 = to_uint8(x, y    , z + 1, voxelID, 3)

                    # Adding vertices for 2 triangles clockwise
                    index = add_data(vertexData, index, v0, v2, v1, v0, v3, v2)

                # Checks whether to add back face to mesh
                if is_void((x, y, z - 1), (worldX, worldY, worldZ - 1), worldVoxels):
                    v0 = to_uint8(x    , y    , z, voxelID, 4)
                    v1 = to_uint8(x    , y + 1, z, voxelID, 4)
                    v2 = to_uint8(x + 1, y + 1, z, voxelID, 4)
                    v3 = to_uint8(x + 1, y    , z, voxelID, 4)

                    # Adding vertices for 2 triangles clockwise
                    index = add_data(vertexData, index, v0, v1, v2, v0, v2, v3)

                # Checks whether to add front face to mesh
                if is_void((x, y, z + 1), (worldX, worldY, worldZ + 1), worldVoxels):
                    v0 = to_uint8(x    , y    , z + 1, voxelID, 5)
                    v1 = to_uint8(x    , y + 1, z + 1, voxelID, 5)
                    v2 = to_uint8(x + 1, y + 1, z + 1, voxelID, 5)
                    v3 = to_uint8(x + 1, y    , z + 1, voxelID, 5)

                    # Adding vertices for 2 triangles clockwise
                    index = add_data(vertexData, index, v0, v2, v1, v0, v3, v2)

    # Only return the none empty areas of the array that has vertex data in
    return vertexData[:index + 1]