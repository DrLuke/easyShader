#version 130
in vec3 ourColor;
in vec2 ourTexcoord;
out vec4 outColor;

uniform float time;
uniform vec2 res;

uniform float tsize;
uniform float colormaster;
uniform float colorfreq;

uniform float beatpt;
uniform float beatptaccum;

uniform float rand1;
uniform float rand2;
uniform float rand3;
uniform float rand4;

uniform sampler2D texIn;

int tuwat[30] = int[](0x1, 0x1, 0x1F, 0x1, 0x1, 0x0,         // T
                       0x1F, 0x10, 0x10, 0x10, 0x1F, 0x0,    // U
                       0xF, 0x10, 0x1C, 0x10, 0xF, 0x0,      // W
                       0x1E, 0x5, 0x5, 0x5, 0x1E, 0x0,       // A
                       0x1, 0x1, 0x1F, 0x1, 0x1, 0x0);       // T

int hello[30] = int[](0x1F, 0x4, 0x4, 0x4, 0xF, 0x0,      // T
                       0x1F, 0x15, 0x15, 0x15, 0x15, 0x0,    // U
                       0x1F, 0x10, 0x10, 0x10, 0x10, 0x0,      // N
                       0x1F, 0x10, 0x10, 0x10, 0x10, 0x0,       // A
                       0x1F, 0x11, 0x11, 0x11, 0x1F, 0x0);       // T

int lolol[30] = int[](0x1F, 0x10, 0x10, 0x10, 0x10, 0x0,       // A
                       0x1F, 0x11, 0x11, 0x11, 0x1F, 0x0,    // U
                       0x1F, 0x10, 0x10, 0x10, 0x10, 0x0,       // A
                       0x1F, 0x11, 0x11, 0x11, 0x1F, 0x0,       // A
                       0x1F, 0x10, 0x10, 0x10, 0x10, 0x0);       // T

vec3 hsv2rgb(float h, float s, float v) {
  vec3 c = vec3(h,s,v);
  vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
  vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
  return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

float dicretize(float i, float s)
{
    return floor(i*s)/s;
}

mat2 rot2(float a) {
	float s = sin(a);
	float c = cos(a);
	mat2 m = mat2(c, -s, s, c);
	return m;
}

vec2 cexp(vec2 z)
{
    return exp(z.x) * vec2(cos(z.y), sin(z.y));
}

vec2 clog(vec2 z)
{
    return vec2(log(length(z)), atan(z.y, z.x));
}

vec2 cpow(vec2 z, float p)
{
    return cexp(clog(z) * p);
}

vec3 pal( in float t, in vec3 a, in vec3 b, in vec3 c, in vec3 d )
{
    return a + b*cos( 6.28318*(c*t+d) );
}

void main()
{
    vec2 uv = 2.*gl_FragCoord.xy/res *1. - vec2(1);
    vec2 uvo = 2.*gl_FragCoord.xy/res *1. - vec2(1);
    uv.x = res.x / res.y;
    uvo.x = res.x / res.y;


    // Scale coordinates
    vec2 fg = gl_FragCoord.xy;

    fg -= res/2.;
    fg /= tsize  + sin(mod(beatptaccum*0.1, 2) * 3.14159) + beatpt*20*0;

    //fg.x = dicretize(fg.x, rand2+0.2);
    //fg.y = dicretize(fg.y, rand3+0.2);

    //fg = 10000/(rot2(time*0.4 - beatptaccum*0.3 + beatpt)*fg*length(uvo));

    // Waveyness
    //fg.y += rand2*tan(fg.x/200. + mod(time*0.1 + beatptaccum, 2.*3.14159)) * colorfreq * 1;

    //fg.x = dicretize(fg.x, rand4*0.4);

    //fg *= rot2(-rand3 * time * 0.2 + dicretize(rand3*length(uv.x), float(rand1)*1) + rand3*beatptaccum);
    //fg *= rot2(-rand3 * time * 0.2 + rand3 + beatptaccum * rand4);

    //fg = cpow(fg/((1+rand4)*20), +3 + rand4*1 + length(uv));
    //fg = cpow(fg/((1+rand4)*1000), -3 - rand4*1);

    // Generate mask
    //int line = 5-int(fg.y - 1000.) % (6);
    //int row = int(fg.x - 2000.) % (30) ;
    int line = 5-int(fg.y - 1000. + int(beatptaccum)) % (6 + int(rand2)*10);    // 6
    int row = int(fg.x - 2000.) % (30 + int(rand2)*10);   // 30
    int pix = lolol[row] & (int(1 + (line + row)*rand4*0) << line);

    //Output
    float tuwatmask = step(1., float(pix));

    // Colormode 1
    outColor.rgb = hsv2rgb(length(uv*colorfreq) - sin(mod(beatpt * 0.2 * 3.14159, 2.*3.14159)),colormaster,colormaster)*tuwatmask;

    // Colormode 2
    //outColor.rgb += hsv2rgb(dicretize(fg.y/res.y * 10, beatpt*10.+1.) + mod(time * 0.1, 1.), colormaster, colormaster) * tuwatmask;

    // Colormode 2
    outColor.rgb *= hsv2rgb(dicretize(fg.x/res.y * 10, beatpt*10.+1.) + mod(time * 0.1, 1.), colormaster, colormaster) * tuwatmask;

    // Neat kap0tts
    //outColor.rgb *= hsv2rgb(uv.x*10. + beatptaccum, colormaster, 1) * tuwatmask;

    //superkap0tt
    //outColor.rgb -= 0.2*pal( length(mod(outColor.bgr, 1.)), vec3(0.5,0.5,0.5),vec3(0.5,0.5,0.5),vec3(1.0,0.7,0.4),vec3(0.0,0.15,0.20) );
    //outColor.rgb *= 1.4;

    //outColor.rgb = mix(outColor.rgb, vec3(0.6)-outColor.rgb*0.5, step(0.5, rand4));
    outColor.a = 1.;
}