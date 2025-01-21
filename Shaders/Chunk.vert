#version 330 core

layout (location = 0) in ivec3 inPosition;
layout (location = 1) in int voxelID;
layout (location = 2) in int faceID;

uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat4 modelMatrix;

out vec3 voxel_colour;
out vec2 uv;

const vec2 uv_coords[4] = vec2[4] (
    vec2(0, 0), vec2(0, 1),
    vec2(1, 0), vec2(1, 1)
);

const int uv_indices[12] = int[12] (
    1, 0, 2, 1, 2, 3,   // Texture coordinate indices for vertices of an even face
    3, 0, 2, 3, 1, 0    // Texture coordinate indices for vertices of an odd face
);

vec3 hash31(float p) {
    vec3 p3 = fract(vec3(p * 21.2) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xxy + p3.yzz) * p3.zyx);
}

void main() {
    int uv_index = gl_VertexID % 6 + (faceID & 1) * 6;
    uv = uv_coords[uv_indices[uv_index]];
    voxel_colour = hash31(voxelID);
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(inPosition, 1.0);
}