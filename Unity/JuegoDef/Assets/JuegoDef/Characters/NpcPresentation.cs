using System;
using UnityEngine;
using GameCreator.Runtime.Common;

namespace JuegoDef.Characters
{
    /// <summary>Small additive gaze and anatomical blinking layer. The existing
    /// Animator owns locomotion, breathing, weight shifts and every state.</summary>
    [DisallowMultipleComponent]
    public sealed class NpcPresentation : MonoBehaviour
    {
        public int seed = 1;
        public Transform attentionTarget;
        public float attentionRange = 4.5f;
        public SkinnedMeshRenderer face, eyes;

        Animator animator;
        Transform head, player, playerHead;
        int left = -1, right = -1, gazeLeft = -1, gazeRight = -1, gazeUp = -1, gazeDown = -1;
        uint random;
        float birth, lastTime = -1, nextBlink, duration, yaw, pitch;
        bool secondBlink, initialized, applied;
        Quaternion inputHead, outputHead;

        public float BlinkLeftWeight { get; private set; }
        public float BlinkRightWeight { get; private set; }
        public float GazeYaw { get; private set; }
        public float GazePitch { get; private set; }
        public float HeadYaw { get; private set; }
        public bool Ready => Initialize() && left >= 0 && right >= 0 && gazeLeft >= 0 && gazeRight >= 0 && gazeUp >= 0 && gazeDown >= 0;

        void OnEnable() { birth = Time.time; initialized = false; applied = false; }
        void LateUpdate() => Sample(Time.time - birth, Time.deltaTime);
        void OnDisable()
        {
            RestoreHead();
            if (face != null) { Set(face, left, 0); Set(face, right, 0); }
            if (eyes != null) foreach (int index in new[] { gazeLeft, gazeRight, gazeUp, gazeDown }) Set(eyes, index, 0);
        }

        bool Initialize()
        {
            if (initialized) return head != null;
            animator = GetComponent<Animator>();
            if (animator == null || animator.avatar == null || !animator.avatar.isHuman) return false;
            head = animator.GetBoneTransform(HumanBodyBones.Head);
            foreach (var renderer in GetComponentsInChildren<SkinnedMeshRenderer>())
            {
                if (face == null && renderer.name.StartsWith("HumanHead", StringComparison.Ordinal)) face = renderer;
                if (eyes == null && renderer.name.StartsWith("HumanEyes", StringComparison.Ordinal)) eyes = renderer;
            }
            if (face == null || eyes == null || head == null) return false;
            left = Index(face, "BlinkLeft"); right = Index(face, "BlinkRight");
            gazeLeft = Index(eyes, "GazeLeft"); gazeRight = Index(eyes, "GazeRight");
            gazeUp = Index(eyes, "GazeUp"); gazeDown = Index(eyes, "GazeDown");
            ResetSchedule(); initialized = true;
            return true;
        }

        static int Index(SkinnedMeshRenderer renderer, string name)
        {
            var mesh = renderer.sharedMesh;
            for (int i = 0; i < mesh.blendShapeCount; i++)
            {
                string value = mesh.GetBlendShapeName(i);
                if (value == name || value.EndsWith("." + name, StringComparison.Ordinal)) return i;
            }
            return -1;
        }
        static void Set(SkinnedMeshRenderer renderer, int index, float value)
        { if (index >= 0) renderer.SetBlendShapeWeight(index, Mathf.Clamp(value, 0, 100)); }
        float Random01()
        {
            random ^= random << 13; random ^= random >> 17; random ^= random << 5;
            return (random & 0xffffff) / 16777216f;
        }
        void ResetSchedule()
        {
            random = unchecked((uint)seed); if (random == 0) random = 1;
            nextBlink = .7f + Random01() * 1.1f;
            duration = .18f + Random01() * .045f;
            lastTime = -1; secondBlink = false; yaw = pitch = 0;
        }
        float Closure(float time)
        {
            if (time < 0 || time > duration) return 0;
            if (time < .052f) return Mathf.SmoothStep(0, 1, time / .052f);
            if (time < .074f) return 1;
            return Mathf.SmoothStep(1, 0, (time - .074f) / (duration - .074f));
        }
        void RestoreHead()
        {
            // Animator normally supplies a fresh base each frame. This also
            // prevents accumulation when a caller samples an unchanged pose.
            if (applied && head != null && Quaternion.Angle(head.rotation, outputHead) < .002f)
                head.rotation = inputHead;
            applied = false;
        }
        Vector3? AttentionPoint()
        {
            if (attentionTarget != null) return attentionTarget.position;
            var current = ShortcutPlayer.Instance;
            var canonical = current != null ? current.transform : null;
            if (canonical != player)
            {
                player = canonical; playerHead = null;
                var rig = player != null ? player.GetComponentInChildren<Animator>() : null;
                if (rig != null && rig.avatar != null && rig.avatar.isHuman)
                    playerHead = rig.GetBoneTransform(HumanBodyBones.Head);
            }
            if (player == null) return null;
            return playerHead != null ? playerHead.position : player.position + Vector3.up * 1.55f;
        }

        /// <summary>The same bounded update used by LateUpdate, exposed for
        /// reproducible Play Mode observation alongside the admitted clips.</summary>
        public void Sample(float elapsed, float deltaTime)
        {
            if (!Initialize() || !float.IsFinite(elapsed) || !float.IsFinite(deltaTime)) return;
            RestoreHead();
            if (elapsed < lastTime) ResetSchedule();
            while (elapsed > nextBlink + duration)
            {
                if (!secondBlink && Random01() < .10f) { nextBlink += duration + .11f; secondBlink = true; }
                else { nextBlink += duration + 2.4f + Random01() * 3.1f; secondBlink = false; }
                duration = .18f + Random01() * .045f;
            }
            float blinkTime = elapsed - nextBlink;
            BlinkLeftWeight = Closure(blinkTime) * 100;
            BlinkRightWeight = Closure(blinkTime - .006f) * 100;
            Set(face, left, BlinkLeftWeight); Set(face, right, BlinkRightWeight);

            float wantedYaw = 0, wantedPitch = 0;
            var point = AttentionPoint();
            if (point.HasValue && Vector3.Distance(point.Value, head.position) < attentionRange)
            {
                var local = transform.InverseTransformDirection(point.Value - head.position);
                float angle = Mathf.Atan2(local.x, local.z) * Mathf.Rad2Deg;
                if (Mathf.Abs(angle) < 70)
                {
                    wantedYaw = Mathf.Clamp(angle, -18, 18);
                    wantedPitch = Mathf.Clamp(Mathf.Atan2(local.y, new Vector2(local.x, local.z).magnitude) * Mathf.Rad2Deg, -12, 12);
                }
            }
            float phase = (unchecked((uint)seed) % 1009) * .031f;
            float follow = 1 - Mathf.Exp(-Mathf.Clamp(deltaTime, 0, .2f) * 4.5f);
            yaw = Mathf.Lerp(yaw, wantedYaw, follow); pitch = Mathf.Lerp(pitch, wantedPitch, follow);
            HeadYaw = Mathf.Clamp(yaw * .45f + Mathf.Sin(elapsed * .63f + phase) * .60f, -8, 8);
            float headPitch = Mathf.Clamp(pitch * .4f + Mathf.Sin(elapsed * .47f + phase * 1.3f) * .35f, -5, 5);
            inputHead = head.rotation;
            head.rotation = Quaternion.AngleAxis(HeadYaw, transform.up) * Quaternion.AngleAxis(-headPitch, transform.right) * inputHead;
            outputHead = head.rotation; applied = true;
            GazeYaw = Mathf.Clamp(yaw - HeadYaw + Mathf.Sin(elapsed * .39f + phase) * 1.3f, -10, 10);
            GazePitch = Mathf.Clamp(pitch - headPitch, -9, 9);
            Set(eyes, gazeLeft, Mathf.Max(0, -GazeYaw) / 12 * 100); Set(eyes, gazeRight, Mathf.Max(0, GazeYaw) / 12 * 100);
            Set(eyes, gazeUp, Mathf.Max(0, GazePitch) / 12 * 100); Set(eyes, gazeDown, Mathf.Max(0, -GazePitch) / 12 * 100);
            lastTime = elapsed;
        }
    }
}
