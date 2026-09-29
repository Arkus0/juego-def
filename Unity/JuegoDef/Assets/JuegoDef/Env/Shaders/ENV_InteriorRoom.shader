// Fake interior behind a window (interior mapping, after van Dongen 2008): the card sits just behind the glass and
// the shader traces the view ray into a virtual room box, then samples a cubemap captured from the centre of a real
// room of the same size (JuegoDef > ENV > 8 Build Interior Rooms). Object space is metric: the card's origin is the
// room floor at the middle of the window wall, +z points out to the street, the room spans x [-W/2, W/2], y [0, H],
// z [-D, 0]. A negative x scale mirrors the room. Brightness comes from globals set by the lighting rig
// (JDLightingRig): dim rooms by day, a hashed share of lit rooms at dusk and night (bars add _LitBias).
// Without a rig in the scene the material's _Brightness applies.
Shader "JuegoDef/ENV/Interior Room"
{
    Properties
    {
        [NoScaleOffset] _RoomCube ("Room cubemap", Cube) = "grey" {}
        _RoomSize ("Room size W H D (m)", Vector) = (3.6, 2.8, 4.2, 0)
        _Tint ("Tint", Color) = (1, 1, 1, 1)
        _Brightness ("Brightness without a rig", Float) = 0.45
        _LitBias ("Lit share bias (bars +1)", Float) = 0
        _Opening ("Opening y0, y1, half width (m, object space)", Vector) = (0.95, 2.5, 0.62, 0)
        _Reflect ("Base reflection", Range(0, 1)) = 0.12
        _Blinds ("Share of lowered blinds", Range(0, 1)) = 0.45
        _BlindColor ("Blind colour", Color) = (0.82, 0.78, 0.7, 1)
        _Curtains ("Share of net curtains", Range(0, 1)) = 0.4
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            float4 _RoomSize;
            half4 _Tint;
            float _Brightness;
            float _LitBias;
            float4 _Opening;
            half _Reflect;
            half _Blinds;
            half4 _BlindColor;
            half _Curtains;
        CBUFFER_END

        // set by JDLightingRig (0 when no rig: the material brightness applies)
        float _JD_InteriorDim;
        float _JD_InteriorLit;
        float _JD_InteriorLitShare;
        half4 _JD_InteriorTint;

        TEXTURECUBE(_RoomCube);
        SAMPLER(sampler_RoomCube);

        struct Attributes
        {
            float4 positionOS : POSITION;
            float3 normalOS : NORMAL;
            UNITY_VERTEX_INPUT_INSTANCE_ID
        };
        ENDHLSL

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
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionOS : TEXCOORD0;
                float3 cameraOS : TEXCOORD1;
                float fog : TEXCOORD2;
                float shade : TEXCOORD3;
                float lit : TEXCOORD4;
                float3 positionWS : TEXCOORD5;
                float3 normalWS : TEXCOORD6;
                float hash : TEXCOORD7;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings vert(Attributes v)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_TRANSFER_INSTANCE_ID(v, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                float3 ws = TransformObjectToWorld(v.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(ws);
                o.positionOS = v.positionOS.xyz;
                o.positionWS = ws;
                o.normalWS = TransformObjectToWorldNormal(float3(0, 0, 1));   // the window wall faces +z
                o.cameraOS = TransformWorldToObject(GetCameraPositionWS());
                o.fog = ComputeFogFactor(o.positionCS.z);
                // one stable random value per window (its world origin): some rooms brighter, some in shadow
                float3 origin = TransformObjectToWorld(float3(0, 0, 0));
                float h = frac(sin(dot(floor(origin.xz * 4.0) + floor(origin.y * 2.0), float2(12.9898, 78.233))) * 43758.5453);
                o.shade = lerp(0.55, 1.2, frac(h * 7.13));
                o.hash = h;
                o.lit = step(h, saturate(_JD_InteriorLitShare + _LitBias));
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                float3 d = normalize(i.positionOS - i.cameraOS);
                d = sign(d) * max(abs(d), 1e-4);                     // no exact zero components (grazing rays)
                float3 bmin = float3(-0.5 * _RoomSize.x, 0.0, -_RoomSize.z);
                float3 bmax = float3(0.5 * _RoomSize.x, _RoomSize.y, 0.0);
                float3 p = float3(i.positionOS.xy, 0.0);
                float3 inv = 1.0 / d;
                float3 tfar = max((bmin - p) * inv, (bmax - p) * inv);
                float t = min(min(tfar.x, tfar.y), tfar.z);
                float3 hit = p + d * t;
                float3 centre = 0.5 * (bmin + bmax);
                half3 room = SAMPLE_TEXTURECUBE_LOD(_RoomCube, sampler_RoomCube, hit - centre, 0).rgb;
                half rigged = step(1e-4, _JD_InteriorLit + _JD_InteriorDim);
                half k = rigged > 0 ? lerp(_JD_InteriorDim, _JD_InteriorLit, i.lit) * lerp(1.0, i.shade, 0.5) : _Brightness * i.shade;
                half3 tint = rigged > 0 ? _JD_InteriorTint.rgb : half3(1, 1, 1);
                half3 col = room * _Tint.rgb * tint * k;

                // what hangs right behind the glass: net curtains (side panels or full), a roller blind lowered to some
                // height — lived-in windows, each different (owner audit: "persianas a diferentes alturas, cortinas")
                float y0 = _Opening.x, y1 = _Opening.y, hw = max(_Opening.z, 0.1);
                float2 q = i.positionOS.xy;
                float hb = frac(i.hash * 3.71), hc = frac(i.hash * 5.13), hl = frac(i.hash * 11.3);
                if (hc < _Curtains)
                {
                    bool full = frac(i.hash * 17.9) < 0.35;
                    float side = hw * lerp(0.28, 0.45, frac(i.hash * 23.1));
                    float ax = abs(q.x);
                    half cover = full ? 1.0 : smoothstep(hw - side - 0.02, hw - side, ax);
                    half folds = 0.8 + 0.2 * sin(q.x * 38.0 + i.hash * 20.0);
                    half lace = 0.75 + 0.25 * step(0.5, frac(q.x * 22.0) + frac(q.y * 22.0) * 0.5);
                    half3 net = half3(0.86, 0.85, 0.8) * folds * lace * (0.45 + 0.55 * k);
                    col = lerp(col, net, cover * (full ? 0.55 : 0.8) * step(y0, q.y));
                }
                if (hb < _Blinds)
                {
                    float level = y1 - lerp(0.12, 0.92, hl) * (y1 - y0);
                    if (q.y > level)
                    {
                        half slat = 0.86 + 0.14 * smoothstep(0.35, 0.5, frac((y1 - q.y) * 22.0));
                        half3 blind = _BlindColor.rgb * lerp(0.85, 1.1, frac(i.hash * 29.3)) * slat * 0.62;
                        col = blind;
                    }
                }
                // controlled reflection: sky / probe with Fresnel, never a mirror
                float3 nW = normalize(i.normalWS);
                float3 vW = GetWorldSpaceNormalizeViewDir(i.positionWS);
                half fres = 0.04 + 0.96 * pow(1.0 - saturate(dot(nW, vW)), 5.0);
                half3 env = GlossyEnvironmentReflection(reflect(-vW, nW), 0.06, 1.0);
                col = lerp(col, env, saturate(max(fres, _Reflect)) * 0.85);
                col = MixFog(col, i.fog);
                return half4(col, 1.0);
            }
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
            #pragma vertex vertDepth
            #pragma fragment fragDepth
            #pragma multi_compile_instancing
            #pragma multi_compile _ DOTS_INSTANCING_ON

            struct VaryingsDepth
            {
                float4 positionCS : SV_POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            VaryingsDepth vertDepth(Attributes v)
            {
                VaryingsDepth o = (VaryingsDepth)0;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_TRANSFER_INSTANCE_ID(v, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionCS = TransformObjectToHClip(v.positionOS.xyz);
                return o;
            }

            half fragDepth(VaryingsDepth i) : SV_Target { return i.positionCS.z; }
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex vertNormals
            #pragma fragment fragNormals
            #pragma multi_compile_instancing
            #pragma multi_compile _ DOTS_INSTANCING_ON

            struct VaryingsNormals
            {
                float4 positionCS : SV_POSITION;
                float3 normalWS : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            VaryingsNormals vertNormals(Attributes v)
            {
                VaryingsNormals o = (VaryingsNormals)0;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_TRANSFER_INSTANCE_ID(v, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionCS = TransformObjectToHClip(v.positionOS.xyz);
                o.normalWS = TransformObjectToWorldNormal(v.normalOS);
                return o;
            }

            half4 fragNormals(VaryingsNormals i) : SV_Target { return half4(normalize(i.normalWS), 0.0); }
            ENDHLSL
        }
    }
}
