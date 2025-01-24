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
def pack_data(x: int, y: int, z: int, voxelID: int, faceID: int, aoValue: int, needFlip: int) -> int:
    """
    Packs all data into a single 32 bit unsigned integer. The format of the 32 bit integer is as below:
    
    x: 6 bits (0-32 in chunk)
    y: 6 bits (0-32 in chunk)
    z: 6 bits (0-32 in chunk)
    voxelID: 8 bits (255 block types)
    faceID: 3 bits (faces 0-5)
    aoValue: 2 bits (values 0-3)
    needFlip: 1 bit (bool 0 or 1)
    """

    yLen, zLen, voxelIDLen, faceIDLen, aoValueLen, needFlipLen = 6, 6, 8, 3, 2, 1

    packedData = (
        x << yLen + zLen + voxelIDLen + faceIDLen + aoValueLen + needFlipLen |
        y << zLen + voxelIDLen + faceIDLen + aoValueLen + needFlipLen |
        z << voxelIDLen + faceIDLen + aoValueLen + needFlipLen |
        voxelID << faceIDLen + aoValueLen + needFlipLen |
        faceID << aoValueLen + needFlipLen |
        aoValue <<  needFlipLen |
        needFlip
    )

    return packedData


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
def add_data(vertexData: np.array, index: int, *vertices: int) -> int:
    """
    Adds any vertices provided to the vertexData array and updates the index pointer

    :param np.array vertexData: The array of vertices in the mesh
    :param int index: The index of the end of the data in the array
    :param *vertices: Any number of vertices to add to the vertexData array

    :returns: The updated index of the end of the data in the vertexData array
    """

    for vertex in vertices:
        vertexData[index] = vertex
        index += 1

    return index


@njit
def calc_ambient_occlusion(voxelPos: tuple[int, int, int], worldVoxelPos: tuple[int, int, int], worldVoxels: np.array, plane: str) -> tuple[int, int, int, int]:
    """
    Calculates the ambient occlusion value for a given voxel by checking the presence of blocks around the face. The block location
    names surrounding the given face are as follows:

    +---+---+---+\n
    |nw | n |ne |\n
    +---+---+---+\n
    | w | F | e |\n
    +---+---+---+\n
    |sw | s |se |\n
    +---+---+---+\n

    :param tuple voxelPos: The position of the voxel within a given chunk
    :param tuple worldVoxelPos: The position of the voxel within the world
    :param np.array worldVoxels: An array of all of the world Voxels
    :param str plane: The plane of the face

    :returns: The ambient occlusion values for the four corners of the face

    :raises: Exception if plane is invalid
    """

    x, y, z = voxelPos
    worldX, worldY, worldZ = worldVoxelPos

    # For top and bottom faces
    if plane == 'Y':
        n =  is_void((x    , y, z - 1), (worldX    , worldY, worldZ - 1), worldVoxels)
        nw = is_void((x - 1, y, z - 1), (worldX - 1, worldY, worldZ - 1), worldVoxels)
        w =  is_void((x - 1, y, z    ), (worldX - 1, worldY, worldZ    ), worldVoxels)
        sw = is_void((x - 1, y, z + 1), (worldX - 1, worldY, worldZ + 1), worldVoxels)
        s =  is_void((x    , y, z + 1), (worldX    , worldY, worldZ + 1), worldVoxels)
        se = is_void((x + 1, y, z + 1), (worldX + 1, worldY, worldZ + 1), worldVoxels)
        e =  is_void((x + 1, y, z    ), (worldX + 1, worldY, worldZ    ), worldVoxels)
        ne = is_void((x + 1, y, z - 1), (worldX + 1, worldY, worldZ - 1), worldVoxels)

    # For left and right faces
    elif plane == 'X':
        n =  is_void((x, y    , z - 1), (worldX, worldY    , worldZ - 1), worldVoxels)
        nw = is_void((x, y - 1, z - 1), (worldX, worldY - 1, worldZ - 1), worldVoxels)
        w =  is_void((x, y - 1, z    ), (worldX, worldY - 1, worldZ    ), worldVoxels)
        sw = is_void((x, y - 1, z + 1), (worldX, worldY - 1, worldZ + 1), worldVoxels)
        s =  is_void((x, y    , z + 1), (worldX, worldY    , worldZ + 1), worldVoxels)
        se = is_void((x, y + 1, z + 1), (worldX, worldY + 1, worldZ + 1), worldVoxels)
        e =  is_void((x, y + 1, z    ), (worldX, worldY + 1, worldZ    ), worldVoxels)
        ne = is_void((x, y + 1, z - 1), (worldX, worldY + 1, worldZ - 1), worldVoxels)

    # For front and back faces
    elif plane == 'Z':
        n =  is_void((x - 1, y    , z), (worldX - 1, worldY    , worldZ), worldVoxels)
        nw = is_void((x - 1, y - 1, z), (worldX - 1, worldY - 1, worldZ), worldVoxels)
        w =  is_void((x    , y - 1, z), (worldX    , worldY - 1, worldZ), worldVoxels)
        sw = is_void((x + 1, y - 1, z), (worldX + 1, worldY - 1, worldZ), worldVoxels)
        s =  is_void((x + 1, y    , z), (worldX + 1, worldY    , worldZ), worldVoxels)
        se = is_void((x + 1, y + 1, z), (worldX + 1, worldY + 1, worldZ), worldVoxels)
        e =  is_void((x    , y + 1, z), (worldX    , worldY + 1, worldZ), worldVoxels)
        ne = is_void((x - 1, y + 1, z), (worldX - 1, worldY + 1, worldZ), worldVoxels)

    else:
        raise Exception(f"Invalid plane value: {plane}")

    aoValues = (n + nw + w), (e + ne + n), (s + se + e), (w + sw + s)

    return aoValues


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
    vertexData = np.empty(CHUNK_VOLUME * 18 * formatSize, dtype = 'uint32')
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
                    aoValues = calc_ambient_occlusion((x, y + 1, z), (worldX, worldY + 1, worldZ), worldVoxels, 'Y')
                    needFlip = aoValues[1] + aoValues[3] > aoValues[0] + aoValues[2]
                    
                    v0 = pack_data(x    , y + 1, z    , voxelID, 0, aoValues[0], needFlip)
                    v1 = pack_data(x + 1, y + 1, z    , voxelID, 0, aoValues[1], needFlip)
                    v2 = pack_data(x + 1, y + 1, z + 1, voxelID, 0, aoValues[2], needFlip)
                    v3 = pack_data(x    , y + 1, z + 1, voxelID, 0, aoValues[3], needFlip)

                    # Adding vertices for 2 triangles clockwise (Flips the triangles if needed to avoid anisotropy)
                    if needFlip:
                        index = add_data(vertexData, index, v1, v0, v3, v1, v3, v2)
                    else:
                        index = add_data(vertexData, index, v0, v3, v2, v0, v2, v1)

                # Checks whether to add bottom face to mesh
                if is_void((x, y - 1, z), (worldX, worldY - 1, worldZ), worldVoxels):
                    aoValues = calc_ambient_occlusion((x, y - 1, z), (worldX, worldY - 1, worldZ), worldVoxels, 'Y')
                    needFlip = aoValues[1] + aoValues[3] > aoValues[0] + aoValues[2]

                    v0 = pack_data(x    , y, z    , voxelID, 1, aoValues[0], needFlip)
                    v1 = pack_data(x + 1, y, z    , voxelID, 1, aoValues[1], needFlip)
                    v2 = pack_data(x + 1, y, z + 1, voxelID, 1, aoValues[2], needFlip)
                    v3 = pack_data(x    , y, z + 1, voxelID, 1, aoValues[3], needFlip)

                    # Adding vertices for 2 triangles clockwise (Flips the triangles if needed to avoid anisotropy)
                    if needFlip:
                        index = add_data(vertexData, index, v1, v3, v0, v1, v2, v3)
                    else:
                        index = add_data(vertexData, index, v0, v2, v3, v0, v1, v2)

                # Checks whether to add right face to mesh
                if is_void((x + 1, y, z), (worldX + 1, worldY, worldZ), worldVoxels):
                    aoValues = calc_ambient_occlusion((x + 1, y, z), (worldX + 1, worldY, worldZ), worldVoxels, 'X')
                    needFlip = aoValues[1] + aoValues[3] > aoValues[0] + aoValues[2]

                    v0 = pack_data(x + 1, y    , z    , voxelID, 2, aoValues[0], needFlip)
                    v1 = pack_data(x + 1, y + 1, z    , voxelID, 2, aoValues[1], needFlip)
                    v2 = pack_data(x + 1, y + 1, z + 1, voxelID, 2, aoValues[2], needFlip)
                    v3 = pack_data(x + 1, y    , z + 1, voxelID, 2, aoValues[3], needFlip)

                    # Adding vertices for 2 triangles clockwise (Flips the triangles if needed to avoid anisotropy)
                    if needFlip:
                        index = add_data(vertexData, index, v3, v0, v1, v3, v1, v2)
                    else:
                        index = add_data(vertexData, index, v0, v1, v2, v0, v2, v3)

                # Checks whether to add left face to mesh
                if is_void((x - 1, y, z), (worldX - 1, worldY, worldZ), worldVoxels):
                    aoValues = calc_ambient_occlusion((x - 1, y, z), (worldX - 1, worldY, worldZ), worldVoxels, 'X')
                    needFlip = aoValues[1] + aoValues[3] > aoValues[0] + aoValues[2]

                    v0 = pack_data(x, y    , z    , voxelID, 3, aoValues[0], needFlip)
                    v1 = pack_data(x, y + 1, z    , voxelID, 3, aoValues[1], needFlip)
                    v2 = pack_data(x, y + 1, z + 1, voxelID, 3, aoValues[2], needFlip)
                    v3 = pack_data(x, y    , z + 1, voxelID, 3, aoValues[3], needFlip)

                    # Adding vertices for 2 triangles clockwise (Flips the triangles if needed to avoid anisotropy)
                    if needFlip:
                        index = add_data(vertexData, index, v3, v1, v0, v3, v2, v1)
                    else:
                        index = add_data(vertexData, index, v0, v2, v1, v0, v3, v2)

                # Checks whether to add back face to mesh
                if is_void((x, y, z - 1), (worldX, worldY, worldZ - 1), worldVoxels):
                    aoValues = calc_ambient_occlusion((x, y, z - 1), (worldX, worldY, worldZ - 1), worldVoxels, 'Z')
                    needFlip = aoValues[1] + aoValues[3] > aoValues[0] + aoValues[2]

                    v0 = pack_data(x    , y    , z, voxelID, 4, aoValues[0], needFlip)
                    v1 = pack_data(x    , y + 1, z, voxelID, 4, aoValues[1], needFlip)
                    v2 = pack_data(x + 1, y + 1, z, voxelID, 4, aoValues[2], needFlip)
                    v3 = pack_data(x + 1, y    , z, voxelID, 4, aoValues[3], needFlip)

                    # Adding vertices for 2 triangles clockwise (Flips the triangles if needed to avoid anisotropy)
                    if needFlip:
                        index = add_data(vertexData, index, v3, v0, v1, v3, v1, v2)
                    else:
                        index = add_data(vertexData, index, v0, v1, v2, v0, v2, v3)

                # Checks whether to add front face to mesh
                if is_void((x, y, z + 1), (worldX, worldY, worldZ + 1), worldVoxels):
                    aoValues = calc_ambient_occlusion((x, y, z + 1), (worldX, worldY, worldZ + 1), worldVoxels, 'Z')
                    needFlip = aoValues[1] + aoValues[3] > aoValues[0] + aoValues[2]

                    v0 = pack_data(x    , y    , z + 1, voxelID, 5, aoValues[0], needFlip)
                    v1 = pack_data(x    , y + 1, z + 1, voxelID, 5, aoValues[1], needFlip)
                    v2 = pack_data(x + 1, y + 1, z + 1, voxelID, 5, aoValues[2], needFlip)
                    v3 = pack_data(x + 1, y    , z + 1, voxelID, 5, aoValues[3], needFlip)

                    # Adding vertices for 2 triangles clockwise (Flips the triangles if needed to avoid anisotropy)
                    if needFlip:
                        index = add_data(vertexData, index, v3, v1, v0, v3, v2, v1)
                    else:
                        index = add_data(vertexData, index, v0, v2, v1, v0, v3, v2)

    # Only return the none empty areas of the array that has vertex data in
    return vertexData[:index + 1]