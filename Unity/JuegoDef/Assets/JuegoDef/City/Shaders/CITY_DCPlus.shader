// "Dreamcast+" surface for the town (Docs/design/CITY_STYLE_DCPLUS.md; owner 2026-10-02: "que deje de parecer assets
// mejorados y parezca un juego de Dreamcast con nivel gráfico top"). The detail lives in the painted texture (relief,
// cavities and soft light baked into the albedo by Tools/city_ivanix/tools/dc_textures.py); the shader keeps the
// lighting simple and legible:
//   wrapped Lambert  - light wraps round the form, no harsh terminator;
//   painted shade    - where the sun does not reach, a cool tint multiplies the ambient (as a painter would);
//   ambient          - spherical harmonics from the scene's trilight, scaled;
//   gloss            - an optional, small Blinn highlight (glass, painted metal, wet stone);
//   emission         - signs and lamps;
//   alpha clip       - card foliage.
// No normal, roughness or occlusion maps on purpose. Realtime sun shadows and Unity fog stay.
Shader "JuegoDef/City/DC Plus"
{
    Properties
    {
        _BaseMap ("Albedo (painted)", 2D) = "white" {}
        _BaseColor ("Tint", Color) = (1, 1, 1, 1)
        _ShadeColor ("Painted shade tint", Color) = (0.70, 0.76, 0.90, 1)
        _Wrap ("Light wrap", Range(0, 1)) = 0.35
        _AmbientScale ("Ambient", Range(0, 2)) = 1.0
        _SunScale ("Sun", Range(0, 2)) = 1.0
        _SpecAmount ("Gloss amount", Range(0, 1)) = 0
        _Gloss ("Gloss sharpness", Range(2, 256)) = 32
        _MipBias ("Texture softness (mip bias)", Range(-1, 2)) = 0.3
        _WorldUV ("World-space UVs (kit masonry and render continue across modules)", Float) = 0
        [NoScaleOffset] _NoiseMap ("Macro noise", 2D) = "grey" {}
        _MacroScale ("Macro tone frequency (1/m)", Float) = 0.06
        _MacroAmount ("Macro tone variation", Range(0, 1)) = 0.1
        [NoScaleOffset] _EmissionMap ("Emission", 2D) = "white" {}
        [HDR] _EmissionColor ("Emission colour", Color) = (0, 0, 0, 0)
        [Toggle(_ALPHATEST_ON)] _AlphaClip ("Alpha clip (cards)", Float) = 0
        _Cutoff ("Alpha cutoff", Range(0, 1)) = 0.5
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
            half4 _ShadeColor;
            half _Wrap;
            half _AmbientScale;
            half _SunScale;
            half _SpecAmount;
            half _Gloss;
            half _MipBias;
            half _WorldUV;
            float _MacroScale;
            half _MacroAmount;
            half4 _EmissionColor;
            half _Cutoff;
        CBUFFER_END

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
            #pragma shader_feature_local _ALPHATEST_ON

            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Fog.hlsl"
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            // _EmissionMap / sampler_EmissionMap come from SurfaceInput.hlsl
            TEXTURE2D(_NoiseMap); SAMPLER(sampler_NoiseMap);

            // metres on the surface, oriented like the kit's own UVs (same mapping as ENV Weathered Lit)
            float2 WorldUV(float3 pw, float3 nw)
            {
                if (abs(nw.y) > 0.7) return pw.xz;
                float2 u = normalize(float2(nw.z, -nw.x) + 1e-5);
                return float2(dot(pw.xz, u), pw.y);
            }

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                float3 normalWS : TEXCOORD2;
                float fog : TEXCOORD3;
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
                o.uv = TRANSFORM_TEX(v.uv, _BaseMap);
                o.fog = ComputeFogFactor(p.positionCS.z);
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                float3 N = normalize(i.normalWS);
                float2 uv = _WorldUV > 0.5 ? WorldUV(i.positionWS, N) * 0.5 * _BaseMap_ST.xy + _BaseMap_ST.zw : i.uv;
                half4 albedo = SAMPLE_TEXTURE2D_BIAS(_BaseMap, sampler_BaseMap, uv, _MipBias) * _BaseColor;
                #if defined(_ALPHATEST_ON)
                    clip(albedo.a - _Cutoff);
                #endif
                // painted variety: a slow tone drift in world space, so no two walls or stretches of paving match
                float2 sc = abs(N.y) > 0.7 ? i.positionWS.xz : float2(i.positionWS.x + i.positionWS.z, i.positionWS.y);
                half macro = SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, sc * _MacroScale).r;
                albedo.rgb *= 1.0 + (macro - 0.5) * 2.0 * _MacroAmount;
                float3 V = GetWorldSpaceNormalizeViewDir(i.positionWS);

                float4 shadowCoord = TransformWorldToShadowCoord(i.positionWS);
                Light sun = GetMainLight(shadowCoord);
                half ndl = dot(N, sun.direction);
                half lit = saturate((ndl + _Wrap) / (1.0 + _Wrap)) * sun.shadowAttenuation;
                half3 ambient = SampleSH(N) * _AmbientScale;
                half3 shade = lerp(_ShadeColor.rgb, half3(1, 1, 1), lit);
                half3 col = albedo.rgb * (ambient * shade + sun.color * lit * _SunScale);

                // a small, painted highlight only where asked for (glass, painted iron, wet stone)
                float3 H = normalize(sun.direction + V);
                col += sun.color * lit * _SpecAmount * pow(saturate(dot(N, H)), _Gloss);

                #if defined(_ADDITIONAL_LIGHTS)
                    InputData inputData = (InputData)0;
                    inputData.positionWS = i.positionWS;
                    inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
                    uint pixelLightCount = GetAdditionalLightsCount();
                    LIGHT_LOOP_BEGIN(pixelLightCount)
                        Light lamp = GetAdditionalLight(lightIndex, i.positionWS);
                        half wl = saturate((dot(N, lamp.direction) + _Wrap) / (1.0 + _Wrap));
                        col += albedo.rgb * lamp.color * lamp.distanceAttenuation * wl;
                    LIGHT_LOOP_END
                #endif

                col += SAMPLE_TEXTURE2D(_EmissionMap, sampler_EmissionMap, i.uv).rgb * _EmissionColor.rgb;
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
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex ShadowPassVertex
            #pragma fragment ShadowPassFragment
            #pragma shader_feature_local _ALPHATEST_ON
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
            #pragma shader_feature_local _ALPHATEST_ON
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
            #pragma shader_feature_local _ALPHATEST_ON
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthNormalsPass.hlsl"
            ENDHLSL
        }
    }
    FallBack Off
}
