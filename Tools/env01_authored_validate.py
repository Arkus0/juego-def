"""Validate ENV01's recorded full-population Unity audits and immutable asset snapshot.

Run from any directory. Fresh Unity audits are made with EnvAuthoredMigration.Audit;
this command checks their relationships and the actual files, not just report booleans.
"""
from pathlib import Path
import hashlib
import json
import sys

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "Unity/JuegoDef"
EVIDENCE = REPO / "Docs/evidence/WP-ENV01-AUTHORED-01"


def read(name):
    return json.loads((EVIDENCE / (name + ".json")).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(path):
    data = path.read_bytes()
    if data.startswith(b"%YAML") or path.suffix == ".meta":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main():
    checks = {}
    audits = {n: read(n) for n in ["SOURCE_AUDIT", "COPIED_AUDIT", "AUTHORED_BASELINE",
                                  "REFERENCE_AUDIT", "EDIT_SAVED_AUDIT", "AFTER_EDITOR_RESTART",
                                  "AFTER_PLAY", "AUTHORED_FINAL", "CANDIDATE_CLEAN_SOURCES", "CANDIDATE_CLEAN_AFTER_PLAY"]}
    digests = ["rendererDigest", "colliderDigest", "lightDigest"]
    for name, audit in audits.items():
        checks[name + ":no_missing"] = not audit["missingReferences"] and all(
            audit[k] == 0 for k in ["missingMeshes", "missingMaterials", "temporaryMeshes"])
        checks[name + ":unique_ids"] = not audit["duplicateIds"]
    for name in ["COPIED_AUDIT", "AUTHORED_BASELINE", "REFERENCE_AUDIT", "AUTHORED_FINAL", "CANDIDATE_CLEAN_SOURCES", "CANDIDATE_CLEAN_AFTER_PLAY"]:
        checks[name + ":source_equivalence"] = all(audits[name][k] == audits["SOURCE_AUDIT"][k] for k in digests)
    for name in ["AFTER_EDITOR_RESTART", "AFTER_PLAY"]:
        checks[name + ":edited_state_unchanged"] = all(audits[name][k] == audits["EDIT_SAVED_AUDIT"][k]
                                                       for k in digests + ["objects", "identities"])
    for name in ["EDIT_AFTER_SCENE_REOPEN", "EDIT_AFTER_DOMAIN_RELOAD", "EDIT_AFTER_EDITOR_RESTART", "EDIT_IN_PLAY", "EDIT_AFTER_PLAY"]:
        checks[name + ":persists"] = read(name)["persisted"]
    checks["real_editor_restart"] = read("RESTART_BEFORE")["pid"] != read("EDIT_AFTER_EDITOR_RESTART")["pid"]
    checks["play_mode_observed"] = read("EDIT_IN_PLAY")["playing"] and not read("EDIT_AFTER_PLAY")["playing"]
    checks["six_legacy_rebuild_paths_blocked"] = read("REGEN_GUARDS")["allBlocked"]
    checks["seven_clean_candidate_rebuild_paths_blocked"] = read("CANDIDATE_CLEAN_GUARDS")["allBlocked"]
    clean_play = read("CANDIDATE_CLEAN_PLAY")
    checks["clean_candidate_play_no_generation"] = clean_play["playing"] and clean_play["environmentObjects"] == read("EDIT_IN_PLAY")["environmentObjects"] and clean_play["environmentPrefabInstances"] == 0
    checks["additive_guard"] = read("ADDITIVE_GUARD")["blockedWithOrdinarySceneActive"]
    inventory = read("INVENTORY")
    checks["no_environment_prefab_links"] = inventory["environmentPrefabInstances"] == 0
    deps = read("AUTHORED_DEPENDENCIES")
    checks["no_mutable_legacy_env_dependencies"] = not any("/Derived/ENV/" in p for p in deps)
    checks["no_prefab_dependencies"] = not any(p.endswith(".prefab") for p in deps)
    checks["no_trace_or_spec_dependencies"] = not any("/Specs/" in p for p in deps)
    snapshots = read("ASSET_SNAPSHOT")
    original_available = (PROJECT / "Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity").exists()
    if original_available:
        checks["original_scene_and_asset_bytes_intact"] = all((PROJECT / x["source"]).exists()
            and (PROJECT / (x["source"] + ".meta")).exists()
            and sha(PROJECT / x["source"]) == x["source_sha256"]
            and sha(PROJECT / (x["source"] + ".meta")) == x["source_meta_sha256"] for x in snapshots)
    checks["authored_snapshot_assets_intact"] = all(x["authored"].endswith(".unity") or (
        canonical_sha(PROJECT / x["authored"]) == x["authored_canonical_sha256"]
        and canonical_sha(PROJECT / (x["authored"] + ".meta")) == x["authored_meta_canonical_sha256"]) for x in snapshots)
    ids = {x["id"] for x in inventory["entries"]}
    candidates = read("CONSOLIDATION_CANDIDATES")
    checks["all_candidates_resolve_to_native_buildings"] = not candidates["unresolved"] and all(
        set(c["buildings"]) <= ids for c in candidates["candidates"])
    result = {"passed": all(checks.values()), "checks": checks, "original_local_available": original_available,
              "original_check_if_absent": "Use the committed pre-migration REFERENCE_AUDIT and ENV01_REFERENCE; never regenerate the original to run this check.", "counts": {
        "buildings": inventory["buildingGroups"], "streets": inventory["streets"], "open_spaces": inventory["openSpaces"],
        "approximate_props": inventory["approximateProps"], "vegetation_roots_outside_buildings": inventory["vegetationRoots"],
        "candidate_groups_overlapping_not_selected": candidates["count"], "frozen_assets": len(snapshots)-1}}
    (EVIDENCE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
