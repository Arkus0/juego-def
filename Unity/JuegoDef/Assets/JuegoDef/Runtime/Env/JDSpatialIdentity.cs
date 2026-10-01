using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>Passive authored identity. It never creates, moves or restores scene objects.</summary>
    [DisallowMultipleComponent]
    public sealed class JDSpatialIdentity : MonoBehaviour
    {
        public string stableId;
        public string kind;
        public string sourceId;
        [Tooltip("Documentation only: shared paving may serve several streets. No layout reconstruction.")]
        public Vector3[] referenceOutline = new Vector3[0];
    }
}
