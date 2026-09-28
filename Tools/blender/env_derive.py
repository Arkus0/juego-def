"""juego-def ENV derivation recipes — Blender 5.x, headless, repeatable.

    blender -b --factory-startup --python Tools/blender/env_derive.py -- [--only NAME[,NAME]] [--vault DIR]

Every recipe writes one FBX to Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/Meshes/<NAME>.fbx and one entry in
Docs/asset_catalog/env_derive_manifest.json (lineage class, donor module names, method). Donor meshes are *read*
from the vault source file `Medieval Village/MedievalVillage_AllModels.blend` (CC0) and never written back.

Recipes are written in the Unity bay-slot frame: x right, y up, z towards the street (the kit wall's street face
sits at z = +0.09). U() converts to Blender (-x, -z, y): the kit's own Unity exports are the Blender source rotated
180 degrees about the vertical, so export() applies that rotation to donors and new geometry alike. Material slot
names are the Unity material names; the Unity module step binds them with Search-and-Remap, so palette remapping
works exactly as on vendor modules.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "Unity" / "JuegoDef" / "Assets" / "JuegoDef" / "Derived" / "ENV" / "Meshes"
MANIFEST_PATH = REPO / "Docs" / "asset_catalog" / "env_derive_manifest.json"
DEFAULT_VAULT = Path("C:/Juego2-Assets")
DONOR_BLEND = "Medieval Village/MedievalVillage_AllModels.blend"
UV_PER_M = 0.5            # kit texel density: tiling/trim textures repeat every ~2 m
WOOD_LIGHT = (0.72, 0.97)  # MI_WoodTrim trim-sheet band: light planks (painted via palette)
WOOD_DARK = (0.44, 0.66)   # MI_WoodTrim band: dark planks
ROCK_SLAB = (0.43, 0.66)   # MI_RockTrim band: smooth grey slab (copings, kerbs, sills)
ROCK_ASHLAR = (0.02, 0.40) # MI_RockTrim band: ashlar blocks

# Lineage classes: DONOR = geometry copied from named kit modules (listed as donors); CREATE_DERIVED = new
# geometry textured with kit materials/trim sheets (material provenance is traced by Tools/env_catalog.py);
# ORIGINAL = new geometry with owned flat materials only.
RECIPES: dict[str, callable] = {}
MANIFEST: dict[str, dict] = {}
VAULT = DEFAULT_VAULT


def recipe(name, lineage, donors=(), method=""):
    def wrap(fn):
        RECIPES[name] = fn
        MANIFEST[name] = {"class": lineage, "donors": list(donors), "method": method or (fn.__doc__ or "").strip()}
        return fn
    return wrap


# ---------------------------------------------------------------- geometry helpers (Unity slot frame)

def U(x, y, z):
    return Vector((-x, -z, y))


def material(name):
    return bpy.data.materials.get(name) or bpy.data.materials.new(name)


def new_object(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def box(name, lo, hi, mat, uv="box", band=None, bevel=0.0):
    """Axis-aligned box between Unity-frame corners lo/hi."""
    bm = bmesh.new()
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = [bm.verts.new(U(x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    idx = lambda i, j, k: v[i * 4 + j * 2 + k]
    faces = [
        (idx(0, 0, 0), idx(0, 0, 1), idx(0, 1, 1), idx(0, 1, 0)),
        (idx(1, 0, 0), idx(1, 1, 0), idx(1, 1, 1), idx(1, 0, 1)),
        (idx(0, 0, 0), idx(1, 0, 0), idx(1, 0, 1), idx(0, 0, 1)),
        (idx(0, 1, 0), idx(0, 1, 1), idx(1, 1, 1), idx(1, 1, 0)),
        (idx(0, 0, 0), idx(0, 1, 0), idx(1, 1, 0), idx(1, 0, 0)),
        (idx(0, 0, 1), idx(1, 0, 1), idx(1, 1, 1), idx(0, 1, 1)),
    ]
    for f in faces:
        bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    if bevel > 0:
        do_bevel(ob, bevel)
    if uv == "box":
        uv_box(ob)
    elif uv == "band":
        uv_band(ob, band)
    return ob


def cylinder(name, center, radius, height, mat, segments=12, band=None, axis="y"):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=radius, radius2=radius, depth=height)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    # created along Blender Z (= Unity y); rotate for other axes
    if axis == "x":
        ob.rotation_euler = (0, math.radians(90), 0)
    elif axis == "z":
        ob.rotation_euler = (math.radians(90), 0, 0)
    ob.location = U(*center)
    apply_transform(ob)
    if band:
        uv_band(ob, band)
    else:
        uv_box(ob)
    return ob


def sphere(name, center, radius, mat, segments=12):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=max(6, segments // 2), radius=radius)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    ob.location = U(*center)
    apply_transform(ob)
    uv_box(ob)
    return ob


def apply_transform(ob):
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def do_bevel(ob, width, segments=1):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=width, segments=segments, affect="EDGES", clamp_overlap=True)
    bm.to_mesh(ob.data)
    bm.free()


def _uv_layer(me):
    return me.uv_layers.active or me.uv_layers.new(name="UVMap")


def uv_box(ob, scale=UV_PER_M, only=None):
    """World-scale box projection; keeps tiling textures at kit density."""
    me = ob.data
    layer = _uv_layer(me).data
    for p in me.polygons:
        if only and me.materials[p.material_index].name not in only:
            continue
        n = p.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            layer[li].uv = (co[a] * scale, co[b] * scale)


def uv_band(ob, band, scale=UV_PER_M, only=None):
    """Trim-sheet mapping: U runs along the face's long side in metres, V squeezes the short side into band."""
    v0, v1 = band
    me = ob.data
    layer = _uv_layer(me).data
    for p in me.polygons:
        if only and me.materials[p.material_index].name not in only:
            continue
        n = p.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        pts = [me.vertices[me.loops[li].vertex_index].co for li in p.loop_indices]
        ea = max(c[a] for c in pts) - min(c[a] for c in pts)
        eb = max(c[b] for c in pts) - min(c[b] for c in pts)
        long_, short = (a, b) if ea >= eb else (b, a)
        smin = min(c[short] for c in pts)
        sext = max(max(c[short] for c in pts) - smin, 1e-6)
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            layer[li].uv = (co[long_] * scale, v0 + (co[short] - smin) / sext * (v1 - v0))


def join(name, objs):
    objs = [o for o in objs if o]
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name
    return ob


def donor(name):
    """Copies one donor object from the vault source .blend into the scene (vault file is only read)."""
    path = str(VAULT / DONOR_BLEND)
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [name]
    ob = dst.objects[0]
    if ob is None:
        raise KeyError(f"donor {name} not found in {path}")
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (0, 0, 0)
    ob.rotation_euler = (0, 0, 0)
    apply_transform(ob)
    return ob


def cut(ob, cutter):
    """Boolean difference; faces created by the cutter take the cutter's material and UVs (stone reveals)."""
    mod = ob.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.use_hole_tolerant = True  # kit walls are open shells (no end caps)
    mod.object = cutter
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return ob


def export(ob, name):
    OUT.mkdir(parents=True, exist_ok=True)
    # tube() leaves QUATERNION mode on the joined object, where rotation_euler is ignored: force Euler first
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = (0, 0, math.pi)  # match the kit's Blender -> Unity orientation (see U())
    apply_transform(ob)
    bpy.ops.object.material_slot_remove_unused()  # no empty sub-meshes in Unity
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    path = OUT / f"{name}.fbx"
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y", bake_space_transform=True,
        mesh_smooth_type="FACE", use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False,
        path_mode="STRIP", embed_textures=False)
    return path


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


# ---------------------------------------------------------------- shared shop/wall dimensions

OPEN_W = 1.6      # shopfront/gate/gallery opening width in a 2 m bay
OPEN_H = 2.38     # head height aligned with kit door frames
WALL_FACE = 0.092 # kit wall street face (z)


def opening_cutter(depth_from=-0.5, depth_to=0.5, mat="MI_RockTrim"):
    c = box("cutter", (-OPEN_W / 2, -0.05, depth_from), (OPEN_W / 2, OPEN_H, depth_to), mat, uv="band", band=ROCK_SLAB)
    return c


# ---------------------------------------------------------------- recipes: frontage

def clean_plaster(donor_name, brick_to_plaster=True):
    """Removes the kit's half-timbering from a plaster wall: every loose MI_WoodTrim part except the full-width
    floor-line band (top 0.24 m) is deleted — braces, posts and the sill-height band are Alpine/medieval cues.
    The plaster plane is continuous behind them, so nothing opens. Optionally exposed-brick spandrels become plaster."""
    ob = donor(donor_name)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.faces.ensure_lookup_table()
    mats = [m.name for m in ob.data.materials]
    seen, doomed = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack, comp = [f], []
        while stack:
            x = stack.pop()
            if x.index in seen:
                continue
            seen.add(x.index)
            comp.append(x)
            for e in x.edges:
                stack.extend(g for g in e.link_faces if g.index not in seen)
        if {mats[c.material_index] for c in comp} != {"MI_WoodTrim"}:
            continue
        vs = {v for c in comp for v in c.verts}
        width = max(v.co.x for v in vs) - min(v.co.x for v in vs)
        zmin = min(v.co.z for v in vs)
        if not (width >= 1.9 and zmin >= 2.8):
            doomed.extend(comp)
    bmesh.ops.delete(bm, geom=doomed, context="FACES")
    if brick_to_plaster and "MI_Brick" in mats and "MI_Plaster" in mats:
        bi, pi = mats.index("MI_Brick"), mats.index("MI_Plaster")
        for f in bm.faces:
            if f.material_index == bi:
                f.material_index = pi
    bm.to_mesh(ob.data)
    bm.free()
    return ob


@recipe("ENV_Wall_Plaster_Clean", "DONOR", ["Wall_Plaster_Straight"])
def wall_plaster_clean():
    """Plain plaster bay without half-timbering: keeps only the floor-line band."""
    return clean_plaster("Wall_Plaster_Straight")


@recipe("ENV_Wall_Plaster_Clean_Base", "DONOR", ["Wall_Plaster_Straight_Base"])
def wall_plaster_clean_base():
    """Ground-floor plaster bay with the kit brick plinth kept, sill band/timber removed."""
    return clean_plaster("Wall_Plaster_Straight_Base", brick_to_plaster=False)


@recipe("ENV_Wall_Plaster_Clean_Window", "DONOR", ["Wall_Plaster_Window_Wide_Flat"])
def wall_plaster_clean_window():
    """Plaster bay with the wide window opening; sill band removed, brick spandrel rendered over."""
    return clean_plaster("Wall_Plaster_Window_Wide_Flat")


@recipe("ENV_Wall_Plaster_Clean_Door", "DONOR", ["Wall_Plaster_Door_Flat"])
def wall_plaster_clean_door():
    """Plaster bay with the flat door opening (portals, balcony doors); side sill bands removed."""
    return clean_plaster("Wall_Plaster_Door_Flat")


@recipe("ENV_Wall_Plaster_Clean_DoorRound", "DONOR", ["Wall_Plaster_Door_Round"])
def wall_plaster_clean_door_round():
    """Plaster bay with the arched door opening; timber removed."""
    return clean_plaster("Wall_Plaster_Door_Round")


@recipe("ENV_Wall_Plaster_Clean_Thin", "DONOR", ["Wall_Plaster_Window_Thin_Round"])
def wall_plaster_clean_thin():
    """Plaster bay with the small round-head window; timber removed."""
    return clean_plaster("Wall_Plaster_Window_Thin_Round")


def clean_gable(donor_name):
    """Gable triangle without the kit's half-timbering and projecting purlins: every loose MI_WoodTrim part goes,
    the plaster triangle (continuous behind the timber) stays and takes the palette facade colour."""
    ob = donor(donor_name)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    mats = [m.name for m in ob.data.materials]
    doomed = [f for f in bm.faces if mats[f.material_index] == "MI_WoodTrim"]
    bmesh.ops.delete(bm, geom=doomed, context="FACES")
    bm.to_mesh(ob.data)
    bm.free()
    return ob


for _span in (4, 6, 8):
    def _make(span=_span):
        return clean_gable(f"Roof_Front_Brick{span}")
    _make.__doc__ = f"Plain plaster gable for a {_span} m span (roof ends above party walls and gable-fronted sheds)."
    recipe(f"ENV_Roof_Gable_{_span}", "DONOR", [f"Roof_Front_Brick{_span}"])(_make)


def _shopfront_wall(donor_name):
    w = clean_plaster(donor_name, brick_to_plaster=False) if "Plaster" in donor_name else donor(donor_name)
    return cut(w, opening_cutter())


@recipe("ENV_Wall_Plaster_Shopfront", "DONOR", ["Wall_Plaster_Straight_Base"])
def wall_plaster_shopfront():
    """Clean plaster ground-floor wall with a 1.6 x 2.38 m shop opening cut by boolean; reveals in kit stone trim."""
    return _shopfront_wall("Wall_Plaster_Straight_Base")


@recipe("ENV_Wall_UnevenBrick_Shopfront", "DONOR", ["Wall_UnevenBrick_Straight"])
def wall_stone_shopfront():
    """Kit rubble-stone wall with the same shop/gate opening; reveals in kit stone trim."""
    return _shopfront_wall("Wall_UnevenBrick_Straight")


def _frame_rect(prefix, x0, x1, y0, y1, zf, zb, t, mat="MI_WoodTrim", band=WOOD_LIGHT, sill=True):
    """Rectangular frame; sill=False leaves a flush threshold (walkable doorways must not have a trip edge)."""
    parts = [
        box(prefix + "L", (x0, y0, zb), (x0 + t, y1, zf), mat, uv="band", band=band, bevel=0.008),
        box(prefix + "R", (x1 - t, y0, zb), (x1, y1, zf), mat, uv="band", band=band, bevel=0.008),
        box(prefix + "T", (x0 + t, y1 - t, zb), (x1 - t, y1, zf), mat, uv="band", band=band, bevel=0.008),
    ]
    if sill:
        parts.append(box(prefix + "B", (x0 + t, y0, zb), (x1 - t, y0 + t, zf), mat, uv="band", band=band, bevel=0.008))
    return parts


@recipe("ENV_Shopfront_Frame", "CREATE_DERIVED")
def shopfront_frame():
    """Display window for the shop opening: painted timber frame, stall-riser panel, mullion, transom light.
    New geometry on the kit MI_WoodTrim trim sheet + MI_WindowGlass (materials from Window_Wide_Flat1)."""
    x0, x1 = -OPEN_W / 2, OPEN_W / 2
    zf, zb = 0.02, -0.10
    parts = _frame_rect("f", x0, x1, 0.0, OPEN_H, zf, zb, 0.09)
    parts.append(box("riser", (x0 + 0.09, 0.09, zb), (x1 - 0.09, 0.62, zf - 0.03), "MI_WoodTrim", uv="band", band=WOOD_LIGHT, bevel=0.01))
    parts.append(box("sill", (x0 + 0.06, 0.60, zb), (x1 - 0.06, 0.66, zf + 0.04), "MI_WoodTrim", uv="band", band=WOOD_LIGHT, bevel=0.01))
    parts.append(box("transom", (x0 + 0.09, 1.95, zb), (x1 - 0.09, 2.02, zf), "MI_WoodTrim", uv="band", band=WOOD_LIGHT, bevel=0.008))
    parts.append(box("mullion", (-0.03, 0.66, zb), (0.03, 1.95, zf - 0.01), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    parts.append(box("glass", (x0 + 0.09, 0.66, -0.06), (x1 - 0.09, OPEN_H - 0.09, -0.05), "MI_WindowGlass", uv="box"))
    return join("ENV_Shopfront_Frame", parts)


DOOR_CLEAR_H = 2.22  # walkable leaf height: GC2 player capsule is 2.0 m + 0.08 skin (kit portal doors clear ~2.3)


def _shopfront_door(name, open_leaf):
    x0, x1 = -OPEN_W / 2, OPEN_W / 2
    zf, zb = 0.02, -0.10
    h = DOOR_CLEAR_H
    parts = _frame_rect("f", x0, x1, 0.0, OPEN_H, zf, zb, 0.08, sill=False)
    # flush granite threshold across the whole wall depth: no slot between pavement and shop floor
    parts.append(box("threshold", (x0, -0.06, -0.42), (x1, 0.0, 0.14), "MI_RockTrim", uv="band", band=ROCK_SLAB))
    parts.append(box("transom", (x0 + 0.08, h, zb), (x1 - 0.08, OPEN_H - 0.08, zf), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    split = x0 + 0.08 + 0.95
    parts.append(box("post", (split, 0.0, zb), (split + 0.07, h, zf), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    # door leaf (slightly recessed): stile/rail frame, kick panel, glass, handle
    leaf = _frame_rect("d", x0 + 0.08, split, 0.02, h, -0.02, -0.08, 0.07)
    leaf.append(box("kick", (x0 + 0.15, 0.09, -0.07), (split - 0.07, 0.45, -0.035), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    leaf.append(box("dglass", (x0 + 0.15, 0.45, -0.06), (split - 0.07, h - 0.07, -0.05), "MI_WindowGlass"))
    leaf.append(box("handle", (split - 0.16, 1.0, -0.02), (split - 0.13, 1.18, 0.02), "MI_MetalOrnaments"))
    if open_leaf:
        leaf_ob = join("leaf", leaf)
        # swing into the shop around the hinge stile (x0 + 0.08, z -0.05)
        hinge = U(x0 + 0.08, 0, -0.05)
        bpy.context.scene.cursor.location = hinge
        for o in bpy.context.selected_objects:
            o.select_set(False)
        leaf_ob.select_set(True)
        bpy.context.view_layer.objects.active = leaf_ob
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        leaf_ob.rotation_euler = (0, 0, math.radians(-88))  # into the shop (design -z), back against the reveal
        apply_transform(leaf_ob)
        parts.append(leaf_ob)
    else:
        parts += leaf
    # side light
    parts.append(box("sriser", (split + 0.07, 0.0, zb), (x1 - 0.08, 0.62, zf - 0.03), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    parts.append(box("sglass", (split + 0.07, 0.62, -0.06), (x1 - 0.08, h, -0.05), "MI_WindowGlass"))
    return join(name, parts)


@recipe("ENV_Shopfront_Door", "CREATE_DERIVED")
def shopfront_door():
    """Shop entrance for the shop opening: glazed door leaf (0.95 m) + side light, flush threshold (closed).
    New geometry on the kit MI_WoodTrim trim sheet + MI_WindowGlass."""
    return _shopfront_door("ENV_Shopfront_Door", False)


@recipe("ENV_Shopfront_Door_Open", "CREATE_DERIVED")
def shopfront_door_open():
    """Same shop entrance with the leaf swung 88 degrees inwards: a walkable 0.9 m public threshold into a shallow
    shop interior (the gameplay open/close interaction belongs to later GC2 work)."""
    return _shopfront_door("ENV_Shopfront_Door_Open", True)


@recipe("ENV_Shutter_Roller", "ORIGINAL")
def shutter_roller():
    """Closed metal roller shutter (persiana) filling the shop opening: ribbed curtain, guide rails, housing box."""
    x0, x1 = -OPEN_W / 2, OPEN_W / 2
    parts = []
    y = 0.0
    i = 0
    while y < OPEN_H - 0.28:
        parts.append(box(f"slat{i}", (x0 + 0.04, y, -0.06), (x1 - 0.04, y + 0.075, -0.03 + (0.012 if i % 2 else 0)), "ENV_Metal_Shutter", bevel=0.006))
        y += 0.075
        i += 1
    parts.append(box("bar", (x0 + 0.04, 0.0, -0.065), (x1 - 0.04, 0.05, -0.015), "ENV_Metal_Iron"))
    parts.append(box("railL", (x0, 0.0, -0.08), (x0 + 0.05, OPEN_H - 0.28, 0.0), "ENV_Metal_Shutter"))
    parts.append(box("railR", (x1 - 0.05, 0.0, -0.08), (x1, OPEN_H - 0.28, 0.0), "ENV_Metal_Shutter"))
    parts.append(box("housing", (x0, OPEN_H - 0.30, -0.10), (x1, OPEN_H, 0.06), "ENV_Metal_Shutter", bevel=0.015))
    parts.append(box("lock", (-0.05, 0.12, -0.03), (0.05, 0.2, 0.0), "ENV_Metal_Iron"))
    return join("ENV_Shutter_Roller", parts)


@recipe("ENV_Gate_Timber", "CREATE_DERIVED")
def gate_timber():
    """Double-leaf plank gate (warehouse / yard) for the shop/gate opening; kit MI_WoodTrim planks + iron straps."""
    x0, x1 = -OPEN_W / 2, OPEN_W / 2
    parts = []
    n = 10
    w = (x1 - x0) / n
    for i in range(n):
        parts.append(box(f"plank{i}", (x0 + i * w + 0.004, 0.02, -0.07), (x0 + (i + 1) * w - 0.004, OPEN_H - 0.02, -0.02), "MI_WoodTrim", uv="band", band=WOOD_DARK, bevel=0.006))
    for yy in (0.35, 1.2, 2.0):
        for sgn in (-1, 1):
            xa, xb = (x0 + 0.05, -0.03) if sgn < 0 else (0.03, x1 - 0.05)
            parts.append(box(f"strap{yy}{sgn}", (xa, yy, -0.02), (xb, yy + 0.07, 0.0), "ENV_Metal_Iron"))
    parts.append(box("wicketgap", (-0.01, 0.02, -0.021), (0.01, OPEN_H - 0.02, -0.018), "ENV_Metal_Iron"))
    return join("ENV_Gate_Timber", parts)


@recipe("ENV_Door_Service", "ORIGINAL")
def door_service():
    """Plain galvanised service door for the kit Door_Flat wall opening (1.3 m): reads as back-of-house, not public."""
    x0, x1, h = -0.64, 0.64, 2.18
    parts = [
        box("frameL", (x0, 0.0, -0.10), (x0 + 0.06, h, 0.0), "ENV_Metal_Galvanised"),
        box("frameR", (x1 - 0.06, 0.0, -0.10), (x1, h, 0.0), "ENV_Metal_Galvanised"),
        box("frameT", (x0, h - 0.06, -0.10), (x1, h, 0.0), "ENV_Metal_Galvanised"),
        box("leaf", (x0 + 0.06, 0.02, -0.07), (x1 - 0.06, h - 0.06, -0.035), "ENV_Metal_Shutter", bevel=0.01),
        box("louvre", (x0 + 0.25, 0.25, -0.036), (x1 - 0.25, 0.65, -0.02), "ENV_Metal_Galvanised"),
        box("bar", (x0 + 0.2, 1.0, -0.035), (x1 - 0.2, 1.05, 0.0), "ENV_Metal_Iron"),
    ]
    return join("ENV_Door_Service", parts)


@recipe("ENV_Door_Balcony", "CREATE_DERIVED")
def door_balcony():
    """Glazed double balcony door (balconera / ventanal) for the kit Door_Flat wall opening: two leaves with kick
    panels and 2x3 panes. Replaces the kit's plank doors on upper floors. Kit MI_WoodTrim + MI_WindowGlass."""
    x0, x1, y0, y1 = -0.56, 0.56, 0.04, 2.14
    zf, zb = -0.02, -0.10
    parts = []
    for side, (a, b) in enumerate(((x0, 0.0), (0.0, x1))):
        parts += _frame_rect(f"l{side}", a, b, y0, y1, zf, zb, 0.07)
        parts.append(box(f"kick{side}", (a + 0.07, y0 + 0.07, zb + 0.02), (b - 0.07, 0.62, zf - 0.02), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
        parts.append(box(f"glass{side}", (a + 0.07, 0.62, -0.065), (b - 0.07, y1 - 0.07, -0.055), "MI_WindowGlass"))
        mid = (a + b) / 2
        parts.append(box(f"mul{side}", (mid - 0.02, 0.62, zb + 0.02), (mid + 0.02, y1 - 0.07, zf - 0.01), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
        for k, yy in enumerate((1.12, 1.62)):
            parts.append(box(f"tr{side}{k}", (a + 0.07, yy - 0.02, zb + 0.02), (b - 0.07, yy + 0.02, zf - 0.01), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    return join("ENV_Door_Balcony", parts)


@recipe("ENV_Window_Insert_Wide", "CREATE_DERIVED")
def window_insert_wide():
    """Glazed joinery insert for the kit rubble-stone wide window opening (±0.60 x 1.05–2.31 m, measured on the
    donor wall). The kit's `Window_Wide_Flat_Rocks` is only a stone surround; without this the building's empty
    interior shows through. Recessed behind the surround: frame, mullion, transom, glass."""
    x0, x1, y0, y1, zf, zb = -0.6, 0.6, 1.05, 2.31, 0.0, -0.08
    parts = _frame_rect("f", x0, x1, y0, y1, zf, zb, 0.07)
    parts.append(box("mul", (-0.03, y0 + 0.07, zb + 0.01), (0.03, y1 - 0.07, zf - 0.01), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    parts.append(box("tr", (x0 + 0.07, 1.86, zb + 0.01), (x1 - 0.07, 1.91, zf - 0.01), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    parts.append(box("glass", (x0 + 0.07, y0 + 0.07, -0.05), (x1 - 0.07, y1 - 0.07, -0.04), "MI_WindowGlass"))
    return join("ENV_Window_Insert_Wide", parts)


@recipe("ENV_Window_Insert_Thin", "CREATE_DERIVED")
def window_insert_thin():
    """Glazed insert for the kit rubble-stone round-head window (±0.32 m, springing 2.31 m, crown 2.51 m):
    rectangular sash plus a segmental glass head."""
    x0, x1, y0, ys, zf, zb = -0.32, 0.32, 1.05, 2.31, 0.0, -0.08
    parts = _frame_rect("f", x0, x1, y0, ys, zf, zb, 0.06)
    parts.append(box("mul", (-0.025, y0 + 0.06, zb + 0.01), (0.025, ys - 0.06, zf - 0.01), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    parts.append(box("glass", (x0 + 0.06, y0 + 0.06, -0.05), (x1 - 0.06, ys - 0.06, -0.04), "MI_WindowGlass"))
    rise, half = 0.2, 0.32
    radius = (half * half + rise * rise) / (2 * rise)
    cy = ys + rise - radius
    bm = bmesh.new()
    # arc from springing to springing; the chord along y = ys closes the face
    xs = [half * (2 * i / 12 - 1) for i in range(13)]
    bm.faces.new([bm.verts.new(U(x, cy + math.sqrt(max(radius * radius - x * x, 0.0)), -0.045)) for x in xs])
    head = new_object("head", bm)
    head.data.materials.append(material("MI_WindowGlass"))
    uv_box(head)
    parts.append(head)
    return join("ENV_Window_Insert_Thin", parts)


@recipe("ENV_Balcony_Iron", "CREATE_DERIVED")
def balcony_iron():
    """Shallow stone-slab balcony with a wrought-iron railing and two iron brackets (balconera).
    Slab on the kit MI_RockTrim slab band; ironwork is owned flat iron."""
    zf = 0.62
    parts = [box("slab", (-0.95, -0.12, WALL_FACE - 0.05), (0.95, 0.0, zf), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.012)]
    top, rail_z = 1.02, zf - 0.06
    parts.append(box("toprail", (-0.9, top - 0.04, rail_z - 0.03), (0.9, top, rail_z + 0.03), "ENV_Metal_Iron"))
    parts.append(box("botrail", (-0.9, 0.06, rail_z - 0.02), (0.9, 0.1, rail_z + 0.02), "ENV_Metal_Iron"))
    x = -0.9
    i = 0
    while x <= 0.9 + 1e-6:
        parts.append(box(f"bar{i}", (x - 0.012, 0.0, rail_z - 0.012), (x + 0.012, top, rail_z + 0.012), "ENV_Metal_Iron"))
        x += 0.12
        i += 1
    for sx in (-1, 1):
        parts.append(box(f"ret{sx}", (sx * 0.9 - 0.012, 0.0, WALL_FACE), (sx * 0.9 + 0.012, top, rail_z), "ENV_Metal_Iron"))
        parts.append(box(f"rettop{sx}", (sx * 0.9 - 0.02, top - 0.04, WALL_FACE), (sx * 0.9 + 0.02, top, rail_z), "ENV_Metal_Iron"))
        parts.append(box(f"brk{sx}", (sx * 0.7 - 0.02, -0.45, WALL_FACE), (sx * 0.7 + 0.02, -0.12, WALL_FACE + 0.06), "ENV_Metal_Iron"))
        parts.append(box(f"brkd{sx}", (sx * 0.7 - 0.02, -0.16, WALL_FACE), (sx * 0.7 + 0.02, -0.12, zf - 0.1), "ENV_Metal_Iron"))
    return join("ENV_Balcony_Iron", parts)


@recipe("ENV_Gallery_Bay", "CREATE_DERIVED")
def gallery_bay():
    """Glazed gallery bay (galería/mirador) for one 2 m bay and one storey, projecting 0.55 m: timber base panel,
    3x3 glazing grid, cornice and a small lead-grey cap. Stacks storey on storey. Kit MI_WoodTrim + MI_WindowGlass."""
    x0, x1, zf = -1.0, 1.0, 0.62
    parts = [
        box("floor", (x0, -0.08, WALL_FACE - 0.05), (x1, 0.04, zf + 0.04), "MI_WoodTrim", uv="band", band=WOOD_LIGHT, bevel=0.01),
        box("panel", (x0 + 0.04, 0.04, zf - 0.08), (x1 - 0.04, 0.95, zf - 0.02), "MI_WoodTrim", uv="band", band=WOOD_LIGHT, bevel=0.01),
        box("sideL", (x0, 0.04, WALL_FACE), (x0 + 0.08, 2.92, zf), "MI_WoodTrim", uv="band", band=WOOD_LIGHT),
        box("sideR", (x1 - 0.08, 0.04, WALL_FACE), (x1, 2.92, zf), "MI_WoodTrim", uv="band", band=WOOD_LIGHT),
        box("cornice", (x0 - 0.02, 2.86, WALL_FACE - 0.05), (x1 + 0.02, 3.0, zf + 0.06), "MI_WoodTrim", uv="band", band=WOOD_LIGHT, bevel=0.012),
        box("sill", (x0 + 0.04, 0.95, zf - 0.1), (x1 - 0.04, 1.0, zf + 0.03), "MI_WoodTrim", uv="band", band=WOOD_LIGHT),
        box("glass", (x0 + 0.08, 1.0, zf - 0.07), (x1 - 0.08, 2.86, zf - 0.06), "MI_WindowGlass"),
    ]
    for i, xx in enumerate((x0 + 0.08 + (x1 - x0 - 0.16) * k / 3 for k in (1, 2))):
        parts.append(box(f"mul{i}", (xx - 0.03, 1.0, zf - 0.08), (xx + 0.03, 2.86, zf - 0.02), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    for i, yy in enumerate((1.62, 2.24)):
        parts.append(box(f"tr{i}", (x0 + 0.08, yy - 0.025, zf - 0.08), (x1 - 0.08, yy + 0.025, zf - 0.02), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    for sx in (-1, 1):  # side glazing
        parts.append(box(f"sg{sx}", (sx * 0.96 - 0.005, 1.0, WALL_FACE + 0.05), (sx * 0.96 + 0.005, 2.86, zf - 0.08), "MI_WindowGlass"))
    return join("ENV_Gallery_Bay", parts)


@recipe("ENV_Shop_Fascia", "ORIGINAL")
def shop_fascia():
    """Blank painted fascia board over a shop opening (typography stays out of ENV): board + moulded frame."""
    parts = [
        box("board", (-0.92, 2.46, WALL_FACE), (0.92, 2.9, WALL_FACE + 0.05), "ENV_Sign_Board", bevel=0.01),
        box("capT", (-0.95, 2.88, WALL_FACE), (0.95, 2.93, WALL_FACE + 0.09), "MI_WoodTrim", uv="band", band=WOOD_LIGHT),
        box("capB", (-0.95, 2.43, WALL_FACE), (0.95, 2.47, WALL_FACE + 0.08), "MI_WoodTrim", uv="band", band=WOOD_LIGHT),
    ]
    return join("ENV_Shop_Fascia", parts)


@recipe("ENV_Sign_Bracket", "ORIGINAL")
def sign_bracket():
    """Projecting blade sign on a wrought-iron bracket, mounted at the left edge of a door bay (blank board)."""
    y = 3.05
    parts = [
        box("plate", (-0.05, y - 0.35, WALL_FACE), (0.05, y + 0.1, WALL_FACE + 0.03), "ENV_Metal_Iron"),
        box("arm", (-0.02, y, WALL_FACE), (0.02, y + 0.04, WALL_FACE + 0.85), "ENV_Metal_Iron"),
        box("strut", (-0.015, y - 0.3, WALL_FACE + 0.02), (0.015, y - 0.26, WALL_FACE + 0.4), "ENV_Metal_Iron"),
        box("board", (-0.025, y - 0.62, WALL_FACE + 0.22), (0.025, y - 0.08, WALL_FACE + 0.8), "ENV_Sign_Board", bevel=0.01),
        box("hookA", (-0.01, y - 0.08, WALL_FACE + 0.3), (0.01, y, WALL_FACE + 0.32), "ENV_Metal_Iron"),
        box("hookB", (-0.01, y - 0.08, WALL_FACE + 0.7), (0.01, y, WALL_FACE + 0.72), "ENV_Metal_Iron"),
    ]
    return join("ENV_Sign_Bracket", parts)


@recipe("ENV_Awning", "ORIGINAL")
def awning():
    """Fixed canvas shop awning (toldo) over a 2 m bay: sloped canvas, valance, iron arms. Canvas colour is a slot."""
    bm = bmesh.new()
    y_wall, y_front, zf = 2.72, 2.28, 1.05
    pts = [U(-0.95, y_wall, WALL_FACE), U(0.95, y_wall, WALL_FACE), U(0.95, y_front, zf), U(-0.95, y_front, zf)]
    vs = [bm.verts.new(p) for p in pts]
    bm.faces.new(vs)
    ob = new_object("canvas", bm)
    ob.data.materials.append(material("ENV_Canvas_Green"))
    sol = ob.modifiers.new("t", "SOLIDIFY")
    sol.thickness = 0.02
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier="t")
    uv_box(ob)
    parts = [ob, box("valance", (-0.95, y_front - 0.22, zf - 0.01), (0.95, y_front, zf + 0.01), "ENV_Canvas_Green")]
    for sx in (-1, 1):
        parts.append(box(f"arm{sx}", (sx * 0.9 - 0.015, 2.1, WALL_FACE), (sx * 0.9 + 0.015, 2.13, zf - 0.02), "ENV_Metal_Iron"))
    return join("ENV_Awning", parts)


@recipe("ENV_Downpipe", "ORIGINAL")
def downpipe():
    """Rain-water downpipe, 3 m per unit height (assembler scales y by storeys), with shoe and wall clips."""
    parts = [cylinder("pipe", (0, 1.5, 0.0), 0.045, 3.0, "ENV_Metal_Downpipe", segments=8)]
    parts.append(box("shoe", (-0.05, 0.0, -0.05), (0.05, 0.12, 0.12), "ENV_Metal_Downpipe"))
    for y in (0.9, 2.1):
        parts.append(box(f"clip{y}", (-0.06, y, -0.12), (0.06, y + 0.04, 0.02), "ENV_Metal_Iron"))
    return join("ENV_Downpipe", parts)


# ---------------------------------------------------------------- recipes: ground, elevation, waterfront

@recipe("ENV_Kerb_2m", "CREATE_DERIVED")
def kerb():
    """Granite kerb 2 m x 0.28 m, top at +0.15 (pavement datum); kit MI_RockTrim slab band."""
    return join("ENV_Kerb_2m", [box("kerb", (-1.0, -0.25, -0.14), (1.0, 0.15, 0.14), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.015)])


@recipe("ENV_Kerb_Corner", "CREATE_DERIVED")
def kerb_corner():
    """Quarter-round kerb corner (radius 1 m) joining two ENV_Kerb_2m runs; kit MI_RockTrim slab band."""
    bm = bmesh.new()
    seg, r0, r1 = 8, 0.86, 1.14
    ring_in, ring_out = [], []
    for i in range(seg + 1):
        a = math.radians(90 * i / seg)
        ring_in.append((r0 * math.cos(a), r0 * math.sin(a)))
        ring_out.append((r1 * math.cos(a), r1 * math.sin(a)))
    def v(x, z, y):
        return bm.verts.new(U(x - 1.0, y, z - 1.0))
    for i in range(seg):
        for (y0, y1) in [(-0.25, 0.15)]:
            a0, a1, b0, b1 = ring_in[i], ring_in[i + 1], ring_out[i], ring_out[i + 1]
            top = [v(a0[0], a0[1], y1), v(b0[0], b0[1], y1), v(b1[0], b1[1], y1), v(a1[0], a1[1], y1)]
            bm.faces.new(top)
            bm.faces.new([v(b0[0], b0[1], y0), v(b1[0], b1[1], y0), v(b1[0], b1[1], y1), v(b0[0], b0[1], y1)])
            bm.faces.new([v(a0[0], a0[1], y0), v(a0[0], a0[1], y1), v(a1[0], a1[1], y1), v(a1[0], a1[1], y0)])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object("ENV_Kerb_Corner", bm)
    ob.data.materials.append(material("MI_RockTrim"))
    uv_band(ob, ROCK_SLAB)
    return ob


@recipe("ENV_Gutter_Channel_2m", "CREATE_DERIVED")
def gutter_channel():
    """Central drainage channel for pedestrian streets: two sloped granite slabs forming a shallow V (0.6 m)."""
    parts = [
        box("l", (-1.0, -0.06, -0.3), (1.0, 0.0, -0.02), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.008),
        box("r", (-1.0, -0.06, 0.02), (1.0, 0.0, 0.3), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.008),
        box("c", (-1.0, -0.08, -0.02), (1.0, -0.03, 0.02), "MI_RockTrim", uv="band", band=ROCK_SLAB),
    ]
    return join("ENV_Gutter_Channel_2m", parts)


def _masonry_wall(name, length, height, thick, coping=True):
    """Rubble retaining/quay wall block: kit MI_UnevenBrick face (tiled at kit density) + ashlar coping course.
    Top of coping at y = 0; wall runs along x, street/water face at +z."""
    parts = [box("body", (-length / 2, -height, -thick), (length / 2, -0.3 if coping else 0.0, 0.0), "MI_UnevenBrick", uv="box")]
    if coping:
        parts.append(box("coping", (-length / 2, -0.3, -thick - 0.05), (length / 2, 0.0, 0.1), "MI_RockTrim", uv="band", band=ROCK_ASHLAR, bevel=0.02))
    return join(name, parts)


@recipe("ENV_Quay_Wall_4m", "CREATE_DERIVED")
def quay_wall():
    """Public quay edge block 4 m long, 3.2 m face down to below water; rubble face + granite coping at y = 0."""
    return _masonry_wall("ENV_Quay_Wall_4m", 4.0, 3.2, 1.2)


@recipe("ENV_Retaining_Wall_2x1", "CREATE_DERIVED")
def retaining_1():
    """Retaining wall 2 m long, 1 m face, coping on top (upper datum at y = 0, lower street at -1)."""
    return _masonry_wall("ENV_Retaining_Wall_2x1", 2.0, 1.0, 0.6)


@recipe("ENV_Retaining_Wall_2x2", "CREATE_DERIVED")
def retaining_2():
    """Retaining wall 2 m long, 2 m face, coping on top."""
    return _masonry_wall("ENV_Retaining_Wall_2x2", 2.0, 2.0, 0.7)


@recipe("ENV_Retaining_Wall_2x3", "CREATE_DERIVED")
def retaining_3():
    """Retaining wall 2 m long, 3 m face (one storey), coping on top."""
    return _masonry_wall("ENV_Retaining_Wall_2x3", 2.0, 3.0, 0.8)


@recipe("ENV_Bollard_Mooring", "ORIGINAL")
def bollard():
    """Cast-iron mooring bollard (noray) for the quay coping: base plate, waisted body, mushroom cap."""
    parts = [
        cylinder("base", (0, 0.03, 0), 0.3, 0.06, "ENV_Metal_Iron", segments=14),
        cylinder("body", (0, 0.3, 0), 0.17, 0.5, "ENV_Metal_Iron", segments=14),
        cylinder("neck", (0, 0.58, 0), 0.14, 0.08, "ENV_Metal_Iron", segments=14),
        cylinder("cap", (0, 0.66, 0), 0.25, 0.1, "ENV_Metal_Iron", segments=14),
    ]
    return join("ENV_Bollard_Mooring", parts)


@recipe("ENV_Quay_Ladder", "ORIGINAL")
def quay_ladder():
    """Iron ladder fixed to the quay face (top at the coping, 3 m down)."""
    parts = []
    for sx in (-0.22, 0.22):
        parts.append(box(f"rail{sx}", (sx - 0.02, -3.0, 0.1), (sx + 0.02, 0.9, 0.14), "ENV_Metal_Iron"))
        parts.append(box(f"hook{sx}", (sx - 0.02, 0.86, -0.25), (sx + 0.02, 0.9, 0.14), "ENV_Metal_Iron"))
    y = -2.8
    while y < 0.0:
        parts.append(box(f"rung{y:.2f}", (-0.22, y, 0.11), (0.22, y + 0.03, 0.13), "ENV_Metal_Iron"))
        y += 0.3
    return join("ENV_Quay_Ladder", parts)


@recipe("ENV_Railing_Quay_2m", "ORIGINAL")
def railing_quay():
    """Public waterfront guard rail, 2 m, 1.05 m high: tube posts + three rails (painted iron)."""
    parts = []
    for sx in (-1.0, 1.0):
        parts.append(cylinder(f"post{sx}", (sx * 0.98, 0.53, 0), 0.03, 1.06, "ENV_Metal_Iron", segments=8))
    for y in (0.35, 0.7, 1.03):
        parts.append(cylinder(f"rail{y}", (0, y, 0), 0.022 if y < 1 else 0.03, 2.0, "ENV_Metal_Iron", segments=8, axis="x"))
    return join("ENV_Railing_Quay_2m", parts)


@recipe("ENV_Fence_Yard_2m", "ORIGINAL")
def fence_yard():
    """Controlled work-yard boundary, 2 m panel x 2.1 m: galvanised palisade on a low plinth. Distinct from the
    public quay railing by height, material and permeability (you see through, you cannot pass)."""
    parts = [box("plinth", (-1.0, 0.0, -0.12), (1.0, 0.25, 0.12), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.01)]
    for sx in (-0.98, 0.98):
        parts.append(box(f"post{sx}", (sx - 0.04, 0.0, -0.04), (sx + 0.04, 2.1, 0.04), "ENV_Metal_Galvanised"))
    for y in (0.5, 1.8):
        parts.append(box(f"rail{y}", (-1.0, y, 0.04), (1.0, y + 0.05, 0.07), "ENV_Metal_Galvanised"))
    x = -0.9
    i = 0
    while x < 0.95:
        parts.append(box(f"pale{i}", (x - 0.02, 0.25, 0.07), (x + 0.02, 2.05, 0.09), "ENV_Metal_Galvanised"))
        x += 0.12
        i += 1
    return join("ENV_Fence_Yard_2m", parts)


@recipe("ENV_Water_Plane_20m", "ORIGINAL")
def water_plane():
    """Port water surface tile 20 x 20 m (y = 0 is the water level; place it below the quay coping)."""
    return join("ENV_Water_Plane_20m", [box("water", (-10, -0.02, -10), (10, 0.0, 10), "ENV_Water_Port")])


# ---------------------------------------------------------------- recipes: port / market / street props

@recipe("ENV_Crate_Fish", "ORIGINAL")
def crate_fish():
    """Stackable plastic fish crate (0.6 x 0.4 x 0.22 m) with hand holes; colour is a material slot."""
    parts = [
        box("bottom", (-0.3, 0.0, -0.2), (0.3, 0.03, 0.2), "ENV_Plastic_Blue"),
        box("wf", (-0.3, 0.0, 0.17), (0.3, 0.22, 0.2), "ENV_Plastic_Blue", bevel=0.008),
        box("wb", (-0.3, 0.0, -0.2), (0.3, 0.22, -0.17), "ENV_Plastic_Blue", bevel=0.008),
        box("wl", (-0.3, 0.0, -0.17), (-0.27, 0.22, 0.17), "ENV_Plastic_Blue", bevel=0.008),
        box("wr", (0.27, 0.0, -0.17), (0.3, 0.22, 0.17), "ENV_Plastic_Blue", bevel=0.008),
        box("ice", (-0.27, 0.03, -0.17), (0.27, 0.15, 0.17), "ENV_Sign_Board"),
    ]
    return join("ENV_Crate_Fish", parts)


@recipe("ENV_Pallet", "CREATE_DERIVED")
def pallet():
    """Euro pallet 1.2 x 0.8 x 0.14 m; kit MI_WoodTrim dark plank band."""
    parts = []
    for i in range(7):
        x = -0.6 + 0.0725 + i * (1.2 - 0.145) / 6
        parts.append(box(f"top{i}", (x - 0.05, 0.12, -0.4), (x + 0.05, 0.14, 0.4), "MI_WoodTrim", uv="band", band=WOOD_DARK))
    for z in (-0.35, 0.0, 0.35):
        parts.append(box(f"blk{z}", (-0.6, 0.02, z - 0.05), (0.6, 0.12, z + 0.05), "MI_WoodTrim", uv="band", band=WOOD_DARK))
        parts.append(box(f"bot{z}", (-0.6, 0.0, z - 0.06), (0.6, 0.02, z + 0.06), "MI_WoodTrim", uv="band", band=WOOD_DARK))
    return join("ENV_Pallet", parts)


@recipe("ENV_Counter_Shop", "CREATE_DERIVED")
def counter_shop():
    """Shop counter 1.8 x 0.6 x 0.95 m: painted timber front panels, stone-slab top."""
    parts = [
        box("body", (-0.9, 0.0, -0.3), (0.9, 0.9, 0.3), "MI_WoodTrim", uv="band", band=WOOD_LIGHT, bevel=0.01),
        box("top", (-0.95, 0.9, -0.34), (0.95, 0.96, 0.34), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.01),
        box("kick", (-0.88, 0.0, 0.26), (0.88, 0.1, 0.31), "MI_WoodTrim", uv="band", band=WOOD_DARK),
    ]
    for i, x in enumerate((-0.6, 0.0, 0.6)):
        parts.append(box(f"pan{i}", (x - 0.26, 0.18, 0.3), (x + 0.26, 0.8, 0.32), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    return join("ENV_Counter_Shop", parts)


@recipe("ENV_Bin_Street", "ORIGINAL")
def bin_street():
    """Wall/post-mounted galvanised litter bin (papelera) on a short post."""
    parts = [
        cylinder("post", (0, 0.45, 0), 0.03, 0.9, "ENV_Metal_Iron", segments=8),
        cylinder("bin", (0, 0.75, 0.18), 0.17, 0.45, "ENV_Metal_Galvanised", segments=12),
        box("strap", (-0.03, 0.8, 0.0), (0.03, 0.86, 0.05), "ENV_Metal_Iron"),
    ]
    return join("ENV_Bin_Street", parts)


@recipe("ENV_Bollard_Street", "ORIGINAL")
def bollard_street():
    """Cast-iron street bollard (pilona) 0.9 m, used to protect thresholds and pedestrian edges."""
    parts = [
        cylinder("body", (0, 0.42, 0), 0.08, 0.84, "ENV_Metal_Iron", segments=12),
        sphere("cap", (0, 0.88, 0), 0.09, "ENV_Metal_Iron", segments=12),
        cylinder("ring", (0, 0.7, 0), 0.095, 0.04, "ENV_Metal_Iron", segments=12),
    ]
    return join("ENV_Bollard_Street", parts)


# ---------------------------------------------------------------- helpers for street life / vehicles / port

def tube(name, a, b, radius, mat, segments=8):
    """Cylinder between two Unity-frame points."""
    va, vb = U(*a), U(*b)
    d = vb - va
    length = max(d.length, 1e-4)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=radius, radius2=radius, depth=length)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    ob.location = (va + vb) / 2
    apply_transform(ob)
    uv_box(ob)
    return ob


def frustum(name, base, r0, r1, height, mat, segments=12):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=r0, radius2=r1, depth=height)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    ob.location = U(base[0], base[1] + height / 2, base[2])
    apply_transform(ob)
    uv_box(ob)
    return ob


def torus(name, center, major, minor, mat, axis="x", segments=20):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    rot = (0, math.radians(90), 0) if axis == "x" else ((math.radians(90), 0, 0) if axis == "z" else (0, 0, 0))
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=segments, minor_segments=6,
                                     location=U(*center), rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(material(mat))
    apply_transform(ob)
    uv_box(ob)
    return ob


def lump(name, center, size, mat, seed=1, rough=0.18):
    """Irregular soft blob (bags, nets, piles): displaced icosphere, deterministic by seed."""
    import random
    rnd = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    for v in bm.verts:
        k = 1.0 + rnd.uniform(-rough, rough)
        v.co = Vector((v.co.x * size[0] * k, v.co.y * size[2] * k, v.co.z * size[1] * k))
        if v.co.z < -size[1] * 0.55:
            v.co.z = -size[1] * 0.55  # flat-ish bottom
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    ob.location = U(center[0], center[1] + size[1] * 0.55, center[2])
    apply_transform(ob)
    uv_box(ob)
    return ob


def flat_poly(name, pts_xz, y, mat):
    bm = bmesh.new()
    bm.faces.new([bm.verts.new(U(x, y, z)) for x, z in pts_xz])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    for p in ob.data.polygons:  # face up
        if p.normal.z < 0:
            p.flip()
    uv_box(ob)
    return ob


def loft(name, sections, mat):
    """Closed loft through cross-sections: list of (z, [(x, y), ...]) with equal point counts (Unity frame)."""
    bm = bmesh.new()
    rings = [[bm.verts.new(U(x, y, z)) for x, y in pts] for z, pts in sections]
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            bm.faces.new([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]])
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    uv_box(ob)
    return ob


# ---------------------------------------------------------------- recipes: ground details and junctions

@recipe("ENV_Plinth_2m", "CREATE_DERIVED")
def plinth():
    """Ashlar plinth band (zócalo) 2 m x 0.42 m standing 6 cm proud of the wall face: hides the wall/pavement seam
    and ties ground floors of different buildings together. Kit MI_RockTrim ashlar band."""
    return join("ENV_Plinth_2m", [box("p", (-1.0, -0.02, 0.07), (1.0, 0.42, 0.16), "MI_RockTrim", uv="band", band=ROCK_ASHLAR, bevel=0.015)])


@recipe("ENV_Plinth_Pier", "CREATE_DERIVED")
def plinth_pier():
    """Plinth stub for the pier beside a door/shop opening (0.2 m, scaled in x by the assembler)."""
    return join("ENV_Plinth_Pier", [box("p", (-0.1, -0.02, 0.07), (0.1, 0.42, 0.16), "MI_RockTrim", uv="band", band=ROCK_ASHLAR, bevel=0.01)])


@recipe("ENV_Drain_Grate", "ORIGINAL")
def drain_grate():
    """Cast-iron gutter grate set in the carriageway beside the kerb."""
    parts = [box("frame", (-0.32, -0.02, -0.2), (0.32, 0.012, 0.2), "ENV_Metal_Iron")]
    for i in range(7):
        x = -0.27 + i * 0.09
        parts.append(box(f"bar{i}", (x - 0.018, 0.012, -0.17), (x + 0.018, 0.02, 0.17), "ENV_Metal_Iron"))
    return join("ENV_Drain_Grate", parts)


@recipe("ENV_Manhole", "ORIGINAL")
def manhole():
    """Round cast-iron manhole cover flush with the paving."""
    return join("ENV_Manhole", [cylinder("disc", (0, 0.004, 0), 0.36, 0.02, "ENV_Metal_Iron", segments=20),
                                cylinder("ring", (0, 0.002, 0), 0.42, 0.018, "MI_RockTrim", segments=20, band=ROCK_SLAB)])


def _puddle(name, seed, r):
    import random
    rnd = random.Random(seed)
    pts = []
    for i in range(14):
        a = 2 * math.pi * i / 14
        k = r * (1 + rnd.uniform(-0.35, 0.25))
        pts.append((math.cos(a) * k * 1.4, math.sin(a) * k))
    return flat_poly(name, pts, 0.006, "ENV_Water_Puddle")


@recipe("ENV_Puddle_A", "ORIGINAL")
def puddle_a():
    """Irregular rain puddle (flat, glossy), about 1.6 x 1.1 m."""
    return join("ENV_Puddle_A", [_puddle("p", 3, 0.55)])


@recipe("ENV_Puddle_B", "ORIGINAL")
def puddle_b():
    """Irregular rain puddle, about 1.0 x 0.7 m."""
    return join("ENV_Puddle_B", [_puddle("p", 11, 0.35)])


@recipe("ENV_Tree_Pit", "ORIGINAL")
def tree_pit():
    """Square iron tree-pit grate (alcorque) 1.3 m with a trunk hole."""
    parts = [box("frame", (-0.65, -0.01, -0.65), (0.65, 0.02, -0.57), "ENV_Metal_Iron"),
             box("frame2", (-0.65, -0.01, 0.57), (0.65, 0.02, 0.65), "ENV_Metal_Iron"),
             box("frame3", (-0.65, -0.01, -0.57), (-0.57, 0.02, 0.57), "ENV_Metal_Iron"),
             box("frame4", (0.57, -0.01, -0.57), (0.65, 0.02, 0.57), "ENV_Metal_Iron")]
    for i in range(6):
        x = -0.5 + i * 0.2
        if abs(x) < 0.2:
            continue
        parts.append(box(f"bar{i}", (x - 0.02, 0.0, -0.57), (x + 0.02, 0.018, 0.57), "ENV_Metal_Iron"))
    return join("ENV_Tree_Pit", parts)


@recipe("ENV_Corner_Column", "ORIGINAL")
def corner_column():
    """Cast-iron corner column (3 m) carrying the corner above a chamfered ground-floor entrance."""
    parts = [cylinder("base", (0, 0.15, 0), 0.16, 0.3, "ENV_Metal_Iron", segments=12),
             cylinder("shaft", (0, 1.6, 0), 0.1, 2.6, "ENV_Metal_Iron", segments=12),
             cylinder("capital", (0, 2.95, 0), 0.2, 0.1, "ENV_Metal_Iron", segments=12),
             cylinder("neck", (0, 2.82, 0), 0.13, 0.12, "ENV_Metal_Iron", segments=12)]
    return join("ENV_Corner_Column", parts)


# ---------------------------------------------------------------- recipes: street life

@recipe("ENV_Lamp_Post", "ORIGINAL")
def lamp_post():
    """Late-20th-century cast-iron street lamp (farola), 4 m, lantern on a short arm towards +z."""
    parts = [cylinder("base", (0, 0.2, 0), 0.13, 0.4, "ENV_Metal_Iron", segments=10),
             cylinder("post", (0, 2.0, 0), 0.055, 3.3, "ENV_Metal_Iron", segments=8),
             tube("arm", (0, 3.5, 0), (0, 3.62, 0.45), 0.025, "ENV_Metal_Iron"),
             box("lantern", (-0.14, 3.2, 0.33), (0.14, 3.55, 0.61), "ENV_Lamp_Glass"),
             frustum("cap", (0, 3.55, 0.47), 0.22, 0.03, 0.18, "ENV_Metal_Iron", segments=4)]
    return join("ENV_Lamp_Post", parts)


@recipe("ENV_Sign_NoEntry", "ORIGINAL")
def sign_no_entry():
    """Generic no-entry traffic sign on a galvanised post (disc facing +z)."""
    parts = [cylinder("post", (0, 1.3, 0), 0.03, 2.6, "ENV_Metal_Galvanised", segments=8),
             cylinder("disc", (0, 2.35, 0.05), 0.3, 0.02, "ENV_Sign_Red", segments=20, axis="z"),
             box("bar", (-0.2, 2.3, 0.061), (0.2, 2.4, 0.066), "ENV_Sign_White")]
    return join("ENV_Sign_NoEntry", parts)


@recipe("ENV_Sign_Direction", "ORIGINAL")
def sign_direction():
    """Pedestrian direction post with two blank arrow plates (typography stays out of ENV)."""
    parts = [cylinder("post", (0, 1.4, 0), 0.035, 2.8, "ENV_Metal_Iron", segments=8)]
    for i, (y, sx) in enumerate(((2.45, 1), (2.15, -1))):
        parts.append(box(f"plate{i}", (0 if sx > 0 else -0.75, y - 0.1, -0.015), (0.75 if sx > 0 else 0, y + 0.1, 0.015), "ENV_Sign_Blue", bevel=0.005))
        parts.append(box(f"tip{i}", (0.75 if sx > 0 else -0.85, y - 0.06, -0.015), (0.85 if sx > 0 else -0.75, y + 0.06, 0.015), "ENV_Sign_Blue"))
    return join("ENV_Sign_Direction", parts)


@recipe("ENV_Street_Name_Plate", "ORIGINAL")
def street_name_plate():
    """Wall-mounted ceramic street-name plate (blank; the street name is content, not ENV)."""
    return join("ENV_Street_Name_Plate", [box("b", (-0.3, -0.13, 0.09), (0.3, 0.13, 0.12), "ENV_Sign_Blue", bevel=0.005),
                                          box("f", (-0.26, -0.09, 0.12), (0.26, 0.09, 0.125), "ENV_Sign_White")])


@recipe("ENV_Cafe_Table", "ORIGINAL")
def cafe_table():
    """Round aluminium bar-terrace table (0.7 m)."""
    return join("ENV_Cafe_Table", [cylinder("top", (0, 0.73, 0), 0.35, 0.03, "ENV_Metal_Galvanised", segments=16),
                                   cylinder("stem", (0, 0.37, 0), 0.03, 0.7, "ENV_Metal_Iron", segments=8),
                                   cylinder("foot", (0, 0.02, 0), 0.22, 0.04, "ENV_Metal_Iron", segments=12)])


@recipe("ENV_Cafe_Chair", "ORIGINAL")
def cafe_chair():
    """Aluminium terrace chair (faces +z)."""
    parts = [box("seat", (-0.21, 0.44, -0.2), (0.21, 0.47, 0.2), "ENV_Metal_Galvanised")]
    for sx in (-0.19, 0.19):
        for sz in (-0.18, 0.18):
            parts.append(tube(f"leg{sx}{sz}", (sx, 0.0, sz), (sx, 0.44, sz), 0.012, "ENV_Metal_Galvanised"))
        parts.append(tube(f"back{sx}", (sx, 0.47, -0.19), (sx, 0.85, -0.23), 0.012, "ENV_Metal_Galvanised"))
    for y in (0.62, 0.8):
        parts.append(box(f"slat{y}", (-0.2, y, -0.23 + (y - 0.47) * -0.1), (0.2, y + 0.05, -0.2 + (y - 0.47) * -0.1), "ENV_Metal_Galvanised"))
    return join("ENV_Cafe_Chair", parts)


@recipe("ENV_Parasol", "ORIGINAL")
def parasol():
    """Terrace parasol, 2.4 m canopy; canvas colour is a material slot (ENV_Canvas_Cream)."""
    return join("ENV_Parasol", [cylinder("pole", (0, 1.15, 0), 0.025, 2.3, "ENV_Metal_Galvanised", segments=8),
                                frustum("canopy", (0, 2.05, 0), 1.2, 0.05, 0.4, "ENV_Canvas_Cream", segments=8),
                                cylinder("base", (0, 0.04, 0), 0.25, 0.08, "ENV_Metal_Iron", segments=12)])


@recipe("ENV_Bicycle", "ORIGINAL")
def bicycle():
    """Ordinary town bicycle, 1.7 m, wheels in the y-z plane (length along z); frame paint slot ENV_Paint_Red."""
    r, rear, front = 0.33, -0.52, 0.52
    parts = [torus("wr", (0, r, rear), r, 0.022, "ENV_Rubber", axis="x"),
             torus("wf", (0, r, front), r, 0.022, "ENV_Rubber", axis="x")]
    bb, seat, head = (0, 0.3, -0.05), (0, 0.85, -0.2), (0, 0.9, 0.38)
    for a, b in ((bb, seat), (bb, head), (seat, head), (bb, (0, r, rear)), (seat, (0, r, rear)), (head, (0, r, front))):
        parts.append(tube("t", a, b, 0.018, "ENV_Paint_Red"))
    parts.append(box("saddle", (-0.07, 0.88, -0.3), (0.07, 0.93, -0.1), "ENV_Rubber"))
    parts.append(tube("stem", head, (0, 1.02, 0.34), 0.015, "ENV_Metal_Galvanised"))
    parts.append(tube("bar", (-0.28, 1.02, 0.34), (0.28, 1.02, 0.34), 0.014, "ENV_Metal_Galvanised"))
    parts.append(box("basket", (-0.17, 0.82, 0.48), (0.17, 1.0, 0.72), "ENV_Metal_Galvanised"))
    return join("ENV_Bicycle", parts)


@recipe("ENV_Clothesline", "ORIGINAL")
def clothesline():
    """Window clothesline (tendedero): two iron brackets 0.55 m out from the wall, two lines, hanging clothes
    in several colours. Mounted under an upper-floor window (origin on the wall face at bracket height)."""
    parts = []
    for sx in (-0.8, 0.8):
        parts.append(box(f"br{sx}", (sx - 0.02, -0.02, 0.09), (sx + 0.02, 0.02, 0.66), "ENV_Metal_Iron"))
    for z in (0.35, 0.6):
        parts.append(tube(f"line{z}", (-0.8, 0.0, z), (0.8, 0.0, z), 0.005, "ENV_Rope"))
    cloth = [(-0.65, 0.35, 0.34, 0.5, "ENV_Cloth_White"), (-0.25, 0.35, 0.3, 0.42, "ENV_Cloth_Blue"), (0.2, 0.35, 0.38, 0.6, "ENV_Cloth_Red"),
             (-0.45, 0.6, 0.4, 0.35, "ENV_Cloth_Yellow"), (0.1, 0.6, 0.28, 0.55, "ENV_Cloth_White"), (0.55, 0.6, 0.32, 0.4, "ENV_Cloth_Blue")]
    for i, (x, z, w, h, m) in enumerate(cloth):
        parts.append(box(f"c{i}", (x - w / 2, -h, z - 0.006), (x + w / 2, -0.01, z + 0.006), m))
    return join("ENV_Clothesline", parts)


@recipe("ENV_Planter_Pot", "ORIGINAL")
def planter_pot():
    """Terracotta planter pot (0.5 m) for doorsteps and balconies; plants are placed separately."""
    return join("ENV_Planter_Pot", [frustum("pot", (0, 0, 0), 0.18, 0.25, 0.42, "ENV_Terracotta", segments=12),
                                    cylinder("soil", (0, 0.4, 0), 0.22, 0.02, "ENV_Soil", segments=12)])


@recipe("ENV_Trash_Bags", "ORIGINAL")
def trash_bags():
    """Three tied rubbish bags left by a door or bin."""
    return join("ENV_Trash_Bags", [lump("a", (0, 0, 0), (0.28, 0.4, 0.25), "ENV_Plastic_Black", 1),
                                   lump("b", (0.42, 0, 0.1), (0.24, 0.33, 0.22), "ENV_Plastic_Black", 2),
                                   lump("c", (0.18, 0, 0.38), (0.22, 0.28, 0.2), "ENV_Plastic_Grey", 3)])


@recipe("ENV_Box_Cardboard", "ORIGINAL")
def box_cardboard():
    """Cardboard delivery box (0.5 x 0.4 x 0.35 m)."""
    return join("ENV_Box_Cardboard", [box("b", (-0.25, 0, -0.2), (0.25, 0.35, 0.2), "ENV_Cardboard", bevel=0.01),
                                      box("tape", (-0.03, 0.35, -0.2), (0.03, 0.352, 0.2), "ENV_Plastic_Grey")])


@recipe("ENV_Bench_Street", "CREATE_DERIVED")
def bench_street():
    """Municipal street bench: cast-iron ends, timber slats (kit MI_WoodTrim dark band), faces +z."""
    parts = []
    for sx in (-0.8, 0.8):
        parts.append(box(f"end{sx}", (sx - 0.04, 0, -0.25), (sx + 0.04, 0.42, 0.2), "ENV_Metal_Iron"))
        parts.append(box(f"back{sx}", (sx - 0.04, 0.42, -0.27), (sx + 0.04, 0.85, -0.2), "ENV_Metal_Iron"))
    for i, z in enumerate((-0.18, -0.06, 0.06, 0.16)):
        parts.append(box(f"s{i}", (-0.95, 0.42, z - 0.05), (0.95, 0.46, z + 0.05), "MI_WoodTrim", uv="band", band=WOOD_DARK))
    for i, y in enumerate((0.55, 0.7)):
        parts.append(box(f"b{i}", (-0.95, y, -0.26), (0.95, y + 0.1, -0.22), "MI_WoodTrim", uv="band", band=WOOD_DARK))
    return join("ENV_Bench_Street", parts)


@recipe("ENV_Phone_Booth", "ORIGINAL")
def phone_booth():
    """Late-1990s public phone cabin (generic, no branding): grey frame, glass sides, open front."""
    parts = [box("roof", (-0.5, 2.2, -0.45), (0.5, 2.35, 0.45), "ENV_Plastic_Grey", bevel=0.02),
             box("base", (-0.5, 0, -0.45), (0.5, 0.04, 0.45), "ENV_Plastic_Grey")]
    for sx in (-0.47, 0.47):
        for sz in (-0.42, 0.42):
            parts.append(box(f"p{sx}{sz}", (sx - 0.03, 0.04, sz - 0.03), (sx + 0.03, 2.2, sz + 0.03), "ENV_Plastic_Grey"))
    parts.append(box("gl", (-0.46, 0.5, -0.43), (-0.45, 2.1, 0.43), "ENV_Glass_Street"))
    parts.append(box("gr", (0.45, 0.5, -0.43), (0.46, 2.1, 0.43), "ENV_Glass_Street"))
    parts.append(box("gb", (-0.45, 0.5, -0.44), (0.45, 2.1, -0.43), "ENV_Glass_Street"))
    parts.append(box("phone", (-0.15, 1.1, -0.43), (0.15, 1.55, -0.33), "ENV_Metal_Galvanised"))
    return join("ENV_Phone_Booth", parts)


# ---------------------------------------------------------------- recipes: accumulated history

@recipe("ENV_Window_Blind", "ORIGINAL")
def window_blind():
    """Retro-fitted PVC roller blind (persiana enrollable) for the kit wide window: box over the head, slats
    lowered two thirds — the typical 1970s–90s replacement over older joinery."""
    parts = [box("box", (-0.82, 2.5, 0.09), (0.82, 2.74, 0.3), "ENV_Blind_PVC", bevel=0.01)]
    y = 1.55
    i = 0
    while y < 2.5:
        parts.append(box(f"s{i}", (-0.74, y, 0.2), (0.74, y + 0.045, 0.225), "ENV_Blind_PVC"))
        y += 0.05
        i += 1
    parts.append(box("guideL", (-0.8, 1.0, 0.18), (-0.76, 2.5, 0.24), "ENV_Blind_PVC"))
    parts.append(box("guideR", (0.76, 1.0, 0.18), (0.8, 2.5, 0.24), "ENV_Blind_PVC"))
    return join("ENV_Window_Blind", parts)


@recipe("ENV_Window_Boarded", "CREATE_DERIVED")
def window_boarded():
    """Boarded-up window for neglected buildings: rough planks across the kit wide window (MI_WoodTrim dark)."""
    parts = []
    for i, y in enumerate((1.05, 1.35, 1.7, 2.05)):
        tilt = (i % 2) * 0.04
        parts.append(box(f"p{i}", (-0.82, y + tilt, 0.12), (0.82, y + 0.22 - tilt, 0.16), "MI_WoodTrim", uv="band", band=WOOD_DARK))
    return join("ENV_Window_Boarded", parts)


@recipe("ENV_Sat_Dish", "ORIGINAL")
def sat_dish():
    """Satellite dish on a wall bracket (late-1990s addition), facing +z and up."""
    dish = frustum("dish", (0, 0, 0), 0.06, 0.4, 0.14, "ENV_Sign_White", segments=16)
    dish.rotation_euler = (math.radians(-60), 0, 0)
    dish.location = U(0, 0.25, 0.35)
    apply_transform(dish)
    parts = [dish, tube("arm", (0, 0.1, 0.09), (0, 0.2, 0.35), 0.02, "ENV_Metal_Galvanised"),
             tube("feed", (0, 0.25, 0.35), (0, 0.5, 0.65), 0.012, "ENV_Metal_Galvanised"),
             box("plate", (-0.08, 0.02, 0.09), (0.08, 0.2, 0.11), "ENV_Metal_Galvanised")]
    return join("ENV_Sat_Dish", parts)


@recipe("ENV_TV_Aerial", "ORIGINAL")
def tv_aerial():
    """Rooftop TV aerial: 2.2 m mast with a Yagi boom and elements."""
    parts = [tube("mast", (0, 0, 0), (0, 2.2, 0), 0.02, "ENV_Metal_Galvanised"),
             tube("boom", (0, 2.1, -0.6), (0, 2.1, 0.6), 0.012, "ENV_Metal_Galvanised")]
    for i in range(7):
        z = -0.55 + i * 0.18
        w = 0.4 - i * 0.03
        parts.append(tube(f"e{i}", (-w, 2.1, z), (w, 2.1, z), 0.006, "ENV_Metal_Galvanised"))
    return join("ENV_TV_Aerial", parts)


@recipe("ENV_Utility_Box", "ORIGINAL")
def utility_box():
    """Electricity/gas meter cabinet fixed on a ground-floor facade (grey plastic)."""
    return join("ENV_Utility_Box", [box("b", (-0.3, 0.6, 0.09), (0.3, 1.4, 0.3), "ENV_Plastic_Grey", bevel=0.015),
                                    box("d", (-0.26, 0.64, 0.3), (0.26, 1.36, 0.305), "ENV_Plastic_Grey"),
                                    box("pipe", (-0.02, 0.0, 0.12), (0.02, 0.6, 0.16), "ENV_Plastic_Grey")])


@recipe("ENV_Cable_Run_2m", "ORIGINAL")
def cable_run():
    """Surface-fixed service cable (2 m along the facade) with clips — added long after the building."""
    parts = [tube("c", (-1.0, 0, 0.11), (1.0, -0.03, 0.11), 0.009, "ENV_Rubber")]
    for x in (-0.6, 0.2, 0.9):
        parts.append(box(f"k{x}", (x - 0.015, -0.03, 0.09), (x + 0.015, 0.02, 0.125), "ENV_Plastic_Grey"))
    return join("ENV_Cable_Run_2m", parts)


@recipe("ENV_Door_Portal_Reformed", "ORIGINAL")
def door_portal_reformed():
    """1980s replacement portal door for the kit Door_Flat opening: bronze-anodised aluminium frame, wired glass,
    push bar. Joinery slot is palette-remapped like painted timber."""
    x0, x1, h = -0.64, 0.64, 2.14
    parts = [box("fl", (x0, 0, -0.1), (x0 + 0.07, h, 0.0), "ENV_Alu_Bronze"),
             box("fr", (x1 - 0.07, 0, -0.1), (x1, h, 0.0), "ENV_Alu_Bronze"),
             box("ft", (x0, h - 0.07, -0.1), (x1, h, 0.0), "ENV_Alu_Bronze"),
             box("mid", (-0.02, 0, -0.08), (0.02, h, -0.02), "ENV_Alu_Bronze"),
             box("kick", (x0 + 0.07, 0.02, -0.07), (x1 - 0.07, 0.35, -0.04), "ENV_Alu_Bronze"),
             box("glass", (x0 + 0.07, 0.35, -0.06), (x1 - 0.07, h - 0.07, -0.05), "ENV_Glass_Street"),
             box("push", (-0.5, 1.0, -0.03), (-0.1, 1.04, 0.01), "ENV_Metal_Galvanised")]
    return join("ENV_Door_Portal_Reformed", parts)


# ---------------------------------------------------------------- recipes: vehicles

def _wheels(xs, zs, r, w):
    parts = []
    for x in xs:
        for z in zs:
            parts.append(cylinder(f"w{x}{z}", (x, r, z), r, w, "ENV_Rubber", segments=14, axis="x"))
            parts.append(cylinder(f"h{x}{z}", (x + (0.01 if x > 0 else -0.01), r, z), r * 0.55, w + 0.02, "ENV_Metal_Galvanised", segments=10, axis="x"))
    return parts


@recipe("ENV_Vehicle_Van", "ORIGINAL")
def vehicle_van():
    """Small 1990s delivery van (generic, no branding), 4.1 m, front towards +z. Body paint slot ENV_Paint_White."""
    body = loft("body", [
        (-2.0, [(-0.8, 0.35), (0.8, 0.35), (0.8, 1.85), (-0.8, 1.85)]),
        (0.6, [(-0.8, 0.35), (0.8, 0.35), (0.8, 1.85), (-0.8, 1.85)]),
        (1.35, [(-0.78, 0.35), (0.78, 0.35), (0.78, 1.25), (-0.78, 1.25)]),
        (2.05, [(-0.75, 0.35), (0.75, 0.35), (0.75, 0.95), (-0.75, 0.95)]),
    ], "ENV_Paint_White")
    parts = [body,
             box("ws", (-0.72, 1.2, 0.62), (0.72, 1.78, 0.66), "ENV_Glass_Street"),
             box("sw", (-0.81, 1.15, 0.0), (0.81, 1.6, 0.58), "ENV_Glass_Street"),
             box("bf", (-0.82, 0.3, 2.0), (0.82, 0.5, 2.12), "ENV_Plastic_Grey"),
             box("br", (-0.82, 0.3, -2.1), (0.82, 0.5, -1.98), "ENV_Plastic_Grey"),
             box("ll", (-0.7, 0.75, 2.04), (-0.4, 0.88, 2.07), "ENV_Lamp_Glass"),
             box("lr", (0.4, 0.75, 2.04), (0.7, 0.88, 2.07), "ENV_Lamp_Glass"),
             box("rd", (-0.02, 0.45, -2.02), (0.02, 1.8, -1.99), "ENV_Plastic_Grey")]
    parts += _wheels((-0.72, 0.72), (-1.35, 1.35), 0.31, 0.2)
    return join("ENV_Vehicle_Van", parts)


@recipe("ENV_Vehicle_Car", "ORIGINAL")
def vehicle_car():
    """Small 1990s hatchback (generic), 3.7 m, front towards +z. Body paint slot ENV_Paint_Red."""
    body = loft("body", [
        (-1.85, [(-0.78, 0.3), (0.78, 0.3), (0.78, 0.95), (-0.78, 0.95)]),
        (1.85, [(-0.78, 0.3), (0.78, 0.3), (0.78, 0.8), (-0.78, 0.8)]),
    ], "ENV_Paint_Red")
    cabin = loft("cabin", [
        (-1.7, [(-0.74, 0.95), (0.74, 0.95), (0.68, 1.3), (-0.68, 1.3)]),
        (-1.45, [(-0.74, 0.95), (0.74, 0.95), (0.66, 1.42), (-0.66, 1.42)]),
        (0.35, [(-0.74, 0.9), (0.74, 0.9), (0.66, 1.42), (-0.66, 1.42)]),
        (0.95, [(-0.76, 0.84), (0.76, 0.84), (0.7, 0.95), (-0.7, 0.95)]),
    ], "ENV_Glass_Street")
    parts = [body, cabin,
             box("roof", (-0.64, 1.4, -1.4), (0.64, 1.45, 0.3), "ENV_Paint_Red"),
             box("bf", (-0.8, 0.28, 1.8), (0.8, 0.45, 1.92), "ENV_Plastic_Grey"),
             box("br", (-0.8, 0.28, -1.92), (0.8, 0.45, -1.8), "ENV_Plastic_Grey"),
             box("ll", (-0.68, 0.62, 1.85), (-0.4, 0.74, 1.87), "ENV_Lamp_Glass"),
             box("lr", (0.4, 0.62, 1.85), (0.68, 0.74, 1.87), "ENV_Lamp_Glass")]
    parts += _wheels((-0.7, 0.7), (-1.2, 1.2), 0.29, 0.18)
    return join("ENV_Vehicle_Car", parts)


# ---------------------------------------------------------------- recipes: working port

@recipe("ENV_Boat_Small", "ORIGINAL")
def boat_small():
    """Small inshore fishing boat (lancha), 5.6 m, bow towards +z, waterline at y = 0. Hull paint slot
    ENV_Paint_Blue with a white sheer strake and a small wheelhouse."""
    def sec(z, half, keel, sheer):
        return (z, [(0, keel), (half * 0.55, keel + 0.12), (half, 0.25), (half, sheer), (-half, sheer), (-half, 0.25), (-half * 0.55, keel + 0.12)])
    hull = loft("hull", [sec(-2.7, 0.8, -0.35, 0.75), sec(-1.5, 1.0, -0.5, 0.75), sec(0.6, 1.0, -0.55, 0.8),
                         sec(1.9, 0.7, -0.45, 0.9), sec(2.8, 0.06, -0.1, 1.05)], "ENV_Paint_Blue")
    strake = loft("strake", [(-2.7, [(-0.82, 0.62), (0.82, 0.62), (0.82, 0.8), (-0.82, 0.8)]),
                             (0.6, [(-1.02, 0.66), (1.02, 0.66), (1.02, 0.84), (-1.02, 0.84)]),
                             (1.9, [(-0.72, 0.76), (0.72, 0.76), (0.72, 0.94), (-0.72, 0.94)])], "ENV_Paint_White")
    parts = [hull, strake,
             box("deck", (-0.85, 0.55, -2.5), (0.85, 0.6, 2.0), "MI_WoodTrim", uv="band", band=WOOD_DARK),
             box("house", (-0.55, 0.6, -0.9), (0.55, 1.75, 0.3), "ENV_Paint_White", bevel=0.03),
             box("houseroof", (-0.62, 1.75, -1.0), (0.62, 1.82, 0.4), "ENV_Paint_Blue"),
             box("hwin", (-0.5, 1.25, 0.3), (0.5, 1.6, 0.32), "ENV_Glass_Street"),
             tube("mast", (0, 1.8, -0.3), (0, 3.6, -0.3), 0.04, "ENV_Metal_Galvanised")]
    return join("ENV_Boat_Small", parts)


@recipe("ENV_Buoy", "ORIGINAL")
def buoy():
    """Orange mooring/fishing buoy (floats on y = 0)."""
    return join("ENV_Buoy", [sphere("b", (0, 0.1, 0), 0.25, "ENV_Buoy_Orange", segments=12)])


@recipe("ENV_Lifebuoy_Post", "ORIGINAL")
def lifebuoy_post():
    """Quay lifebuoy on a post with a small cabinet."""
    return join("ENV_Lifebuoy_Post", [cylinder("post", (0, 0.8, 0), 0.04, 1.6, "ENV_Metal_Iron", segments=8),
                                      torus("ring", (0, 1.25, 0.08), 0.3, 0.06, "ENV_Buoy_Orange", axis="z"),
                                      box("hook", (-0.03, 1.5, 0.0), (0.03, 1.56, 0.1), "ENV_Metal_Iron")])


@recipe("ENV_Net_Pile", "ORIGINAL")
def net_pile():
    """Heap of fishing net with floats, about 1.4 m wide."""
    parts = [lump("net", (0, 0, 0), (0.7, 0.35, 0.55), "ENV_Net_Green", seed=5, rough=0.25),
             lump("net2", (0.5, 0, 0.35), (0.4, 0.25, 0.35), "ENV_Net_Green", seed=6, rough=0.25)]
    for i, (x, z) in enumerate(((-0.3, 0.4), (0.2, -0.45), (0.6, 0.1), (-0.55, -0.2))):
        parts.append(sphere(f"f{i}", (x, 0.45, z), 0.07, "ENV_Buoy_Orange", segments=8))
    return join("ENV_Net_Pile", parts)


@recipe("ENV_Quay_Steps", "CREATE_DERIVED")
def quay_steps():
    """Stone steps running down the quay face to the water (1.6 m drop, 1.2 m wide), outer side wall.
    Top step at y = 0 against the coping line (z = 0), descending towards +x."""
    parts = []
    n = 8
    for i in range(n):
        y = -0.2 * (i + 1)
        parts.append(box(f"st{i}", (i * 0.35, y, 0.1), (i * 0.35 + 0.37, y + 0.2, 1.3), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.01))
        parts.append(box(f"fill{i}", (i * 0.35, -3.2, 0.1), (i * 0.35 + 0.37, y, 1.3), "MI_UnevenBrick"))
    parts.append(box("cheek", (-0.05, -3.2, 1.3), (n * 0.35 + 0.1, 0.0, 1.55), "MI_UnevenBrick"))
    parts.append(box("cap", (-0.05, 0.0, 1.25), (n * 0.35 + 0.1, 0.12, 1.6), "MI_RockTrim", uv="band", band=ROCK_ASHLAR))
    return join("ENV_Quay_Steps", parts)


@recipe("ENV_Slipway", "CREATE_DERIVED")
def slipway():
    """Concrete slipway ramp 4 m wide, 7 m long, dropping 1.8 m into the water (+z), stone kerbs."""
    bm = bmesh.new()
    pts = [U(-2, 0, 0), U(2, 0, 0), U(2, -1.8, 7), U(-2, -1.8, 7)]
    bm.faces.new([bm.verts.new(p) for p in pts])
    ramp = new_object("ramp", bm)
    ramp.data.materials.append(material("ENV_Ground_Concrete"))
    sol = ramp.modifiers.new("t", "SOLIDIFY")
    sol.thickness = 0.3
    bpy.context.view_layer.objects.active = ramp
    bpy.ops.object.modifier_apply(modifier="t")
    uv_box(ramp)
    parts = [ramp]
    for sx in (-2.1, 2.1):
        k = loft(f"kerb{sx}", [(0, [(sx - 0.1, -0.3), (sx + 0.1, -0.3), (sx + 0.1, 0.1), (sx - 0.1, 0.1)]),
                               (7, [(sx - 0.1, -2.1), (sx + 0.1, -2.1), (sx + 0.1, -1.7), (sx - 0.1, -1.7)])], "MI_RockTrim")
        uv_band(k, ROCK_SLAB)
        parts.append(k)
    return join("ENV_Slipway", parts)


@recipe("ENV_Parapet_2m", "CREATE_DERIVED")
def parapet():
    """Low stone parapet (0.75 m) with granite coping — designed edge for overlooks and terraces."""
    return join("ENV_Parapet_2m", [box("body", (-1.0, 0, -0.2), (1.0, 0.62, 0.2), "MI_UnevenBrick"),
                                   box("cope", (-1.02, 0.62, -0.26), (1.02, 0.76, 0.26), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.02)])


@recipe("ENV_Parapet_Rail_2m", "CREATE_DERIVED")
def parapet_rail():
    """Stone upstand (0.45 m) with a painted iron rail above it — the public waterfront edge treatment."""
    parts = [box("body", (-1.0, 0, -0.18), (1.0, 0.36, 0.18), "MI_UnevenBrick"),
             box("cope", (-1.02, 0.36, -0.22), (1.02, 0.46, 0.22), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.015)]
    for x in (-0.95, 0.0, 0.95):
        parts.append(cylinder(f"post{x}", (x, 0.76, 0), 0.028, 0.6, "ENV_Metal_Iron", segments=8))
    parts.append(tube("rail", (-1.0, 1.06, 0), (1.0, 1.06, 0), 0.03, "ENV_Metal_Iron"))
    parts.append(tube("rail2", (-1.0, 0.78, 0), (1.0, 0.78, 0), 0.018, "ENV_Metal_Iron"))
    return join("ENV_Parapet_Rail_2m", parts)


@recipe("ENV_Mooring_Line", "ORIGINAL")
def mooring_line():
    """Unit mooring rope along +z (1 m); the assembler stretches it from bollard to boat."""
    return join("ENV_Mooring_Line", [tube("r", (0, 0, 0), (0, 0, 1), 0.02, "ENV_Rope")])


# ---------------------------------------------------------------- driver

def main(argv):
    global VAULT
    only = None
    if "--only" in argv:
        only = set(argv[argv.index("--only") + 1].split(","))
    if "--vault" in argv:
        VAULT = Path(argv[argv.index("--vault") + 1])
    if not (VAULT / DONOR_BLEND).is_file():
        raise SystemExit(f"ENV_DERIVE_ERROR donor source missing: {VAULT / DONOR_BLEND}")
    manifest_path = MANIFEST_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    done = []
    for name, fn in RECIPES.items():
        if only and name not in only:
            continue
        reset()
        ob = fn()
        ob.name = name
        export(ob, name)
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        mats = sorted({m.name for m in ob.data.materials if m})
        manifest[name] = {**MANIFEST[name], "materials": mats, "triangles": tris,
                          "donorSource": DONOR_BLEND if MANIFEST[name]["donors"] else None}
        done.append(f"{name} tris={tris} mats={','.join(mats)}")
    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), indent=2) + "\n", encoding="utf-8")
    for line in done:
        print("ENV_DERIVED", line)
    print(f"ENV_DERIVE_DONE {len(done)} -> {OUT}")


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
