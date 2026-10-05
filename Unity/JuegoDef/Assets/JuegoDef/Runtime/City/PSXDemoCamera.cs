using UnityEngine;

namespace JuegoDef.City
{
    /// <summary>
    /// Demo third-person camera for CITY_B_PS1_DEMO. Simple, deterministic PS1-style orbit: follows the player's head,
    /// yaw from the mouse (auto-aligns behind movement after 1.5 s idle), fixed downward pitch, sphere-cast collision so
    /// the camera never goes through walls or under the terrain (the GC2 shot solver ended up below the plaza floor).
    /// Exposes the framing the demo was authored with: radius 3.6 m, head +1.6 m, pitch -12 degrees, FOV 60.
    /// </summary>
    [DefaultExecutionOrder(200)]
    public class PSXDemoCamera : MonoBehaviour
    {
        public Transform target;
        public float radius = 3.6f;
        public float headHeight = 1.6f;
        public float pitchDeg = 12f;
        public float fov = 60f;
        public float mouseSensitivity = 2.2f;
        public float maxYaw = 180f;
        [Tooltip("Seconds without mouse input before the camera aligns behind the movement direction.")]
        public float alignDelay = 1.5f;
        public float alignSpeed = 2.5f;
        public float smoothTime = 0.08f;
        public float skinWidth = 0.35f;
        public LayerMask collisionMask = ~0;

        float yaw;
        float lastInputTime = -10f;
        Vector3 camPosVelocity;

        void Start()
        {
            var cam = GetComponent<Camera>();
            if (cam != null) cam.fieldOfView = fov;
            if (target != null) yaw = target.eulerAngles.y;
        }

        void LateUpdate()
        {
            if (target == null) return;
            var mouse = UnityEngine.InputSystem.Mouse.current;
            if (mouse != null)
            {
                var d = mouse.delta.ReadValue() * mouseSensitivity * 0.02f;
                if (Mathf.Abs(d.x) > 0.0001f)
                {
                    yaw += d.x;
                    lastInputTime = Time.unscaledTime;
                }
            }
            yaw = Mathf.Repeat(yaw + 180f, 360f) - 180f;

            // auto-align behind movement
            var player = target.GetComponent<GameCreator.Runtime.Characters.Character>();
            if (player != null && player.Motion != null && Time.unscaledTime - lastInputTime > alignDelay)
            {
                var dir = (Vector3)player.Motion.MoveDirection;
                if (dir.sqrMagnitude > 0.0001f)
                {
                    var targetYaw = Mathf.Atan2(dir.x, dir.z) * Mathf.Rad2Deg;
                    yaw = Mathf.LerpAngle(yaw, targetYaw, alignSpeed * Time.unscaledDeltaTime);
                }
            }

            float pitch = pitchDeg * Mathf.Deg2Rad;
            var head = target.position + Vector3.up * headHeight;
            var dir3 = new Vector3(Mathf.Sin(yaw * Mathf.Deg2Rad) * Mathf.Cos(pitch), -Mathf.Sin(pitch), Mathf.Cos(yaw * Mathf.Deg2Rad) * Mathf.Cos(pitch));
            var desired = head - dir3 * radius;

            // collision: pull the camera in front of anything between head and desired position
            var toCam = desired - head;
            float dist = toCam.magnitude;
            if (Physics.SphereCast(head, skinWidth, toCam / Mathf.Max(dist, 0.001f), out var hit, dist, collisionMask, QueryTriggerInteraction.Ignore))
                desired = head + (toCam / dist) * Mathf.Max(hit.distance - skinWidth, 0.4f);
            // never under the ground plane of the hit nor under water level
            if (Physics.Raycast(desired + Vector3.up * 2f, Vector3.down, out var floor, 60f, collisionMask, QueryTriggerInteraction.Ignore))
                desired.y = Mathf.Max(desired.y, floor.point.y + 0.45f);
            desired.y = Mathf.Max(desired.y, 0.6f);

            transform.position = Vector3.SmoothDamp(transform.position, desired, ref camPosVelocity, smoothTime, Mathf.Infinity, Time.unscaledDeltaTime);
            transform.LookAt(head);
        }
    }
}
