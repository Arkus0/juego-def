// URP Lit stays responsible for lighting, normal maps, shadows, fog and depth.
// _SpecColor is unused in our metallic workflow (_SPECULAR_SETUP is forbidden):
// x = deterministic identity seed, y = complexion / 5, z = variation strength,
// w = age. Packing in the existing Lit constant buffer retains SRP batching.
#ifndef JUEGODEF_CHARACTER_SKIN_INPUT
#define JUEGODEF_CHARACTER_SKIN_INPUT
#define InitializeStandardLitSurfaceData InitializeCharacterBaseSurfaceData
#include "Packages/com.unity.render-pipelines.universal/Shaders/LitInput.hlsl"
#undef InitializeStandardLitSurfaceData

float CharHash(float2 p) { return frac(sin(dot(p,float2(127.1,311.7))) * 43758.5453); }
float CharNoise(float2 p)
{
    float2 i=floor(p), f=frac(p); f=f*f*(3-2*f);
    return lerp(lerp(CharHash(i),CharHash(i+float2(1,0)),f.x),
                lerp(CharHash(i+float2(0,1)),CharHash(i+1),f.x),f.y);
}
float CharEllipse(float2 p,float2 c,float2 r) { return dot((p-c)/r,(p-c)/r); }

void InitializeStandardLitSurfaceData(float2 uv, out SurfaceData surfaceData)
{
    InitializeCharacterBaseSurfaceData(uv,surfaceData);
    float seed=_SpecColor.x*97.0;
    float type=round(_SpecColor.y*5.0), amount=_SpecColor.z;
    float age=_SpecColor.w;
    // Source atlas face landmarks (same UV layout as char_skin.py). Avoid eyes,
    // lips and the atlas border; no discontinuity is introduced at UV seams.
    float2 q=float2(uv.x,1-uv.y)*2000.0;
    float face=1-smoothstep(.65,1.0,CharEllipse(q,float2(370,410),float2(210,225)));
    float eye=max(exp(-CharEllipse(q,float2(267,355),float2(58,30))),
                  exp(-CharEllipse(q,float2(474,355),float2(58,30))));
    float lip=exp(-CharEllipse(q,float2(370,530),float2(81,34)));
    float cheek=max(exp(-CharEllipse(q,float2(250,455),float2(60,42))),
                    exp(-CharEllipse(q,float2(490,455),float2(60,42))));
    float nose=exp(-CharEllipse(q,float2(370,461),float2(35,43)));
    float eligible=face*(1-eye)*(1-lip);
    float broad=CharNoise(q*.017+seed)-.5;
    float fine=CharNoise(q*.21+seed)-.5;
    // Restrained vascular variation, warm cheeks and nose, cool temples.
    surfaceData.albedo *= 1 + amount*eligible*(broad*.22+fine*.08);
    surfaceData.albedo += amount*eligible*(cheek*.17+nose*.12)*float3(.10,-.018,-.025);
    float weather=(type==2 ? 1 : .25);
    surfaceData.albedo += weather*eligible*(cheek+nose)*float3(.010,-.005,-.007);
    if(type==1 || type==3)
    {
        float2 cell=floor(q/12), local=frac(q/12)-.5;
        float rnd=CharHash(cell+seed);
        float aa=max(fwidth(length(local)),.025);
        float dots=1-smoothstep(.075-aa,.075+aa,length(local));
        float spots=dots*step(type==3 ? .95 : .90,rnd)*eligible;
        surfaceData.albedo *= 1-spots*(type==3 ? .13 : .10);
    }
    if(type==4)
    {
        float mole=exp(-CharEllipse(q,float2(480+seed*.13,480-seed*.16),float2(3,3)))*eligible;
        surfaceData.albedo *= 1-mole*.32;
    }
    if(type==5)
    {
        float scar=exp(-CharEllipse(q,float2(257,429),float2(3,19)))*eligible;
        surfaceData.albedo=lerp(surfaceData.albedo,surfaceData.albedo*float3(1.06,.95,.93),scar*.65);
    }
    surfaceData.smoothness *= saturate(1-eligible*(.22+age*.08)+broad*.15);
}
#endif
