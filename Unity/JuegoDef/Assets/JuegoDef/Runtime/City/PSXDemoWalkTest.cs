using UnityEngine;

namespace JuegoDef.City
{
    /// <summary>
    /// Dev/attract-mode walk: drives the GC2 character forward (MoveToDirection is a per-frame velocity command, so a
    /// one-shot reflection call does nothing). Attach in Play Mode to verify locomotion, collision and the walk cycle
    /// along the demo route; remove before shipping. W holds a manual walk even without input hardware.
    /// </summary>
    public class PSXDemoWalkTest : MonoBehaviour
    {
        public Vector3 direction = new Vector3(0f, 0f, -1f);
        public bool autoWalk = true;

        void FixedUpdate()
        {
            var character = GetComponent<GameCreator.Runtime.Characters.Character>();
            if (character == null || character.Motion == null) return;
            bool walk = autoWalk || (UnityEngine.InputSystem.Keyboard.current != null && UnityEngine.InputSystem.Keyboard.current.wKey.isPressed);
            if (walk) character.Motion.MoveToDirection(direction.normalized, Space.World, 0);
        }
    }
}
