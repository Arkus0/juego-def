// "Dreamcast+" ground for the town: one surface, the paving decided by a class map laid out as a worker would lay it
// (Tools/city_ivanix/tools/paving_map.py, 12.5 cm per texel). Owner review 2026-10-02: the cuts between pavings were
// straight lines; "un obrero no lo haria perfecto".
//   - the map is read through a warped lookup (two octaves of noise), so every change of paving wanders by hand;
//   - where two pavings meet, a granite band (cinta) is laid along the joint, its width varying a little;
//   - each class keeps its own painted texture, tiling and tint (taken from the DC material it had before);
//   - lighting as DC Plus: wrapped Lambert, painted cool shade, SH ambient, a small wet gloss, fog and sun shadows.
// Class ids (paving_map.py): 0 canto, 1 canto viejo, 2 huerta, 3 suelo, 4 roca, 5 prado, 6 losa, 7 adoquin, 8 muelle,
// 9 patio, 10 camino, 11 abanico, 12 granito.
Shader "JuegoDef/City/DC Ground"
{
    Properties
    {
        [NoScaleOffset] _ClassMap ("Paving class map (R8, point)", 2D) = "black" {}
        _MapOrigin ("Map origin (x, z) and texel (m)", Vector) = (0, 0, 0.125, 0)
        _MapSize ("Map size in texels (w, h)", Vector) = (1, 1, 0, 0)
        _WarpAmp ("Hand wander (m)", Range(0, 1)) = 0.32
        _WarpFine ("Hand tremor (m)", Range(0, 0.3)) = 0.07
        _WarpFreq ("Wander frequency (1/m)", Float) = 0.17
        _Band ("Granite band half width (m)", Range(0, 0.5)) = 0.17

        [NoScaleOffset] _T0 ("Canto", 2D) = "grey" {}       _ST0 ("Canto tiling", Vector) = (1, 1, 0, 0)       _C0 ("Canto tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T1 ("Canto viejo", 2D) = "grey" {} _ST1 ("tiling", Vector) = (1, 1, 0, 0)             _C1 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T2 ("Huerta", 2D) = "grey" {}      _ST2 ("tiling", Vector) = (1, 1, 0, 0)             _C2 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T3 ("Suelo", 2D) = "grey" {}       _ST3 ("tiling", Vector) = (1, 1, 0, 0)             _C3 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T4 ("Roca", 2D) = "grey" {}        _ST4 ("tiling", Vector) = (1, 1, 0, 0)             _C4 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T5 ("Prado", 2D) = "grey" {}       _ST5 ("tiling", Vector) = (1, 1, 0, 0)             _C5 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T6 ("Losa", 2D) = "grey" {}        _ST6 ("tiling", Vector) = (1, 1, 0, 0)             _C6 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T7 ("Adoquin", 2D) = "grey" {}     _ST7 ("tiling", Vector) = (1, 1, 0, 0)             _C7 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T8 ("Muelle", 2D) = "grey" {}      _ST8 ("tiling", Vector) = (1, 1, 0, 0)             _C8 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T9 ("Patio", 2D) = "grey" {}       _ST9 ("tiling", Vector) = (1, 1, 0, 0)             _C9 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T10 ("Camino", 2D) = "grey" {}     _ST10 ("tiling", Vector) = (1, 1, 0, 0)            _C10 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T11 ("Abanico", 2D) = "grey" {}    _ST11 ("tiling", Vector) = (1, 1, 0, 0)            _C11 ("tint", Color) = (1, 1, 1, 1)
        [NoScaleOffset] _T12 ("Granito", 2D) = "grey" {}    _ST12 ("tiling", Vector) = (1, 1, 0, 0)            _C12 ("tint", Color) = (1, 1, 1, 1)

        _ShadeColor ("Painted shade tint", Color) = (0.80, 0.83, 0.92, 1)
        _Wrap ("Light wrap", Range(0, 1)) = 0.35
        _AmbientScale ("Ambient", Range(0, 2)) = 1.08
        _SunScale ("Sun", Range(0, 2)) = 1.0
        _SpecAmount ("Wet gloss on the paving", Range(0, 1)) = 0.1
        _Gloss ("Gloss sharpness", Range(2, 256)) = 18
        _MipBias ("Texture softness (mip bias)", Range(-1, 2)) = 0.3
        [NoScaleOffset] _NoiseMap ("Noise", 2D) = "grey" {}
        _MacroScale ("Macro tone frequency (1/m)", Float) = 0.06
        _MacroAmount ("Macro tone variation", Range(0, 1)) = 0.1

        // kept for the shared URP passes (shadow, depth)
        [HideInInspector] _BaseMap ("Base", 2D) = "white" {}
        [HideInInspector] _BaseColor ("Base colour", Color) = (1, 1, 1, 1)
        [HideInInspector] _Cutoff ("Cutoff", Float) = 0.5
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" "UniversalMaterialType" = "Lit" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half _Cutoff;
            float4 _MapOrigin;
            float4 _MapSize;
            float _WarpAmp, _WarpFine, _WarpFreq, _Band;
            float4 _ST0, _ST1, _ST2, _ST3, _ST4, _ST5, _ST6, _ST7, _ST8, _ST9, _ST10, _ST11, _ST12;
            half4 _C0, _C1, _C2, _C3, _C4, _C5, _C6, _C7, _C8, _C9, _C10, _C11, _C12;
            half4 _ShadeColor;
            half _Wrap, _AmbientScale, _SunScale, _SpecAmount, _Gloss, _MipBias;
            float _MacroScale;
            half _MacroAmount;
        CBUFFER_END

        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/SurfaceInput.hlsl"
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Fog.hlsl"
            #pragma multi_compile_instancing
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_ClassMap);
            TEXTURE2D(_NoiseMap); SAMPLER(sampler_NoiseMap);
            TEXTURE2D(_T0); SAMPLER(sampler_T0);
            TEXTURE2D(_T1); TEXTURE2D(_T2); TEXTURE2D(_T3); TEXTURE2D(_T4); TEXTURE2D(_T5); TEXTURE2D(_T6);
            TEXTURE2D(_T7); TEXTURE2D(_T8); TEXTURE2D(_T9); TEXTURE2D(_T10); TEXTURE2D(_T11); TEXTURE2D(_T12);

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; UNITY_VERTEX_INPUT_INSTANCE_ID };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float fog : TEXCOORD2;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings vert(Attributes v)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_TRANSFER_INSTANCE_ID(v, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                VertexPositionInputs p = GetVertexPositionInputs(v.positionOS.xyz);
                o.positionCS = p.positionCS;
                o.positionWS = p.positionWS;
                o.normalWS = TransformObjectToWorldNormal(v.normalOS);
                o.fog = ComputeFogFactor(p.positionCS.z);
                return o;
            }

            int ClassAt(float2 q)
            {
                float2 t = (q - _MapOrigin.xy) / _MapOrigin.z;
                int2 ij = clamp(int2(floor(t)), int2(0, 0), int2(_MapSize.xy) - 1);
                return (int)round(LOAD_TEXTURE2D(_ClassMap, ij).r * 255.0);
            }

            bool Paved(int c) { return c == 0 || c == 1 || c == 6 || c == 7 || c == 10 || c == 11; }
            // a band is laid where a paving meets another paving or the soft ground; not against the houses (3),
            // the shore rock (4), the granite already there (12) or the edge of the map (255)
            bool Joins(int c, int n) { return n != c && n != 3 && n != 4 && n != 12 && n < 13; }

            bool Band(float2 q, int c, float w)
            {
                return Joins(c, ClassAt(q + float2(w, 0))) || Joins(c, ClassAt(q - float2(w, 0))) ||
                       Joins(c, ClassAt(q + float2(0, w))) || Joins(c, ClassAt(q - float2(0, w)));
            }

            half3 Paving(int c, float2 p)
            {
                #define TAKE(N) case N: return SAMPLE_TEXTURE2D_BIAS(_T##N, sampler_T0, p * 0.5 * _ST##N.xy + _ST##N.zw, _MipBias).rgb * _C##N.rgb;
                switch (c)
                {
                    TAKE(0) TAKE(1) TAKE(2) TAKE(3) TAKE(4) TAKE(5) TAKE(6) TAKE(7) TAKE(8) TAKE(9) TAKE(10) TAKE(11) TAKE(12)
                    default: return SAMPLE_TEXTURE2D_BIAS(_T0, sampler_T0, p * 0.5 * _ST0.xy + _ST0.zw, _MipBias).rgb * _C0.rgb;
                }
                #undef TAKE
            }

            half4 frag(Varyings i) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                float3 N = normalize(i.normalWS);
                float2 p = i.positionWS.xz;

                // the worker's hand: a slow wander and a small tremor on every line of the layout
                float2 w1 = float2(SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, p * _WarpFreq).r,
                                   SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, p * _WarpFreq + 17.31).r) - 0.5;
                float2 w2 = float2(SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, p * _WarpFreq * 5.3 + 3.7).r,
                                   SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, p * _WarpFreq * 5.3 + 41.9).r) - 0.5;
                float2 q = p + w1 * 2.0 * _WarpAmp + w2 * 2.0 * _WarpFine;
                int c = ClassAt(q);

                // the granite band along each joint, its width varying with the same hand; a dark joint at its edges
                float bw = _Band * (0.8 + 0.4 * (w2.x + 0.5));
                bool edge = false;
                if (Paved(c) && Band(q, c, bw))
                {
                    edge = !Band(q, c, bw * 0.62);
                    c = 12;
                }

                half3 albedo = Paving(c, p);
                if (edge) albedo *= 0.66;
                half macro = SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, p * _MacroScale).r;
                albedo *= 1.0 + (macro - 0.5) * 2.0 * _MacroAmount;
                float3 V = GetWorldSpaceNormalizeViewDir(i.positionWS);

                float4 shadowCoord = TransformWorldToShadowCoord(i.positionWS);
                Light sun = GetMainLight(shadowCoord);
                half lit = saturate((dot(N, sun.direction) + _Wrap) / (1.0 + _Wrap)) * sun.shadowAttenuation;
                half3 ambient = SampleSH(N) * _AmbientScale;
                half3 shade = lerp(_ShadeColor.rgb, half3(1, 1, 1), lit);
                half3 col = albedo * (ambient * shade + sun.color * lit * _SunScale);
                half spec = (c == 2 || c == 5 || c == 9) ? 0.0 : _SpecAmount;                 // soft ground does not shine
                float3 H = normalize(sun.direction + V);
                col += sun.color * lit * spec * pow(saturate(dot(N, H)), _Gloss);

                #if defined(_ADDITIONAL_LIGHTS)
                    InputData inputData = (InputData)0;
                    inputData.positionWS = i.positionWS;
                    inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
                    uint pixelLightCount = GetAdditionalLightsCount();
                    LIGHT_LOOP_BEGIN(pixelLightCount)
                        Light lamp = GetAdditionalLight(lightIndex, i.positionWS);
                        half wl = saturate((dot(N, lamp.direction) + _Wrap) / (1.0 + _Wrap));
                        col += albedo * lamp.color * lamp.distanceAttenuation * wl;
                    LIGHT_LOOP_END
                #endif

                col = MixFog(col, i.fog);
                return half4(col, 1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0
            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex ShadowPassVertex
            #pragma fragment ShadowPassFragment
            #pragma multi_compile_instancing
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "Packages/com.unity.render-pipelines.universal/Shaders/ShadowCasterPass.hlsl"
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask R
            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex DepthOnlyVertex
            #pragma fragment DepthOnlyFragment
            #pragma multi_compile_instancing
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthOnlyPass.hlsl"
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On
            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex DepthNormalsVertex
            #pragma fragment DepthNormalsFragment
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthNormalsPass.hlsl"
            ENDHLSL
        }
    }
    FallBack Off
}
