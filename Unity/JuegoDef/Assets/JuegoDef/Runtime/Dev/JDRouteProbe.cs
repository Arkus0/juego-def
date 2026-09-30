using System.Collections;
using System.Text;
using GameCreator.Runtime.Characters;
using GameCreator.Runtime.Common;
using UnityEngine;

namespace JuegoDef.Dev
{
    /// <summary>
    /// Development probe: in Play Mode, drives the GC2 player through a waypoint route with its real character
    /// controller and logs arrivals, stalls and the colliders involved. Screenshots miss collision defects; walking
    /// the route does not. Leave the GameObject disabled; enable it for a test run. Log lines start with JD_ROUTE.
    /// </summary>
    public class JDRouteProbe : MonoBehaviour
    {
        public Vector3[] waypoints;
        public float arriveDistance = 0.7f;
        public float stuckSeconds = 2.5f;
        public float waypointTimeout = 40f;

        IEnumerator Start()
        {
            yield return new WaitForSeconds(0.5f);
            Character player = null;
            foreach (var c in FindObjectsByType<Character>(FindObjectsSortMode.None))
                if (c.IsPlayer) player = c;
            if (player == null) { Debug.LogError("JD_ROUTE NO_PLAYER"); yield break; }

            float startTime = Time.time, walked = 0f;
            int reached = 0, stalls = 0;
            var last = player.transform.position;
            Debug.Log($"JD_ROUTE START waypoints={waypoints.Length} at={Fmt(last)}");
            for (int i = 0; i < waypoints.Length; i++)
            {
                var target = waypoints[i];
                bool finished = false;
                player.Motion.MoveToLocation(new Location(target), 0.3f, (_, _) => finished = true, 1);
                float t0 = Time.time, lastProgress = Time.time;
                var progressAt = player.transform.position;
                string outcome = "REACHED";
                while (Flat(player.transform.position - target) > arriveDistance && !finished)
                {
                    yield return new WaitForSeconds(0.2f);
                    var p = player.transform.position;
                    walked += (p - last).magnitude;
                    last = p;
                    if ((p - progressAt).magnitude > 0.15f) { progressAt = p; lastProgress = Time.time; }
                    if (Time.time - lastProgress > stuckSeconds) { outcome = "STUCK"; break; }
                    if (Time.time - t0 > waypointTimeout) { outcome = "TIMEOUT"; break; }
                }
                if (Flat(player.transform.position - target) <= arriveDistance) outcome = "REACHED";
                else if (outcome == "REACHED") outcome = "ABORTED";  // motion reported finished short of the target
                if (outcome == "REACHED") reached++;
                else
                {
                    stalls++;
                    Debug.LogWarning($"JD_ROUTE {outcome} wp={i} target={Fmt(target)} at={Fmt(player.transform.position)} blockers={Blockers(player)}");
                    // Resume from the target so one defect does not hide the rest of the route.
                    // waypoints are ground points; the GC2 character pivot sits ~1 m above the ground
                    player.Driver.SetPosition(target + Vector3.up * 1.1f);
                    yield return new WaitForSeconds(0.3f);
                    last = player.transform.position;
                }
                Debug.Log($"JD_ROUTE wp={i} {outcome} t={Time.time - t0:F1}s at={Fmt(player.transform.position)}");
            }
            player.Motion.StopToDirection(1);
            Debug.Log($"JD_ROUTE END reached={reached}/{waypoints.Length} stalls={stalls} walked={walked:F1}m time={Time.time - startTime:F1}s");
        }

        static float Flat(Vector3 v) => new Vector2(v.x, v.z).magnitude;
        static string Fmt(Vector3 v) => $"({v.x:F2},{v.y:F2},{v.z:F2})";

        static string Blockers(Character player)
        {
            var sb = new StringBuilder();
            var hits = Physics.OverlapSphere(player.transform.position + player.transform.forward * 0.4f, 0.45f);
            foreach (var h in hits)
                if (!h.transform.IsChildOf(player.transform))
                    sb.Append(h.transform.parent ? h.transform.parent.name + "/" : "").Append(h.name).Append(' ');
            return sb.Length > 0 ? sb.ToString().TrimEnd() : "none";
        }
    }
}
