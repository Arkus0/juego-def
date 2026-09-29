// Atlantic sky for the ENV look (owner audit 2026-09-29: "el cielo azul intenso y la niebla gris no terminan de
// casar"). One gradient whose horizon IS the fog colour (the lighting rig writes both from the same preset), a soft
// sun, and drifting fbm clouds lit from the sun side — the damp northern sky with broken cloud instead of a flat
// saturated procedural blue. Sun direction from URP's main light; clouds from the ENV weathering noise.
Shader "JuegoDef/ENV/Sky Atlantic"
{
    Properties
    {
        _ZenithColor ("Zenith", Color) = (0.43, 0.56, 0.69, 1)
        _HorizonColor ("Horizon (= fog colour)", Color) = (0.76, 0.8, 0.82, 1)
        _GroundColor ("Below horizon", Color) = (0.52, 0.53, 0.5, 1)
        _Gradient ("Gradient exponent", Float) = 0.55
        _Haze ("Horizon haze", Range(0, 1)) = 0.55
        _SunColor ("Sun", Color) = (1, 0.93, 0.8, 1)
        _SunSize ("Sun size (rad)", Float) = 0.03
        _SunGlow ("Sun glow", Range(0, 2)) = 0.35
        [NoScaleOffset] _NoiseMap ("Cloud noise", 2D) = "grey" {}
        _CloudCoverage ("Cloud coverage", Range(0, 1)) = 0.45
        _CloudSoftness ("Cloud softness", Range(0.01, 0.5)) = 0.18
        _CloudScale ("Cloud scale", Float) = 0.35
        _CloudSpeed ("Cloud drift", Float) = 0.004
        _CloudLit ("Cloud lit", Color) = (0.96, 0.95, 0.92, 1)
        _CloudShade ("Cloud shade", Color) = (0.62, 0.66, 0.71, 1)
        _Exposure ("Exposure", Float) = 1
    }
    SubShader
    {
        Tags { "Queue" = "Background" "RenderType" = "Background" "PreviewType" = "Skybox" "RenderPipeline" = "UniversalPipeline" }
        Cull Off ZWrite Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _ZenithColor, _HorizonColor, _GroundColor, _SunColor, _CloudLit, _CloudShade;
                float _Gradient, _Haze, _SunSize, _SunGlow, _CloudCoverage, _CloudSoftness, _CloudScale, _CloudSpeed, _Exposure;
            CBUFFER_END
            TEXTURE2D(_NoiseMap); SAMPLER(sampler_NoiseMap);
            float4 _JD_SunDir;   // set by the lighting rig; URP's main light is used when present

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 dir : TEXCOORD0; };

            Varyings vert(Attributes v)
            {
                Varyings o;
                o.positionCS = TransformObjectToHClip(v.positionOS.xyz);
                o.dir = v.positionOS.xyz;
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                float3 d = normalize(i.dir);
                float3 sun = dot(_MainLightPosition.xyz, _MainLightPosition.xyz) > 0.01 ? normalize(_MainLightPosition.xyz) : normalize(_JD_SunDir.xyz + float3(0, 1e-4, 0));
                float up = d.y;
                half3 sky = up >= 0 ? lerp(_HorizonColor.rgb, _ZenithColor.rgb, pow(saturate(up), _Gradient))
                                    : lerp(_HorizonColor.rgb, _GroundColor.rgb, saturate(-up * 5.0));
                float sd = saturate(dot(d, sun));
                sky += _SunColor.rgb * (pow(sd, 64.0) * _SunGlow + pow(sd, 6.0) * _SunGlow * 0.25);
                // clouds on a plane above the town
                half cover = 0;
                if (up > 0.0)
                {
                    float2 uv = d.xz / (up + 0.12) * _CloudScale + _Time.y * _CloudSpeed * float2(1.0, 0.35);
                    half n = SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, uv).r * 0.6
                           + SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, uv * 2.7 + 0.37).g * 0.3
                           + SAMPLE_TEXTURE2D(_NoiseMap, sampler_NoiseMap, uv * 6.1 + 0.71).a * 0.1;
                    half t = 1.0 - _CloudCoverage;
                    cover = smoothstep(t, t + _CloudSoftness, n) * smoothstep(0.0, 0.18, up);
                    half lit = saturate((n - t) * 2.0 + pow(sd, 3.0) * 0.5);
                    half3 cloud = lerp(_CloudShade.rgb, _CloudLit.rgb, lit);
                    sky = lerp(sky, cloud, cover * 0.95);
                }
                float disk = smoothstep(cos(_SunSize), cos(_SunSize * 0.6), sd);
                sky = lerp(sky, _SunColor.rgb * 3.0, disk * saturate(up * 20.0) * (1.0 - cover));
                sky = lerp(sky, _HorizonColor.rgb, _Haze * exp(-abs(up) * 9.0));
                return half4(sky * _Exposure, 1);
            }
            ENDHLSL
        }
    }
}
