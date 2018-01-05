#version 130
in vec3 ourColor;
in vec2 ourTexcoord;
out vec4 outColor;

uniform float time;
uniform vec2 res;

uniform float test;
uniform float green;

void main()
{
    vec2 uv = mod(gl_FragCoord.xy/res *1., 1.);


    outColor = vec4(abs(sin(test)), green*0.01, 0., 1.0);
}