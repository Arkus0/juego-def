// Distant mountain range behind the district hills (EnvDistrict.MountainRange). Flat-shaded low-poly facets lit by the
// main light and hazed towards the scene fog colour here, not by the fog itself: the linear fog ends before the range
// and would erase it. Vertex colour: r = height on the range (0 foot .. 1 crest), g = bare rock share, b = far layer.
Shader "JuegoDef/ENV/Backdrop Range"
{
    Properties
    {
        _LowColor ("Foot (woods)", Color) = (0.37, 0.43, 0.38, 1)
        _HighColor ("Crest", Color) = (0.55, 0.59, 0.6, 1)
        _RockColor ("Bare limestone", Color) = (0.72, 0.72, 0.71, 1)
        _Haze ("Haze towards the fog colour", Range(0, 1)) = 0.42
        _FarHaze ("Extra haze on the far layer", Range(0, 1)) = 0.18
        _Shade ("Sun modelling", Range(0, 1)) = 0.5
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry+10" "RenderPipeline" = "UniversalPipeline" }
        Pass
        {
            Name "Forward"
            Tags { "LightMode" = "UniversalForward" }
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _LowColor, _HighColor, _RockColor;
                half _Haze, _FarHaze, _Shade;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; half4 color : COLOR; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 normalWS : TEXCOORD0; half4 color : TEXCOORD1; };

            Varyings vert(Attributes v)
            {
                Varyings o;
                o.positionCS = TransformObjectToHClip(v.positionOS.xyz);
                o.normalWS = TransformObjectToWorldNormal(v.normalOS);
                o.color = v.color;
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                half3 c = lerp(_LowColor.rgb, _HighColor.rgb, i.color.r);
                c = lerp(c, _RockColor.rgb, i.color.g);
                Light sun = GetMainLight();
                half ndl = saturate(dot(normalize(i.normalWS), sun.direction) * 0.5 + 0.5);
                half3 tint = sun.color / max(max(sun.color.r, max(sun.color.g, sun.color.b)), 1e-3);
                c *= lerp(1.0, lerp(0.68, 1.12, ndl), _Shade) * lerp(half3(1, 1, 1), tint, 0.35);
                half haze = saturate(_Haze + i.color.b * _FarHaze) * lerp(1.0, 0.82, i.color.r);
                c = lerp(c, unity_FogColor.rgb, haze);
                return half4(c, 1);
            }
            ENDHLSL
        }
    }
}
