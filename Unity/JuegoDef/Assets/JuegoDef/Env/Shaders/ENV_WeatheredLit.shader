// Weathered lit surface for the ENV factory (owner audit 2026-09-29: "la piedra es demasiado uniforme", "el revoco
// resulta plano", "falta humedad ambiental", "la escena es demasiado limpia"). Physically based URP lighting over the
// kit's painted textures, plus cheap weathering that never repeats with the 2 m kit tiling:
//   macro tone  - world-space low-frequency tone/hue drift (no two walls, no two stretches of paving alike);
//   damp        - rising damp at the foot of walls (object y = storey floor) or above the river water line (world);
//   streaks     - rain streaks on vertical faces;
//   moss        - on up-facing faces and in the damp band, only where the material allows it;
//   patches     - rectangular repairs/repaints (object space + a per-object seed);
//   flaking     - render fallen off, the material behind showing (neglected fronts).
// Everything is per material (no per-renderer data), so it stays SRP-batcher / GPU-Resident-Drawer friendly.
// The noise texture channels (Tools/env_textures.py, T_ENV_Weather_Noise): R low fbm, G mid fbm, B vertical streaks,
// A soft blotches. The river water level comes from the global _JD_WaterLevel (set by the district builder).
Shader "JuegoDef/ENV/Weathered Lit"
{
    Properties
    {
        _BaseMap ("Albedo", 2D) = "white" {}
        _BaseColor ("Colour", Color) = (1, 1, 1, 1)
        [Normal] _BumpMap ("Normal", 2D) = "bump" {}
        _BumpScale ("Normal scale", Float) = 1
        [NoScaleOffset] _RoughMap ("Roughness", 2D) = "white" {}
        _RoughChannel ("Roughness channel mask", Vector) = (1, 0, 0, 0)
        _Roughness ("Roughness multiplier", Float) = 1
        _Metallic ("Metallic", Float) = 0
        [NoScaleOffset] _NoiseMap ("Weathering noise (RGBA, linear)", 2D) = "grey" {}
        _MacroScale ("Macro noise frequency (1/m)", Float) = 0.08
        _MacroAmount ("Macro tone variation", Range(0, 1)) = 0.12
        _MacroHue ("Macro hue drift colour", Color) = (1, 0.94, 0.84, 1)
        _DetailTone ("Stone-scale tone variation", Range(0, 0.5)) = 0.08
        _Seed ("Material seed (offsets every noise lookup)", Float) = 0
        _DampHeight ("Rising damp height (m)", Float) = 0
        _DampAmount ("Rising damp darkening", Range(0, 1)) = 0
        _DampWorld ("Damp from the river water level (0 object y, 1 world)", Float) = 0
        _StreakAmount ("Rain streaks", Range(0, 1)) = 0
        _MossAmount ("Moss", Range(0, 1)) = 0
        _MossColor ("Moss colour", Color) = (0.32, 0.37, 0.2, 1)
        _PatchAmount ("Repair patches (share of cells)", Range(0, 1)) = 0
        _PatchTint ("Patch tint", Color) = (1.07, 1.05, 1.01, 1)
        _FlakeAmount ("Flaking render (share)", Range(0, 1)) = 0
        [NoScaleOffset] _FlakeMap ("Material behind the render", 2D) = "grey" {}
        _FlakeColor ("Revealed tint", Color) = (1, 1, 1, 1)
        _Cutoff ("Alpha cutoff (unused)", Float) = 0.5
        [Enum(UnityEngine.Rendering.CullMode)] _Cull ("Cull", Float) = 2
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" "UniversalMaterialType" = "Lit" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half _BumpScale;
            half4 _RoughChannel;
            half _Roughness;
            half _Metallic;
            float _MacroScale;
            half _MacroAmount;
            half4 _MacroHue;
            half _DetailTone;
            float _Seed;
            float _DampHeight;
            half _DampAmount;
            half _DampWorld;
            half _StreakAmount;
            half _MossAmount;
            half4 _MossColor;
            half _PatchAmount;
            half4 _PatchTint;
            half _FlakeAmount;
            half4 _FlakeColor;
            half _Cutoff;
        CBUFFER_END

        float _JD_WaterLevel;

        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/SurfaceInput.hlsl"
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex vert
            #pragma fragment frag

            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_ATLAS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile_fragment _ _LIGHT_COOKIES
            #pragma multi_compile _ _LIGHT_LAYERS
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Fog.hlsl"
            #pragma multi_compile_instancing
            #pragma instancing_options renderinglayer
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_RoughMap);   SAMPLER(sampler_RoughMap);
            TEXTURE2D(_NoiseMap);   SAMPLER(sampler_NoiseMap);
            TEXTURE2D(_FlakeMap);   SAMPLER(sampler_FlakeMap);

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float4 tangentOS : TANGENT;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                float3 normalWS : TEXCOORD2;
                float4 tangentWS : TEXCOORD3;
                float3 positionOS : TEXCOORD4;
                float4 seedFog : TEXCOORD5;   // xyz object origin (world), w fog factor
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
                VertexNormalInputs n = GetVertexNormalInputs(v.normalOS, v.tangentOS);
                o.positionCS = p.positionCS;
                o.positionWS = p.positionWS;
                o.normalWS = n.normalWS;
                o.tangentWS = float4(n.tangentWS, v.tangentOS.w * GetOddNegativeScale());
                o.positionOS = v.positionOS.xyz;
                o.uv = TRANSFORM_TEX(v.uv, _BaseMap);
                o.seedFog = float4(TransformObjectToWorld(float3(0, 0, 0)), ComputeFogFactor(p.positionCS.z));
                return o;
            }

            float Hash21(float2 p)
            {
                p = frac(p * float2(123.34, 456.21));
                p += dot(p, p + 45.32);
                return frac(p.x * p.y);
            }

            // 2D coordinates on the surface in metres: walls use (along, up), floors use (x, z)
            float2 SurfaceCoords(float3 pw, float3 nw)
            {
                float3 an = abs(nw);
                if (an.y > 0.7) return pw.xz;
                return an.x > an.z ? float2(pw.z, pw.y) : float2(pw.x, pw.y);
            }

            half4 N(float2 c) { return SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, c); }

            half4 frag(Varyings i) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                half4 albedo = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv) * _BaseColor;
                half3 nTS = UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, i.uv), _BumpScale);
                half rough = saturate(dot(SAMPLE_TEXTURE2D(_RoughMap, sampler_RoughMap, i.uv), _RoughChannel) * _Roughness);

                float3 nGeo = normalize(i.normalWS);
                // every material of a family has its own seed: the same weathering never lines up on two buildings
                float2 sc = SurfaceCoords(i.positionWS, nGeo) + _Seed * float2(17.31, 7.97);
                float seed = Hash21(i.seedFog.xz * 0.37 + i.seedFog.y + _Seed);
                half vertical = 1.0 - saturate(abs(nGeo.y) * 1.6);

                // macro tone and hue drift
                half4 nm = N(sc * _MacroScale + seed * 0.0);
                half tone = 1.0 + (nm.r - 0.5) * 2.0 * _MacroAmount;
                // stone-scale tone: breaks the 2-4 m repeat of the masonry and paving textures (owner: "la piedra se
                // repite con demasiada regularidad")
                tone *= 1.0 + (N(sc * 1.9 + 0.31).g - 0.5) * 2.0 * _DetailTone;
                albedo.rgb *= tone * lerp(half3(1, 1, 1), _MacroHue.rgb, saturate(nm.g * 1.4 - 0.2) * _MacroAmount * 3.0);

                // repair patches: rectangular cells in the object's own frame, drawn per object
                if (_PatchAmount > 0)
                {
                    float2 pc = floor(float2(i.positionOS.x / 0.95 + seed * 7.0, i.positionOS.y / 0.62));
                    float h = Hash21(pc + seed * 31.0);
                    if (h < _PatchAmount) albedo.rgb *= lerp(_PatchTint.rgb, half3(1, 1, 1), frac(h * 17.0) * 0.5);
                }

                // flaking render: soft blotches, likelier near the foot of the wall
                half flake = 0;
                if (_FlakeAmount > 0)
                {
                    // low-frequency blotches (patches 0.2-1.2 m), not speckle; a little broken up by the mid noise
                    half b = N(sc * 0.17 + seed * 3.1).a * 0.85 + N(sc * 0.6 + seed).g * 0.15;
                    half bias = saturate(1.0 - i.positionOS.y / 2.2) * 0.2;
                    half thr = 1.0 - _FlakeAmount * 1.4 - bias;
                    flake = smoothstep(thr, thr + 0.015, b) * vertical;
                    half rim = smoothstep(thr - 0.02, thr, b) * (1 - flake) * vertical;
                    half3 behind = SAMPLE_TEXTURE2D(_FlakeMap, sampler_FlakeMap, i.uv * 1.3).rgb * _FlakeColor.rgb;
                    albedo.rgb = lerp(albedo.rgb * (1.0 - 0.35 * rim), behind, flake);
                    rough = lerp(rough, 0.95, flake);
                }

                // rising damp / river water line
                half damp = 0;
                if (_DampAmount > 0)
                {
                    float h = _DampWorld > 0.5 ? i.positionWS.y - _JD_WaterLevel : i.positionOS.y;
                    half edge = N(sc * 0.45 + seed).g;
                    float top = _DampHeight * (0.55 + 0.9 * edge);
                    damp = saturate((top - h) / max(0.25 * top, 0.05)) * vertical;
                    albedo.rgb = lerp(albedo.rgb, albedo.rgb * half3(0.6, 0.62, 0.6), damp * _DampAmount);
                    rough = lerp(rough, rough * 0.72, damp * _DampAmount);
                    if (_DampWorld > 0.5)
                    {
                        // dark algae band just above the water, a pale tide mark above it
                        half band = exp(-pow((h - 0.28) / 0.22, 2.0));
                        albedo.rgb = lerp(albedo.rgb, half3(0.16, 0.19, 0.12), band * 0.75 * vertical);
                        half mark = exp(-pow((h - 0.95 - edge * 0.3) / 0.08, 2.0));
                        albedo.rgb *= 1.0 + mark * 0.12 * vertical;
                    }
                }

                // rain streaks on vertical faces
                if (_StreakAmount > 0)
                {
                    half s = N(float2(sc.x * 0.9 + seed, sc.y * 0.07)).b;
                    half streak = saturate((s - 0.52) * 3.2) * _StreakAmount * vertical;
                    albedo.rgb *= 1.0 - 0.38 * streak;
                }

                // moss: up-facing faces and the damp band, patchy
                if (_MossAmount > 0)
                {
                    half up = saturate((nGeo.y - 0.3) / 0.45);
                    half m = N(sc * 0.6 + seed * 5.0).a;
                    half k = saturate((m * 0.9 + up * 0.55 + damp * 0.45 - 1.25 + _MossAmount) * 5.0) * (1 - flake);
                    albedo.rgb = lerp(albedo.rgb, _MossColor.rgb * (0.75 + 0.5 * nm.g), k);
                    rough = lerp(rough, 1.0, k);
                }

                // lighting
                float3 bitangent = i.tangentWS.w * cross(i.normalWS, i.tangentWS.xyz);
                half3x3 tbn = half3x3(i.tangentWS.xyz, bitangent, i.normalWS);
                InputData inputData = (InputData)0;
                inputData.positionWS = i.positionWS;
                inputData.positionCS = i.positionCS;
                inputData.normalWS = NormalizeNormalPerPixel(TransformTangentToWorld(nTS, tbn));
                inputData.viewDirectionWS = GetWorldSpaceNormalizeViewDir(i.positionWS);
                inputData.shadowCoord = TransformWorldToShadowCoord(i.positionWS);
                inputData.fogCoord = i.seedFog.w;
                inputData.bakedGI = SampleSH(inputData.normalWS);
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
                inputData.shadowMask = half4(1, 1, 1, 1);

                SurfaceData surface = (SurfaceData)0;
                surface.albedo = albedo.rgb;
                surface.alpha = 1;
                surface.metallic = _Metallic;
                surface.smoothness = 1.0 - rough;
                surface.normalTS = nTS;
                surface.occlusion = 1;
                surface.specular = half3(0, 0, 0);
                half4 color = UniversalFragmentPBR(inputData, surface);
                color.rgb = MixFog(color.rgb, inputData.fogCoord);
                return half4(color.rgb, 1);
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
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex ShadowPassVertex
            #pragma fragment ShadowPassFragment
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
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
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex DepthOnlyVertex
            #pragma fragment DepthOnlyFragment
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthOnlyPass.hlsl"
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex DepthNormalsVertex
            #pragma fragment DepthNormalsFragment
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthNormalsPass.hlsl"
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
