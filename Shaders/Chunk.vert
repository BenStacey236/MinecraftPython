#version 330 core

layout (location = 0) in uint packedData;

int x, y, z;
int voxelID;
int faceID;
int aoID;
int needFlip;

uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat4 modelMatrix;

out vec3 voxel_colour;
out vec2 uv;
out float shading;

const float aoValues[4] = float[4] (0.1, 0.25, 0.5, 1.0);

const float faceShading[6] = float[6] (
    1.0, 0.5, // Top and bottom faces
    0.5, 0.8, // Right and left faces
    0.5, 0.8  // Front and back Faces
);

const vec2 uv_coords[4] = vec2[4] (
    vec2(0, 0), vec2(0, 1),
    vec2(1, 0), vec2(1, 1)
);

const int uv_indices[24] = int[24] (
    1, 0, 2, 1, 2, 3,   // Texture coordinate indices for vertices of an even face (no flip)
    3, 0, 2, 3, 1, 0,   // Texture coordinate indices for vertices of an odd face (no flip)
    3, 1, 0, 3, 0, 2,   // Texture coordinate indices for vertices of an even face (flipped)
    1, 2, 3, 1, 0, 2    // Texture coordinate indices for vertices of an odd face (flipped)
);

vec3 hash31(float p) {
    vec3 p3 = fract(vec3(p * 21.2) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xxy + p3.yzz) * p3.zyx);
}


void unpack(uint packedData) {
    // x, y, z, voxelID, faceID, aoValue, needFlip

    uint yLen = 6u, zLen = 6u, voxelIDLen = 8u, faceIDLen = 3u, aoIDLen = 2u, needFlipLen = 1u;
    uint yMask = 63u, zMask = 63u, voxelIDMask = 255u, faceIDMask = 7u, aoIDMask = 3u, needFlipMask = 1u;

    x = int(packedData >> (yLen + zLen + voxelIDLen + faceIDLen + aoIDLen + needFlipLen));
    y = int((packedData >> (zLen + voxelIDLen + faceIDLen + aoIDLen + needFlipLen)) & yMask);
    z = int((packedData >> (voxelIDLen + faceIDLen + aoIDLen + needFlipLen)) & zMask);
    voxelID = int((packedData >> (faceIDLen + aoIDLen + needFlipLen)) & voxelIDMask);
    faceID = int((packedData >> (aoIDLen + needFlipLen) & faceIDMask));
    aoID = int((packedData >> needFlipLen) & aoIDMask);
    needFlip = int(packedData & needFlipMask);
}   


void main() {
    unpack(packedData);
    vec3 inPosition = vec3(x, y, z);

    // Texturing
    int uv_index = gl_VertexID % 6 + ((faceID & 1) + needFlip * 2) * 6;
    uv = uv_coords[uv_indices[uv_index]];

    // Colouring and shading
    voxel_colour = hash31(voxelID);
    shading = faceShading[faceID] * aoValues[aoID];
    
    // Vertex positions
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(inPosition, 1.0);
}