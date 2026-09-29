// Localized weathering decal (owner audit 2026-09-29: "humedad bajo bajantes, reparaciones, desgaste de zócalos,
// manchas en esquinas"). A thin quad laid on a wall by the facade dresser where the cause is: a downpipe splashes,
// a sill drips, an iron balcony rusts, an extractor soots, a corner catches the rain, a patch was repaired.
// Blend is 2x multiply (result = wall * 2 * stain): the texture is authored around mid grey, darker = stain,
// lighter = fresh repair render, tinted = algae / rust. Fog fades it to neutral so distant stains do not glow.
Shader "JuegoDef/ENV/Stain"
{
    Properties
    {
        _BaseMap ("Stain atlas (RGB around 0.5, A mask)", 2D) = "grey" {}
        _Strength ("Strength", Range(0, 1.5)) = 1
    }
    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Geometry+450" "RenderPipeline" = "UniversalPipeline" "IgnoreProjector" = "True" }
        Blend DstColor SrcColor
        ZWrite Off
        Cull Off
        Offset -1, -1

        Pass
        {
            Name "Forward"
            Tags { "LightMode" = "UniversalForward" }
            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_fog
            #pragma multi_compile_instancing
            #pragma multi_compile _ DOTS_INSTANCING_ON
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half _Strength;
            CBUFFER_END
            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);

            struct Attributes { float4 positionOS : POSITION; float2 uv : TEXCOORD0; UNITY_VERTEX_INPUT_INSTANCE_ID };
            struct Varyings { float4 positionCS : SV_POSITION; float2 uv : TEXCOORD0; float fog : TEXCOORD1; UNITY_VERTEX_INPUT_INSTANCE_ID UNITY_VERTEX_OUTPUT_STEREO };

            Varyings vert(Attributes v)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_TRANSFER_INSTANCE_ID(v, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionCS = TransformObjectToHClip(v.positionOS.xyz);
                o.uv = TRANSFORM_TEX(v.uv, _BaseMap);
                o.fog = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                half4 t = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv);
                half3 c = lerp(half3(0.5, 0.5, 0.5), t.rgb, saturate(t.a * _Strength));
                c = MixFogColor(c, half3(0.5, 0.5, 0.5), i.fog);
                return half4(c, 1);
            }
            ENDHLSL
        }
    }
}
