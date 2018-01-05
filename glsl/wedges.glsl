#version 130
in vec3 ourColor;
in vec2 ourTexcoord;
out vec4 outColor;

uniform float time;
uniform vec2 res;

uniform sampler2D texIn;


uniform float beatpt;
uniform float rand1;
uniform float rand1pt;
uniform float rand2;
uniform float rand2pt;
uniform float rand3;
uniform float rand3pt;
uniform float rand4;
uniform float rand4pt;
uniform float beatptaccum;
uniform float beataccumpt;
uniform float rand5;

int tuwat[30] = int[](0x1, 0x1, 0x1F, 0x1, 0x1, 0x0,         // T
                       0x1F, 0x10, 0x10, 0x10, 0x1F, 0x0,    // U
                       0xF, 0x10, 0x1C, 0x10, 0xF, 0x0,      // W
                       0x1E, 0x5, 0x5, 0x5, 0x1E, 0x0,       // A
                       0x1, 0x1, 0x1F, 0x1, 0x1, 0x0);       // T

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


#define tilesize (2+ rand4 * 4. + int(beatpt)*10)
#define borderwidth 0.06
float tile(vec2 fragCoord, float x, float y)
{
    vec2 uv = fract(fragCoord/tilesize);

    float yval = mix(uv.y, (1. - uv.y), step(0.0, -y));
    float xval = mix(uv.x, (1. - uv.x), step(0.0, -x));;


    return smoothstep(1.0 - borderwidth, 1.0 + borderwidth, yval + xval);
}

vec3 pal( in float t, in vec3 a, in vec3 b, in vec3 c, in vec3 d )
{
    return a + b*cos( 6.28318*(c*t+d) );
}

void main()
{
	vec2 uv = 2.*gl_FragCoord.xy/res *1. - vec2(1);
	vec2 uvo = 2.*gl_FragCoord.xy/res *1. - vec2(1);
	vec2 fragCoord = gl_FragCoord.xy;

	//fragCoord.y += rand4pt * tan(uv.x*10 + mod(beataccumpt, 1)*10.) * 10. * (0.5-mod(beataccumpt+0.5, 1));

	fragCoord *= rot2(length(rot2(beataccumpt)* mod(uv, 2) * (rand4pt+0.4) * 0.3));
    //fragCoord *= rot2(1/rand4*3.14159*2 + length(uv*vec2(rand3-0.5, rand2-0.5)));

    //fragCoord = cpow(uv*12., 2);
    fragCoord = cpow(uv*(7+rand3*4), 2);

    // 1/x trafo
    //fragCoord = (10+rand4)/fragCoord;
    fragCoord = mix(fragCoord, (10+rand4)/fragCoord, rand1pt);

    fragCoord *= rot2(beatptaccum*2*rand5 + beatpt*0.4);

	float iTime = time;

    vec2 sc = (floor((fragCoord - res.xy / 2.) / tilesize) + vec2(1));
    sc *= rot2(length(uv)/100000);

    float xfunc = 0;
    xfunc = sin(sc.x*(10000. + dicretize(rand1pt, 10))  * 3.14159*2.) * 1.;
    xfunc += cos(sc.y * 100.) * sin(sc.x * 100.) * rand2;
    xfunc += cos(sin(length(sc)*10)) * rand3;


    float yfunc = 1.;
    yfunc = sin(mod(sc.y*50000., 1.)*3.14159*2.)*rand3;
    yfunc += cos(sin(length(sc)*20)) * rand4;



	float tilemask = tile(fragCoord - res.xy / 2., xfunc, yfunc);

    vec3 color = vec3(rand4pt, rand2pt, rand3pt);
    color = normalize(color);

    // swirl
    color = hsv2rgb(beatpt*0.2 + sin(length(fragCoord)*0.11 + time + atan(fragCoord.y, fragCoord.x)*8*rand5 + rand4), 0.7,1);

    //color *= hsv2rgb(dicretize(length(tan(uv * (1. + rand3pt*3))*(1. + rand1 + rand2 + rand3))+ mod(beataccumpt, 1), 10), 0.7, 1);

    //outColor.rgb = vec3(length(uv))*tilemask * 0.8;
    outColor.rgb = (vec3(1)-color.grb) * (1.-tilemask) * 1.3;

    //outColor.rgb -= texture(texIn, rot2(time*0.5-beatptaccum*1.)*uv*rand5).rgb;
    outColor.rgb -= pal( length(mod(outColor.rgb, 1.)), vec3(0.5,0.5,0.5),vec3(0.5,0.5,0.5),vec3(1.0,0.7,0.4),vec3(0.0,0.15,0.20) );
    outColor.rgb *= 1.0;
    //outColor.rgb -= texture(texIn, fract(rot2(beatpt - beatptaccum + time)*uv*4*beatpt)).rgb * 1.;

    //outColor.rgb *= 0.1;
    //outColor.rgb += texture(texIn, uv*100000000).rgb*texture(texIn, uv*100000).gbr * beatpt;
    //outColor.rgb *= 10;
    //outColor.rgb -= texture(texIn, fract(rot2(beatpt - beatptaccum + time)*uv*0.9*beatpt)).rgb * 1.;
    //outColor.rgb *= texture(texIn, rot2(10*tan(length(uv*0.1)+beatptaccum*(4+rand3)))*uv * (100004000 + rand1 * rand2pt)).rbr;

	outColor.a = 1.;
}