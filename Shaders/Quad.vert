#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec3 inColour;

uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat4 modelMatrix;

out vec3 colour;


void main() {
    colour = inColour;
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(inPosition, 1.0);
}