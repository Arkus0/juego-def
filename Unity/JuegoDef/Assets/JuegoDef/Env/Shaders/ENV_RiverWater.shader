// River water for the casco channel (owner audit 2026-09-29: "el agua parece una superficie azul/gris plana; falta
// profundidad visual, reflejo, corriente suave, variación, contacto con bordes"). Stylised, not photoreal:
//   depth   - colour and opacity from the water column over the bed (camera depth texture): clear green-brown in the
//             shallows where the stones show, dark bottle green in the pools;
//   flow    - two normal layers scrolling downstream (_FlowDir) at different speeds and scales;
//   light   - sun glint and sky/probe reflection with Fresnel (the town reflected when the probe is baked);
//   contact - foam lines where the water meets walls, rocks and the bed (depth under _FoamDepth), broken by noise.
Shader "JuegoDef/ENV/River Water"
{
    Properties
    {
        _ShallowColor ("Shallow", Color) = (0.36, 0.42, 0.33, 1)
        _DeepColor ("Deep", Color) = (0.07, 0.15, 0.14, 1)
        _DepthRange ("Depth to deep colour (m)", Float) = 1.2
        _Clarity ("Shallow transparency", Range(0, 1)) = 0.55
        [Normal][NoScaleOffset] _NormalMap ("Ripple normal", 2D) = "bump" {}
        _NormalScale ("Ripple strength", Float) = 0.55
        _RippleScale ("Ripple scale (1/m)", Float) = 0.35
        _FlowDir ("Flow direction (x, z) and speed (m/s)", Vector) = (0.7, 0.7, 0.35, 0)
        [NoScaleOffset] _NoiseMap ("Foam noise", 2D) = "grey" {}
        _FoamColor ("Foam", Color) = (0.86, 0.88, 0.84, 1)
        _FoamDepth ("Foam depth (m)", Float) = 0.28
        _Reflect ("Base reflection", Range(0, 1)) = 0.12
        _Gloss ("Sun glint sharpness", Float) = 180
    }
    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Transparent-50" "RenderPipeline" = "UniversalPipeline" }
        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        Cull Back

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
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _ShallowColor, _DeepColor, _FoamColor;
                float _DepthRange, _Clarity, _NormalScale, _RippleScale, _FoamDepth, _Reflect, _Gloss;
                float4 _FlowDir;
            CBUFFER_END
            TEXTURE2D(_NormalMap); SAMPLER(sampler_NormalMap);
            TEXTURE2D(_NoiseMap); SAMPLER(sampler_NoiseMap);

            struct Attributes { float4 positionOS : POSITION; UNITY_VERTEX_INPUT_INSTANCE_ID };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float4 screen : TEXCOORD1;
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
                o.screen = ComputeScreenPos(p.positionCS);
                o.fog = ComputeFogFactor(p.positionCS.z);
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                float2 suv = i.screen.xy / i.screen.w;
                float sceneZ = LinearEyeDepth(SampleSceneDepth(suv), _ZBufferParams);
                float waterZ = LinearEyeDepth(i.positionCS.z, _ZBufferParams);
                float column = max(0, sceneZ - waterZ);

                float2 flow = normalize(_FlowDir.xy + 1e-4) * _FlowDir.z;
                float2 w = i.positionWS.xz * _RippleScale;
                float t = _Time.y;
                half3 n1 = UnpackNormalScale(SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, w + flow * t * 0.35), _NormalScale);
                half3 n2 = UnpackNormalScale(SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, w * 2.3 + flow * t * 0.6 + 0.37), _NormalScale * 0.6);
                half3 nt = normalize(half3(n1.xy + n2.xy, n1.z * n2.z));
                float3 nW = normalize(float3(nt.x, nt.z, nt.y));

                float deep = saturate(column / _DepthRange);
                half3 body = lerp(_ShallowColor.rgb, _DeepColor.rgb, deep);
                half alpha = lerp(1.0 - _Clarity, 1.0, saturate(deep * 1.4));

                // light: diffuse-ish body tinted by the sun and ambient, glint, Fresnel reflection
                Light sun = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                float3 V = GetWorldSpaceNormalizeViewDir(i.positionWS);
                half ndl = saturate(dot(nW, sun.direction));
                half3 amb = SampleSH(nW);
                body *= amb + sun.color * (0.35 + 0.4 * ndl) * sun.shadowAttenuation;
                float3 H = normalize(sun.direction + V);
                half glint = pow(saturate(dot(nW, H)), _Gloss) * sun.shadowAttenuation;
                half fres = 0.02 + 0.98 * pow(1.0 - saturate(dot(nW, V)), 5.0);
                half3 env = GlossyEnvironmentReflection(reflect(-V, nW), 0.04, 1.0);
                // reflections stay under the water's own colour: a river in a stone channel, not a mirror of blue sky
                half3 col = lerp(body, env * lerp(half3(1, 1, 1), _ShallowColor.rgb * 1.6, 0.35), saturate(max(fres, _Reflect)) * 0.55);
                col += sun.color * glint * 2.5;
                alpha = saturate(alpha + fres * 0.5 + glint);

                // contact foam: thin broken lines where the column is shallow (walls, rocks, bed edges)
                half fn = SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, i.positionWS.xz * 0.9 + flow * t * 0.4).a;
                half edge = 1.0 - saturate(column / _FoamDepth);
                half foam = saturate((edge * 1.25 - (1.0 - fn) * 0.9) * 3.0) * step(0.001, column);
                col = lerp(col, _FoamColor.rgb * (amb + sun.color * 0.6), foam * 0.85);
                alpha = max(alpha, foam * 0.9);

                col = MixFog(col, i.fog);
                return half4(col, alpha);
            }
            ENDHLSL
        }
    }
}
