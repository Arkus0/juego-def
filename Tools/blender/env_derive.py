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
ROCK_BLOCK = (0.64, 0.97)  # MI_RockTrim band: large dressed blocks (sillería; the lower band reads as brick once tinted)

# Lineage classes: DONOR = geometry copied from named kit modules (listed as donors); CREATE_DERIVED = new
# geometry textured with kit materials/trim sheets (material provenance is traced by Tools/env_catalog.py);
# ORIGINAL = new geometry with owned flat materials only.
RECIPES: dict[str, callable] = {}
MANIFEST: dict[str, dict] = {}
VAULT = DEFAULT_VAULT


SMOOTH: dict[str, float] = {}


def recipe(name, lineage, donors=(), method="", smooth=None):
    """smooth: auto-smooth angle in degrees. Curved and bevel-rounded props export with smooth normals below that
    angle (Quaternius look: soft, light-catching edges), hard edges above it stay crisp."""
    def wrap(fn):
        RECIPES[name] = fn
        MANIFEST[name] = {"class": lineage, "donors": list(donors), "method": method or (fn.__doc__ or "").strip()}
        if smooth:
            SMOOTH[name] = smooth
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
    bm = bmesh.new()
    top = OPEN_H - 0.28
    rows = []
    y = 0.0
    k = 0
    while y <= top + 1e-6:
        z = -0.03 + (0.012 if k % 2 else 0.0)
        rows.append((bm.verts.new(U(x0 + 0.04, y, z)), bm.verts.new(U(x1 - 0.04, y, z))))
        y += 0.0375
        k += 1
    for (a0, a1), (b0, b1) in zip(rows, rows[1:]):
        bm.faces.new([a0, a1, b1, b0])
    for f in bm.faces:
        f.normal_update()
        if f.normal.dot(Vector(U(0, 0, 1))) < 0:
            f.normal_flip()
    curtain = new_object("curtain", bm)
    curtain.data.materials.append(material("ENV_Metal_Shutter"))
    uv_box(curtain)
    parts.append(curtain)
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


def loft(name, sections, mat, cap_start=True, cap_end=True, hidden=()):
    """Loft through cross-sections: list of (z, [(x, y), ...]) with equal point counts (Unity frame). The loft is
    built closed (so normals resolve), then the start/end caps and the side columns listed in `hidden` (column i runs
    between section points i and i+1) are dropped where they face a wall or a board and never render."""
    bm = bmesh.new()
    rings = [[bm.verts.new(U(x, y, z)) for x, y in pts] for z, pts in sections]
    n = len(rings[0])
    drop = []
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            f = bm.faces.new([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]])
            if i in hidden:
                drop.append(f)
    f0 = bm.faces.new(rings[0][::-1])
    f1 = bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if not cap_start:
        drop.append(f0)
    if not cap_end:
        drop.append(f1)
    if drop:
        bmesh.ops.delete(bm, geom=drop, context="FACES_ONLY")
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    uv_box(ob)
    return ob


def rbox(name, lo, hi, mat, r=0.015, seg=2, uv="box", band=None):
    """Box with rounded (multi-segment) bevels: soft, light-catching edges in the Quaternius manner."""
    ob = box(name, lo, hi, mat, uv="none")
    if r > 0:
        do_bevel(ob, r, seg)
    if uv == "band":
        uv_band(ob, band)
    else:
        uv_box(ob)
    return ob


def beam(name, a, b, x0, x1, h, mat, r=0.01, seg=2, band=None):
    """Straight bar of rectangular section lying in a y-z plane from a = (y, z) to b = (y, z), spanning x0..x1 in x;
    h is the section depth across the bar. Bench and board frames, raked slats, ribs on tapered faces."""
    (ay, az), (by, bz) = a, b
    dy, dz = by - ay, bz - az
    L = math.hypot(dy, dz) or 1e-4
    py, pz = -dz / L * h / 2, dy / L * h / 2
    bm = bmesh.new()
    vs = {}
    for i, x in enumerate((x0, x1)):
        for j, (cy, cz) in enumerate(((ay, az), (by, bz))):
            for k, sg in enumerate((-1, 1)):
                vs[i, j, k] = bm.verts.new(U(x, cy + sg * py, cz + sg * pz))
    for f in (((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)), ((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)),
              ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1)),
              ((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)), ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1))):
        bm.faces.new([vs[t] for t in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    if r > 0:
        do_bevel(ob, r, seg)
    if band:
        uv_band(ob, band)
    else:
        uv_box(ob)
    return ob


def sweep(name, pts, radius, mat, segments=12, caps=True):
    """Tube swept along a Unity-frame polyline: one ring per point on the bisector, parallel-transported so it never
    twists — continuous bent tubes (bike hoops, chair frames, handles) with no gaps at the bends."""
    P = [U(*p) for p in pts]
    bm = bmesh.new()
    rings = []
    n1 = None
    for i, p in enumerate(P):
        if i == 0:
            t = P[1] - P[0]
        elif i == len(P) - 1:
            t = P[-1] - P[-2]
        else:
            t = (P[i + 1] - P[i]).normalized() + (P[i] - P[i - 1]).normalized()
        t.normalize()
        if n1 is None:
            ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            n1 = t.cross(ref).normalized()
        else:
            n1 = (n1 - t * n1.dot(t)).normalized()
        n2 = t.cross(n1).normalized()
        rings.append([bm.verts.new(p + (n1 * math.cos(2 * math.pi * j / segments) + n2 * math.sin(2 * math.pi * j / segments)) * radius)
                      for j in range(segments)])
    for a, b in zip(rings, rings[1:]):
        for j in range(segments):
            bm.faces.new([a[j], a[(j + 1) % segments], b[(j + 1) % segments], b[j]])
    if caps:
        bm.faces.new(rings[0][::-1])
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    uv_box(ob)
    return ob


def arc(cx, cy, r, a0, a1, n, z=0.0):
    """Points of a circular arc in the x-y plane at depth z (degrees, counter-clockwise)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)), z) for k in range(n + 1)]


def vloft(name, sections, mat, cap_bottom=True, cap_top=True):
    """Loft up through horizontal sections: [(y, [(x, z), ...]), ...] with equal point counts (bins, lids, bodies)."""
    bm = bmesh.new()
    rings = [[bm.verts.new(U(x, y, z)) for x, z in pts] for y, pts in sections]
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            bm.faces.new([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]])
    if cap_bottom:
        bm.faces.new(rings[0][::-1])
    if cap_top:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    uv_box(ob)
    return ob


def rrect(w, d, c, x=0.0, z=0.0):
    """Octagonal rounded-rectangle outline (half sizes w, d, corner cut c) for vloft sections."""
    return [(x - w + c, z - d), (x + w - c, z - d), (x + w, z - d + c), (x + w, z + d - c),
            (x + w - c, z + d), (x - w + c, z + d), (x - w, z + d - c), (x - w, z - d + c)]


def revolve_poly(name, profile, mat, n=8, rot=math.pi / 8, closed=False, band=None):
    """Closed surface of revolution on a regular n-gon (octagonal basins, piers): profile [(radius, y), ...]. With
    closed=True the last point joins the first (an annulus section such as a basin rim); otherwise ends at radius 0
    close to a point and others are capped. Faces follow the polygon's flats, so the corners stay crisp."""
    bm = bmesh.new()
    rings = []
    for r, y in profile:
        rings.append([bm.verts.new(U(r * math.cos(rot + 2 * math.pi * i / n), y, r * math.sin(rot + 2 * math.pi * i / n))) for i in range(n)])
    pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    for a, b in pairs:
        for i in range(n):
            bm.faces.new([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]])
    if not closed:
        if profile[0][0] > 1e-4:
            bm.faces.new(rings[0][::-1])
        if profile[-1][0] > 1e-4:
            bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    if band:
        uv_band(ob, band)
    else:
        uv_box(ob)
    return ob


def slab_xy(name, pts, z0, z1, mat, band=None, r=0.0):
    """A polygon drawn in the x-y plane (Unity frame, counter-clockwise) extruded from z0 to z1: pediments, crowns."""
    bm = bmesh.new()
    back = [bm.verts.new(U(x, y, z0)) for x, y in pts]
    front = [bm.verts.new(U(x, y, z1)) for x, y in pts]
    bm.faces.new(back[::-1])
    bm.faces.new(front)
    k = len(pts)
    for i in range(k):
        bm.faces.new([back[i], back[(i + 1) % k], front[(i + 1) % k], front[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    if r > 0:
        do_bevel(ob, r, 2)
    if band:
        uv_band(ob, band)
    else:
        uv_box(ob)
    return ob


def water_jet(name, tip, direction, reach, y_end, radius=0.022, steps=10):
    """A spout's stream: a parabola from the tip (Unity frame) along a horizontal direction, landing at y_end."""
    dx, dz = direction
    pts = [(tip[0] + dx * reach * t, tip[1] - (tip[1] - y_end) * t * t, tip[2] + dz * reach * t) for t in [k / steps for k in range(steps + 1)]]
    return sweep(name, pts, radius, "ENV_Water_Jet", segments=6)


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


@recipe("ENV_Manhole", "ORIGINAL", smooth=35)
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


@recipe("ENV_Cafe_Table", "ORIGINAL", smooth=40)
def cafe_table():
    """Round aluminium bar-terrace table (0.72 m): moulded top with a rolled edge, tube stem, heavy cast foot."""
    return join("ENV_Cafe_Table", [
        lathe("top", [(0.0, 0.715), (0.34, 0.715), (0.358, 0.724), (0.364, 0.742), (0.356, 0.758), (0.34, 0.764), (0.0, 0.764)], "ENV_PropMat_Alu", segments=24),
        lathe("stem", [(0.034, 0.05), (0.034, 0.69), (0.06, 0.705), (0.07, 0.716)], "ENV_PropMat_Alu", segments=14),
        lathe("foot", [(0.25, 0.0), (0.25, 0.02), (0.22, 0.035), (0.08, 0.06), (0.05, 0.075), (0.0, 0.075)], "ENV_PropMat_Negro", segments=20)])


@recipe("ENV_Cafe_Chair", "ORIGINAL", smooth=40)
def cafe_chair():
    """Aluminium bistro chair (faces +z): continuous tube frame — front legs, seat frame, rear legs running up into
    the raked back — slatted seat and two back slats, side stretchers."""
    A = "ENV_PropMat_Alu"
    r = 0.0145
    parts = []
    for sx in (-0.2, 0.2):
        parts.append(sweep(f"front{sx}", [(sx, 0.0, 0.2), (sx, 0.44, 0.185)], r, A))
        parts.append(sweep(f"rear{sx}", [(sx, 0.0, -0.21), (sx, 0.44, -0.19), (sx, 0.62, -0.215), (sx, 0.86, -0.255)], r, A))
        parts.append(sweep(f"str{sx}", [(sx, 0.16, 0.195), (sx, 0.16, -0.2)], 0.009, A, segments=8))
    parts.append(sweep("seatframe", [(-0.2, 0.445, 0.19), (0.2, 0.445, 0.19), (0.2, 0.445, -0.19), (-0.2, 0.445, -0.19), (-0.2, 0.445, 0.19)], 0.011, A, segments=8))
    for i in range(5):
        z = 0.155 - i * 0.078
        parts.append(rbox(f"slat{i}", (-0.205, 0.452, z - 0.028), (0.205, 0.466, z + 0.028), A, r=0.005))
    for i, y in enumerate((0.66, 0.79)):
        zc = -0.215 + (y - 0.62) * (-0.04 / 0.24)
        parts.append(beam(f"back{i}", (y - 0.035, zc + 0.006), (y + 0.035, zc - 0.006), -0.2, 0.2, 0.014, A, r=0.005))
    return join("ENV_Cafe_Chair", parts)


@recipe("ENV_Parasol", "ORIGINAL", smooth=30)
def parasol():
    """Terrace parasol, 2.5 m canopy: eight-panel canvas shell (ENV_Canvas_Cream) over eight ribs, finial, aluminium
    pole with a runner, heavy iron base."""
    parts = [lathe("canopy", [(0.035, 2.2), (1.2, 1.955), (1.26, 1.955), (1.26, 2.0), (0.9, 2.17), (0.45, 2.33), (0.06, 2.43), (0.0, 2.44)],
                   "ENV_Canvas_Cream", segments=8),
             lathe("pole", [(0.028, 0.08), (0.028, 2.46), (0.0, 2.47)], "ENV_PropMat_Alu", segments=12),
             lathe("runner", [(0.045, 1.72), (0.045, 1.84), (0.0, 1.85)], "ENV_PropMat_Alu", segments=12),
             sphere("finial", (0.0, 2.48, 0.0), 0.045, "ENV_PropMat_Alu", segments=12),
             lathe("base", [(0.3, 0.0), (0.3, 0.035), (0.26, 0.06), (0.07, 0.09), (0.045, 0.14), (0.0, 0.14)], "ENV_PropMat_Negro", segments=20)]
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        parts.append(tube(f"rib{k}", (0.0, 1.84, 0.0), (1.12 * math.cos(a), 1.955, 1.12 * math.sin(a)), 0.009, "ENV_PropMat_Alu", segments=6))
    return join("ENV_Parasol", parts)


@recipe("ENV_Bicycle", "ORIGINAL", smooth=35)
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


@recipe("ENV_Bench_Street", "CREATE_DERIVED", smooth=35)
def bench_street():
    """Municipal street bench (banco de listones) 1.9 m, faces +z: two cast-iron end frames painted carriage green —
    splayed legs, seat rail, raked back post and a rounded armrest on rubber feet — carrying four seat slats and three
    back slats in the kit timber (MI_WoodTrim dark band). Every edge rounded, sections thick enough to read at 15 m."""
    parts = []
    iron = "ENV_PropMat_Verde"
    for sx in (-0.82, 0.82):
        x0, x1 = sx - 0.032, sx + 0.032
        for i, (a, b) in enumerate((((0.0, 0.27), (0.44, 0.22)),     # front leg
                                     ((0.0, -0.28), (0.44, -0.2)),    # rear leg
                                     ((0.40, 0.25), (0.40, -0.24)),   # seat rail
                                     ((0.38, -0.23), (0.88, -0.36)),  # raked back post
                                     ((0.42, 0.22), (0.66, 0.21)),    # arm post
                                     ((0.65, 0.27), (0.68, -0.29)))):  # armrest
            parts.append(beam(f"f{sx}{i}", a, b, x0, x1, 0.058, iron, r=0.014))
        for z in (0.27, -0.28):
            parts.append(rbox(f"foot{sx}{z}", (sx - 0.05, 0.0, z - 0.055), (sx + 0.05, 0.03, z + 0.055), "ENV_PropMat_Oscuro", r=0.01))
    for i, z in enumerate((0.19, 0.085, -0.02, -0.125)):
        parts.append(rbox(f"s{i}", (-0.96, 0.43, z - 0.047), (0.96, 0.472, z + 0.047), "MI_WoodTrim", r=0.013, uv="band", band=WOOD_DARK))
    dy, dz = 0.5, -0.13
    L = math.hypot(dy, dz)
    ty, tz = dy / L, dz / L            # along the back post
    ny, nz = -tz, ty                   # its front normal (towards +z)
    for i, t in enumerate((0.3, 0.56, 0.82)):
        y, z = 0.38 + dy * t + ny * 0.047, -0.23 + dz * t + nz * 0.047
        parts.append(beam(f"b{i}", (y - ty * 0.05, z - tz * 0.05), (y + ty * 0.05, z + tz * 0.05), -0.96, 0.96, 0.036, "MI_WoodTrim", r=0.012, band=WOOD_DARK))
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


@recipe("ENV_Sat_Dish", "ORIGINAL", smooth=35)
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


# ---------------------------------------------------------------- recipes: casco quality pass (owner 2026-09-28)
# "los assets creados propios no están al nivel de los quaternius": every piece below is modelled for the kit's
# stylised look — chunky readable silhouettes, bevelled edges, revolved profiles instead of bare cylinders, and
# painted textures (kit trim sheets or the generated T_ENV_* painted maps) instead of flat colours. Lebaniego
# vocabulary for the CASCO: deep eaves on carved rafter tails (canecillos), solanas, ashlar quoins and window
# surrounds in sandstone, a casona shield.

def lathe(name, profile, mat, segments=16, center=(0.0, 0.0), band=None):
    """Surface of revolution about the vertical axis through (x, z) = center. profile: [(radius, y), ...] bottom to
    top; radius 0 at an end closes it to a point. UVs wrap once around (U) and follow the profile length (V)."""
    bm = bmesh.new()
    rings = []
    for r, y in profile:
        ring = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            ring.append(bm.verts.new(U(center[0] + r * math.cos(a), y, center[1] + r * math.sin(a))))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for i in range(segments):
            bm.faces.new([a[i], a[(i + 1) % segments], b[(i + 1) % segments], b[i]])
    if profile[0][0] > 1e-4:
        bm.faces.new(rings[0][::-1])
    if profile[-1][0] > 1e-4:
        bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    # cylindrical UVs: U wraps once around at kit density (perimeter of the widest ring), V runs up in metres
    me = ob.data
    layer = _uv_layer(me).data
    bx, by = -center[0], -center[1]          # the axis in Blender coordinates (see U())
    rmax = max(r for r, _ in profile) or 0.1
    for p in me.polygons:
        angs = [math.atan2(me.vertices[me.loops[li].vertex_index].co.y - by, me.vertices[me.loops[li].vertex_index].co.x - bx) for li in p.loop_indices]
        if max(angs) - min(angs) > math.pi:  # face across the seam
            angs = [a + 2 * math.pi if a < 0 else a for a in angs]
        for li, ang in zip(p.loop_indices, angs):
            z = me.vertices[me.loops[li].vertex_index].co.z
            v = z * UV_PER_M
            if band:
                v = band[0] + (v % 1.0) * (band[1] - band[0])
            layer[li].uv = (ang * rmax * UV_PER_M, v)
    return ob


def rafter(name, x, z0, z1, top0, slope, w, h, mat, carve=True, hide_top=True):
    """Timber rafter/joist tail running out along +z: top follows y = top0 - slope*(z - z0); the tip is carved
    (bottom rises in a quarter round) as on lebaniego eaves."""
    xs = (x - w / 2, x + w / 2)
    secs = []
    for t in (0.0, 0.55, 0.7, 0.85, 1.0):
        z = z0 + (z1 - z0) * t
        top = top0 - slope * (z - z0)
        if carve and t > 0.55:
            q = (t - 0.55) / 0.45
            bot = top - max(0.035, h * math.cos(q * math.pi / 2) ** 0.8)
        else:
            bot = top - h
        secs.append((z, [(xs[0], bot), (xs[1], bot), (xs[1], top), (xs[0], top)]))
    ob = loft(name, secs, mat, cap_start=False, hidden=(2,) if hide_top else ())
    uv_band(ob, WOOD_DARK)
    return ob


@recipe("ENV_Downpipe", "ORIGINAL", smooth=35)
def downpipe():
    """Rain-water downpipe, 3 m per unit height (the assembler scales y by storeys): painted iron pipe with socket
    collars and wall brackets. Hopper head and shoe are separate modules so scaling never stretches them."""
    parts = [lathe("pipe", [(0.05, 0.0), (0.05, 3.0)], "ENV_Metal_Downpipe", segments=12)]
    for y in (0.5, 1.5, 2.5):
        parts.append(lathe(f"socket{y}", [(0.058, y - 0.05), (0.064, y - 0.035), (0.064, y + 0.035), (0.058, y + 0.05)], "ENV_Metal_Downpipe", segments=12))
        parts.append(box(f"clip{y}", (-0.018, y - 0.02, -0.14), (0.018, y + 0.02, -0.045), "ENV_Metal_Iron", bevel=0.005))
    return join("ENV_Downpipe", parts)


@recipe("ENV_Downpipe_Head", "ORIGINAL", smooth=35)
def downpipe_head():
    """Hopper head (embudo) under the eave: flared box collecting the gutter, short neck into the pipe. Pipe top at
    y = 0; the hopper sits above it."""
    parts = []
    secs = [(y, [(-w, -d), (w, -d), (w, d), (-w, d)]) for y, w, d in ((0.0, 0.06, 0.06), (0.1, 0.07, 0.07), (0.28, 0.15, 0.11), (0.32, 0.16, 0.12))]
    bm = bmesh.new()
    rings = [[bm.verts.new(U(x, y, z - 0.03)) for x, z in pts] for y, pts in secs]
    for a, b in zip(rings, rings[1:]):
        for i in range(4):
            bm.faces.new([a[i], a[(i + 1) % 4], b[(i + 1) % 4], b[i]])
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    hop = new_object("hopper", bm)
    hop.data.materials.append(material("ENV_Metal_Downpipe"))
    uv_box(hop)
    parts.append(hop)
    parts.append(lathe("rim", [(0.0, 0.32), (0.17, 0.32), (0.17, 0.35), (0.0, 0.35)], "ENV_Metal_Iron", segments=4))
    parts.append(box("outlet", (-0.04, 0.24, -0.16), (0.04, 0.3, -0.09), "ENV_Metal_Downpipe", bevel=0.005))
    return join("ENV_Downpipe_Head", parts)


@recipe("ENV_Downpipe_Shoe", "ORIGINAL", smooth=35)
def downpipe_shoe():
    """Pipe shoe (zapata): the pipe kicks forward at the foot and ends in a cast-iron boot over the channel."""
    parts = [tube("kick", (0, 0.42, 0), (0, 0.16, 0.12), 0.05, "ENV_Metal_Downpipe", segments=12),
             lathe("boot", [(0.075, 0.0), (0.08, 0.04), (0.066, 0.18), (0.058, 0.2)], "ENV_Metal_Iron", segments=12, center=(0.0, 0.14)),
             lathe("socket", [(0.058, 0.36), (0.066, 0.38), (0.066, 0.44), (0.058, 0.46)], "ENV_Metal_Downpipe", segments=12)]
    return join("ENV_Downpipe_Shoe", parts)


@recipe("ENV_Awning", "ORIGINAL")
def awning():
    """Shop awning (toldo) over a 2 m bay: striped canvas on a gentle convex curve, scalloped valance, iron arms and
    front bar. The canvas slot (ENV_Canvas_*) carries the stripes; one texture tile across the bay = 4 stripes."""
    y_wall, y_front, z_wall, z_front = 2.74, 2.26, WALL_FACE + 0.02, 1.05
    n = 6
    bm = bmesh.new()
    cols = []
    for k in range(n + 1):
        t = k / n
        z = z_wall + (z_front - z_wall) * t
        y = y_wall + (y_front - y_wall) * t + 0.06 * math.sin(t * math.pi)  # slight belly
        cols.append((z, y))
    xs = [-0.95 + 1.9 * i / 8 for i in range(9)]
    grid = [[bm.verts.new(U(x, y, z)) for x in xs] for z, y in cols]
    for a, b in zip(grid, grid[1:]):
        for i in range(len(xs) - 1):
            bm.faces.new([a[i], a[i + 1], b[i + 1], b[i]])
    # valance with scallops: 5 tongues along the front edge
    zf, yf = cols[-1]
    val = []
    m = 40
    for i in range(m + 1):
        x = -0.95 + 1.9 * i / m
        s = abs(math.sin(i / m * 5 * math.pi))
        val.append((x, yf - 0.16 - 0.06 * s))
    top = [bm.verts.new(U(x, yf, zf + 0.004)) for x, _ in val]
    bot = [bm.verts.new(U(x, y, zf + 0.004)) for x, y in val]
    for i in range(m):
        bm.faces.new([top[i], top[i + 1], bot[i + 1], bot[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    canvas = new_object("canvas", bm)
    canvas.data.materials.append(material("ENV_Canvas_Green"))
    sol = canvas.modifiers.new("t", "SOLIDIFY")
    sol.thickness = 0.012
    bpy.context.view_layer.objects.active = canvas
    bpy.ops.object.modifier_apply(modifier="t")
    me = canvas.data
    layer = _uv_layer(me).data
    for p in me.polygons:
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            layer[li].uv = ((-co.x + 0.95) / 1.9, (co.z + (-co.y)) * 0.6)  # U across the bay, V down the slope
    parts = [canvas]
    for sx in (-1, 1):
        parts.append(tube(f"arm{sx}", (sx * 0.9, 2.02, WALL_FACE), (sx * 0.9, yf - 0.03, zf - 0.02), 0.014, "ENV_Metal_Iron"))
        parts.append(box(f"plate{sx}", (sx * 0.9 - 0.04, 1.96, WALL_FACE - 0.01), (sx * 0.9 + 0.04, 2.1, WALL_FACE + 0.015), "ENV_Metal_Iron", bevel=0.004))
    parts.append(tube("bar", (-0.95, yf - 0.03, zf - 0.02), (0.95, yf - 0.03, zf - 0.02), 0.018, "ENV_Metal_Iron", segments=8))
    parts.append(box("roller", (-0.97, y_wall - 0.02, WALL_FACE), (0.97, y_wall + 0.12, WALL_FACE + 0.12), "ENV_Metal_Galvanised", bevel=0.03))
    return join("ENV_Awning", parts)


@recipe("ENV_Lamp_Post", "ORIGINAL", smooth=35)
def lamp_post():
    """Cast-iron street lamp in the classic Spanish 'fernandina' line (about 3.9 m): moulded base, fluted-looking
    tapering shaft with collars, four-sided lantern with a pyramid hood and finial."""
    prof = [(0.21, 0.0), (0.21, 0.08), (0.17, 0.12), (0.17, 0.22), (0.14, 0.26), (0.155, 0.36), (0.12, 0.46), (0.085, 0.62),
            (0.07, 0.8), (0.062, 2.6), (0.058, 2.95), (0.08, 2.98), (0.08, 3.04), (0.06, 3.07), (0.05, 3.2), (0.09, 3.24), (0.09, 3.28), (0.0, 3.28)]
    parts = [lathe("post", prof, "ENV_Metal_Iron", segments=14)]
    # lantern: glass body tapering out, iron corner bars, hood and finial
    secs = [(3.28, 0.12), (3.72, 0.19)]
    bm = bmesh.new()
    rings = [[bm.verts.new(U(x * r, y, z * r)) for x, z in ((-1, -1), (1, -1), (1, 1), (-1, 1))] for y, r in secs]
    for i in range(4):
        bm.faces.new([rings[0][i], rings[0][(i + 1) % 4], rings[1][(i + 1) % 4], rings[1][i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    glass = new_object("glass", bm)
    glass.data.materials.append(material("ENV_Lamp_Glass"))
    uv_box(glass)
    parts.append(glass)
    for cx, cz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        parts.append(tube(f"bar{cx}{cz}", (cx * 0.12, 3.28, cz * 0.12), (cx * 0.19, 3.72, cz * 0.19), 0.012, "ENV_Metal_Iron", segments=6))
    parts.append(box("gallery", (-0.15, 3.24, -0.15), (0.15, 3.3, 0.15), "ENV_Metal_Iron", bevel=0.01))
    hood = [(0.23, 3.72), (0.23, 3.76), (0.0, 3.98)]
    parts.append(lathe("hood", hood, "ENV_Metal_Iron", segments=4))
    parts.append(lathe("finial", [(0.02, 3.96), (0.035, 4.0), (0.0, 4.08)], "ENV_Metal_Iron", segments=8))
    return join("ENV_Lamp_Post", parts)


@recipe("ENV_Bollard_Street", "ORIGINAL", smooth=35)
def bollard_street():
    """Cast-iron street bollard (pilona), 0.95 m: moulded foot, slightly tapering body, collar and domed cap."""
    prof = [(0.12, 0.0), (0.12, 0.05), (0.095, 0.09), (0.085, 0.12), (0.078, 0.68), (0.098, 0.7), (0.098, 0.76), (0.075, 0.79),
            (0.08, 0.84), (0.07, 0.9), (0.04, 0.94), (0.0, 0.95)]
    return join("ENV_Bollard_Street", [lathe("b", prof, "ENV_Metal_Iron", segments=14)])


@recipe("ENV_Bin_Street", "CREATE_DERIVED", smooth=35)
def bin_street():
    """Rustic litter bin: ring of dark timber slats (kit MI_WoodTrim dark band) bound by two iron hoops, iron rim,
    dark liner inside. Free-standing, 0.8 m."""
    parts = []
    n = 14
    r = 0.22
    for i in range(n):
        a = 2 * math.pi * i / n
        x, z = r * math.cos(a), r * math.sin(a)
        slat = box(f"s{i}", (-0.042, 0.02, -0.018), (0.042, 0.78, 0.018), "MI_WoodTrim", uv="band", band=WOOD_DARK, bevel=0.006)
        slat.rotation_euler = (0, 0, a + math.pi / 2)  # long side tangent to the ring (see U())
        slat.location = U(x, 0, z)
        apply_transform(slat)
        parts.append(slat)
    for y in (0.14, 0.64):
        parts.append(lathe(f"hoop{y}", [(0.245, y), (0.252, y + 0.01), (0.252, y + 0.05), (0.245, y + 0.06)], "ENV_Metal_Iron", segments=16))
    parts.append(lathe("rim", [(0.2, 0.76), (0.255, 0.77), (0.255, 0.81), (0.2, 0.82)], "ENV_Metal_Iron", segments=16))
    parts.append(lathe("liner", [(0.0, 0.08), (0.19, 0.08), (0.2, 0.78)], "ENV_Metal_Iron", segments=12))
    return join("ENV_Bin_Street", parts)


@recipe("ENV_Utility_Box", "ORIGINAL", smooth=35)
def utility_box():
    """Meter cabinet (hornacina de contadores) on a ground-floor facade: galvanised steel box with a recessed door,
    hinges, lock, louvres and the service conduit down to the ground."""
    z0, z1 = WALL_FACE, WALL_FACE + 0.2
    parts = [box("body", (-0.32, 0.55, z0), (0.32, 1.45, z1), "ENV_Metal_Galvanised", bevel=0.02),
             box("door", (-0.27, 0.6, z1 - 0.004), (0.27, 1.4, z1 + 0.012), "ENV_Metal_Shutter", bevel=0.008),
             box("roof", (-0.34, 1.44, z0), (0.34, 1.49, z1 + 0.04), "ENV_Metal_Galvanised", bevel=0.01)]
    for y in (0.72, 1.28):
        parts.append(box(f"hinge{y}", (-0.3, y, z1), (-0.26, y + 0.07, z1 + 0.03), "ENV_Metal_Iron", bevel=0.004))
    parts.append(box("lock", (0.19, 0.98, z1 + 0.01), (0.23, 1.06, z1 + 0.035), "ENV_Metal_Iron", bevel=0.004))
    for k in range(4):
        y = 1.18 + k * 0.045
        parts.append(box(f"louvre{k}", (-0.16, y, z1 + 0.01), (0.16, y + 0.02, z1 + 0.03), "ENV_Metal_Galvanised"))
    parts.append(box("plate", (-0.08, 0.72, z1 + 0.01), (0.08, 0.8, z1 + 0.018), "ENV_Sign_Board"))
    parts.append(lathe("conduit", [(0.022, 0.0), (0.022, 0.56)], "ENV_Metal_Iron", segments=8, center=(0.0, z0 + 0.06)))
    return join("ENV_Utility_Box", parts)


@recipe("ENV_Sign_Bracket", "ORIGINAL", smooth=35)
def sign_bracket():
    """Hanging shop sign on a wrought-iron bracket (the Pyrenean/lebaniego street's signature): wall plate, top bar,
    a scrolled strut, two rings and a painted board in a moulded dark-timber frame (blank: no lettering in ENV)."""
    y = 3.05
    parts = [box("plate", (-0.06, y - 0.4, WALL_FACE - 0.005), (0.06, y + 0.12, WALL_FACE + 0.025), "ENV_Metal_Iron", bevel=0.008),
             tube("bar", (0, y + 0.03, WALL_FACE), (0, y + 0.03, WALL_FACE + 0.9), 0.016, "ENV_Metal_Iron"),
             sphere("knob", (0, y + 0.03, WALL_FACE + 0.92), 0.03, "ENV_Metal_Iron", segments=8)]
    # scrolled strut: from low on the plate up to the bar, ending in a spiral curl
    pts = []
    for k in range(13):
        t = k / 12
        pts.append((0.0, y - 0.36 + 0.36 * t ** 0.7, WALL_FACE + 0.02 + 0.5 * t))
    curl_c = (0.0, y - 0.1, WALL_FACE + 0.36)
    for k in range(14):
        a = math.pi * 0.2 + k / 13 * math.pi * 1.6
        rr = 0.09 * (1 - k / 18)
        pts.append((0.0, curl_c[1] + rr * math.sin(a), curl_c[2] - rr * math.cos(a)))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        parts.append(tube(f"sc{i}", a, b, 0.011, "ENV_Metal_Iron", segments=6))
    for zz in (WALL_FACE + 0.3, WALL_FACE + 0.78):
        parts.append(torus(f"ring{zz}", (0, y - 0.03, zz), 0.035, 0.007, "ENV_Metal_Iron", axis="x", segments=10))
    bx0, bx1, by0, by1 = WALL_FACE + 0.22, WALL_FACE + 0.86, y - 0.62, y - 0.08
    parts.append(box("board", (-0.022, by0 + 0.04, bx0 + 0.04), (0.022, by1 - 0.04, bx1 - 0.04), "ENV_Sign_Board", bevel=0.004))
    # painted faces with 0..1 UVs (ENV_Sign_Face), so a business's icon board maps whole on both sides
    for sx in (-1, 1):
        q = bmesh.new()
        vs = [q.verts.new(U(sx * 0.0235, yy, zz)) for yy, zz in ((by0 + 0.05, bx0 + 0.05), (by0 + 0.05, bx1 - 0.05), (by1 - 0.05, bx1 - 0.05), (by1 - 0.05, bx0 + 0.05))]
        q.faces.new(vs)
        fo = new_object(f"face{sx}", q)
        fo.data.materials.append(material("ENV_Sign_Face"))
        layer = _uv_layer(fo.data).data
        for li, uv in zip(fo.data.polygons[0].loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            layer[li].uv = uv if sx > 0 else (1 - uv[0], uv[1])
        me = fo.data
        want = U(sx, 0, 0) - U(0, 0, 0)
        if me.polygons[0].normal.dot(want) < 0:
            me.flip_normals()
        parts.append(fo)
    for nm, lo, hi in (("fT", (-0.032, by1 - 0.05, bx0), (0.032, by1, bx1)), ("fB", (-0.032, by0, bx0), (0.032, by0 + 0.05, bx1)),
                       ("fL", (-0.032, by0, bx0), (0.032, by1, bx0 + 0.05)), ("fR", (-0.032, by0, bx1 - 0.05), (0.032, by1, bx1))):
        parts.append(box(nm, lo, hi, "MI_WoodTrim", uv="band", band=WOOD_DARK, bevel=0.008))
    return join("ENV_Sign_Bracket", parts)


@recipe("ENV_Shop_Fascia", "CREATE_DERIVED")
def shop_fascia():
    """Painted fascia board over a shop opening in a moulded timber frame with end consoles (blank board)."""
    z = WALL_FACE
    parts = [box("board", (-0.9, 2.47, z), (0.9, 2.88, z + 0.05), "ENV_Sign_Board", bevel=0.008),
             box("capT", (-0.97, 2.87, z), (0.97, 2.95, z + 0.11), "MI_WoodTrim", uv="band", band=WOOD_DARK, bevel=0.015),
             box("capB", (-0.95, 2.42, z), (0.95, 2.48, z + 0.09), "MI_WoodTrim", uv="band", band=WOOD_DARK, bevel=0.012)]
    for sx in (-1, 1):
        parts.append(loft(f"console{sx}", [(z, [(sx * 0.93 - 0.04, 2.3), (sx * 0.93 + 0.04, 2.3), (sx * 0.93 + 0.04, 2.95), (sx * 0.93 - 0.04, 2.95)]),
                                          (z + 0.12, [(sx * 0.93 - 0.04, 2.8), (sx * 0.93 + 0.04, 2.8), (sx * 0.93 + 0.04, 2.95), (sx * 0.93 - 0.04, 2.95)])], "MI_WoodTrim"))
        uv_band(parts[-1], WOOD_DARK)
    return join("ENV_Shop_Fascia", parts)


@recipe("ENV_Window_Reja", "ORIGINAL", smooth=40)
def window_reja():
    """Box grille (reja de cajón) over a ground-floor wide window: square wrought-iron bars on a flat-bar frame that
    stands out from the wall far enough to clear the kit sill, three flat cross bands, returns back to the wall — the
    Spanish ground floor's first line of privacy and a cheap way to vary ground floors. Fits the kit wide window
    (±0.80 m, sill 0.94 m, head 2.52 m, sill 0.42 m proud)."""
    M = "ENV_PropMat_Negro"
    x0, x1, y0, y1, zf, z0 = -0.86, 0.86, 0.9, 2.6, 0.47, WALL_FACE
    parts = [rbox("top", (x0, y1 - 0.025, zf - 0.012), (x1, y1 + 0.02, zf + 0.012), M, r=0.005),
             rbox("bot", (x0, y0 - 0.02, zf - 0.012), (x1, y0 + 0.025, zf + 0.012), M, r=0.005)]
    for sx in (x0, x1):
        parts.append(rbox(f"side{sx}", (sx - 0.022, y0 - 0.02, zf - 0.012), (sx + 0.022, y1 + 0.02, zf + 0.012), M, r=0.005))
        for yy in (y0, y1):
            parts.append(rbox(f"ret{sx}{yy}", (sx - 0.012, yy - 0.02, z0), (sx + 0.012, yy + 0.02, zf), M, r=0.004))
        for zz in (z0 + (zf - z0) * 0.5,):
            parts.append(rbox(f"rv{sx}", (sx - 0.01, y0, zz - 0.01), (sx + 0.01, y1, zz + 0.01), M, r=0.003))
    x = x0 + 0.13
    while x < x1 - 0.08:
        parts.append(rbox(f"bar{x:.2f}", (x - 0.011, y0, zf - 0.011), (x + 0.011, y1, zf + 0.011), M, r=0.003))
        x += 0.13
    for yy in (1.12, 1.76, 2.4):
        parts.append(rbox(f"band{yy}", (x0, yy - 0.018, zf - 0.004), (x1, yy + 0.018, zf + 0.016), M, r=0.004))
    return join("ENV_Window_Reja", parts)


@recipe("ENV_Fascia_Lamp", "ORIGINAL", smooth=40)
def fascia_lamp():
    """Gooseneck shop-sign lamp (aplique de rótulo): round wall plate, a curved arm reaching 0.55 m out and a small
    enamelled shade hanging over the fascia below. Origin = foot of the plate on the wall face."""
    z = WALL_FACE
    M = "ENV_PropMat_Negro"
    arm = [(0.0, 0.05, z + 0.01), (0.0, 0.08, z + 0.14), (0.0, 0.15, z + 0.3), (0.0, 0.16, z + 0.43), (0.0, 0.11, z + 0.53), (0.0, 0.03, z + 0.57)]
    parts = [sweep("arm", arm, 0.013, M, segments=8),
             lathe("shade", [(0.03, 0.03), (0.05, 0.0), (0.12, -0.1), (0.125, -0.115), (0.0, -0.115)], M, segments=16, center=(0.0, z + 0.57)),
             sphere("bulb", (0.0, -0.1, z + 0.57), 0.04, "ENV_Lamp_Glass", segments=10)]
    plate = lathe("plate", [(0.0, 0.0), (0.06, 0.0), (0.06, 0.018), (0.0, 0.018)], M, segments=14)
    plate.rotation_euler = (math.radians(90), 0, 0)
    plate.location = U(0, 0.06, z)
    apply_transform(plate)
    parts.append(plate)
    return join("ENV_Fascia_Lamp", parts)


@recipe("ENV_Door_Canopy", "ORIGINAL", smooth=30)
def door_canopy():
    """Tejaroz: the small tiled canopy over an old house door in the northern towns — two timber brackets with struts
    on the wall, a boarded rafter frame falling away from the wall, curved clay tiles (cobijas) in a row, a mortar
    fillet against the wall. 2.1 m wide, 0.78 m deep. Origin = door centre on the ground; sits above the kit door
    frames (top 2.58 m)."""
    z = WALL_FACE
    T = "ENV_Joinery_Timber"
    y0, depth, fall = 3.04, 0.74, 0.3            # top at the wall, projection, drop to the eave
    t = math.atan2(fall, depth)
    parts = []
    for x in (-0.86, 0.86):
        parts.append(beam(f"post{x}", (2.2, z + 0.035), (y0 - 0.02, z + 0.035), x - 0.045, x + 0.045, 0.07, T, r=0.008))
        parts.append(beam(f"strut{x}", (2.26, z + 0.05), (y0 - fall * 0.82, z + depth * 0.8), x - 0.04, x + 0.04, 0.07, T, r=0.008))
        parts.append(beam(f"rafter{x}", (y0 - 0.03, z), (y0 - fall - 0.04, z + depth + 0.02), x - 0.045, x + 0.045, 0.09, T, r=0.008))
    parts.append(beam("board", (y0 + 0.02, z), (y0 - fall + 0.02, z + depth + 0.04), -1.05, 1.05, 0.035, T, r=0.006))
    parts.append(beam("fascia", (y0 - fall - 0.06, z + depth + 0.02), (y0 - fall + 0.04, z + depth + 0.05), -1.05, 1.05, 0.04, T, r=0.006))
    # curved tiles laid down the slope, 0.21 m apart, a little overhang at the eave
    bm = bmesh.new()
    L, R, n = depth + 0.12, 0.092, 7
    for c in range(10):
        xc = -0.945 + c * 0.21
        rings = []
        for k in range(5):
            sd = L * k / 4
            base = (y0 + 0.04 - sd * math.sin(t), z + sd * math.cos(t))
            ring = []
            for j in range(n + 1):
                ph = math.pi * j / n
                off = R * math.sin(ph) * (1.0 - 0.12 * k / 4)
                ring.append(bm.verts.new(U(xc + R * math.cos(ph), base[0] + off * math.cos(t), base[1] + off * math.sin(t))))
            rings.append(ring)
        for a, b in zip(rings, rings[1:]):
            for j in range(n):
                bm.faces.new([a[j], a[j + 1], b[j + 1], b[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    tiles = new_object("tiles", bm)
    tiles.data.materials.append(material("ENV_Tile_Aged"))
    solid = tiles.modifiers.new("solid", "SOLIDIFY")
    solid.thickness = 0.018
    bpy.context.view_layer.objects.active = tiles
    bpy.ops.object.modifier_apply(modifier="solid")
    uv_box(tiles)
    parts.append(tiles)
    parts.append(rbox("fillet", (-1.08, y0 - 0.02, z - 0.01), (1.08, y0 + 0.14, z + 0.07), "ENV_PropMat_Gris", r=0.02))
    return join("ENV_Door_Canopy", parts)


@recipe("ENV_Cable_Span", "ORIGINAL", smooth=40)
def cable_span():
    """Service cable slung across a lane between two facades (palomillas): a sagging black cable 4 m long from a
    wall bracket with a white insulator at each end; scaled along x to the span. Origin = left anchor on its wall,
    the cable runs along +x."""
    M = "ENV_PropMat_Negro"
    pts = [(4.0 * k / 16, -0.2 * (1 - (2 * k / 16 - 1) ** 2), 0.0) for k in range(17)]
    parts = [sweep("cable", pts, 0.011, M, segments=6, caps=False)]
    for x, sgn in ((0.0, 1), (4.0, -1)):
        px0, px1 = (x, x + 0.012) if sgn > 0 else (x - 0.012, x)
        parts.append(rbox(f"plate{x}", (px0, -0.06, -0.05), (px1, 0.06, 0.05), M, r=0.004))
        parts.append(tube(f"hook{x}", (x, 0.0, 0.0), (x + 0.1 * sgn, 0.0, 0.0), 0.008, M, segments=6))
        parts.append(sphere(f"ins{x}", (x + 0.1 * sgn, 0.0, 0.0), 0.028, "ENV_PropMat_Blanco", segments=8))
    return join("ENV_Cable_Span", parts)


@recipe("ENV_Planter_Pot", "ORIGINAL", smooth=40)
def planter_pot():
    """Terracotta planter pot (0.45 m): foot ring, flared body, thick rolled rim; soil top. Smooth-shaded."""
    prof = [(0.0, 0.0), (0.15, 0.0), (0.162, 0.018), (0.158, 0.045), (0.19, 0.2), (0.222, 0.35), (0.235, 0.352), (0.258, 0.37),
            (0.262, 0.4), (0.25, 0.428), (0.228, 0.432), (0.215, 0.41)]
    return join("ENV_Planter_Pot", [lathe("pot", prof, "ENV_Terracotta", segments=20),
                                    lathe("soil", [(0.0, 0.39), (0.215, 0.39)], "ENV_Soil", segments=20)])


# ---- lebaniego vocabulary

EAVE_SLOPE = 0.48  # kit roof underside at the front: falls 0.48 m per m (measured on the 6 m eaves roof, pitch 0.45)


@recipe("ENV_Eave_Canecillos", "CREATE_DERIVED")
def eave_canecillos():
    """Lebaniego deep eave for one 2 m bay, fitted under the kit roof overhang: timber boarding (tablazón) following
    the roof underside, five carved rafter tails (canecillos) and the wall plate. y = 0 is the facade top (floors x
    3 m), the street face is at z = WALL_FACE. Kit MI_WoodTrim trim sheet (palette joinery: chestnut)."""
    z0, z1 = WALL_FACE, 0.88
    parts = []
    # boarding: thin sloped plank surface just under the roof
    bm = bmesh.new()
    pts = [(-1.0, z0), (1.0, z0), (1.0, z1), (-1.0, z1)]
    top = [bm.verts.new(U(x, -0.045 - EAVE_SLOPE * (z - z0), z)) for x, z in pts]
    bot = [bm.verts.new(U(x, -0.075 - EAVE_SLOPE * (z - z0), z)) for x, z in pts]
    bm.faces.new(top)
    bm.faces.new(bot[::-1])
    for i in range(4):
        bm.faces.new([top[i], bot[i], bot[(i + 1) % 4], top[(i + 1) % 4]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    boards = new_object("boards", bm)
    boards.data.materials.append(material("MI_WoodTrim"))
    uv_band(boards, WOOD_LIGHT)
    parts.append(boards)
    for i, x in enumerate((-0.8, -0.4, 0.0, 0.4, 0.8)):
        parts.append(rafter(f"can{i}", x, z0, z1 - 0.04, -0.075, EAVE_SLOPE, 0.11, 0.17, "MI_WoodTrim"))
    parts.append(box("plate", (-1.0, -0.26, z0 - 0.02), (1.0, -0.075, z0 + 0.13), "MI_WoodTrim", uv="band", band=WOOD_DARK))
    return join("ENV_Eave_Canecillos", parts)


@recipe("ENV_Solana_Bay", "CREATE_DERIVED")
def solana_bay():
    """Solana for one 2 m bay of the top floor (slot frame, y = 0 at the floor): board floor on carved joist tails,
    front fascia, balustrade of turned balusters between rails, a post at the bay's left edge rising to the eave with
    a zapata. Bays chain along the facade; ENV_Solana_Wing closes the ends. Kit MI_WoodTrim (palette joinery)."""
    zf = 1.0
    parts = [box("floor", (-1.0, -0.02, WALL_FACE - 0.02), (1.0, 0.06, zf), "MI_WoodTrim", uv="band", band=WOOD_LIGHT),
             box("fascia", (-1.0, -0.12, zf - 0.03), (1.0, 0.06, zf + 0.02), "MI_WoodTrim", uv="band", band=WOOD_DARK)]
    for i, x in enumerate((-0.66, 0.0, 0.66)):
        parts.append(rafter(f"joist{i}", x, WALL_FACE, zf + 0.12, -0.02, 0.0, 0.1, 0.18, "MI_WoodTrim"))
    rail_z = zf - 0.07
    parts.append(box("rail_b", (-1.0, 0.07, rail_z - 0.04), (1.0, 0.13, rail_z + 0.04), "MI_WoodTrim", uv="band", band=WOOD_DARK))
    parts.append(box("rail_t", (-1.0, 0.98, rail_z - 0.055), (1.0, 1.05, rail_z + 0.055), "MI_WoodTrim", uv="band", band=WOOD_DARK, bevel=0.012))
    bal = [(0.022, 0.13), (0.03, 0.24), (0.036, 0.5), (0.022, 0.76), (0.02, 0.98)]
    x = -0.86
    k = 0
    while x < 0.95:
        parts.append(lathe(f"bal{k}", bal, "MI_WoodTrim", segments=6, center=(x, rail_z), band=WOOD_DARK))
        x += 0.125
        k += 1
    parts.append(box("post", (-0.99, 0.06, rail_z - 0.06), (-0.87, 2.9, rail_z + 0.06), "MI_WoodTrim", uv="band", band=WOOD_DARK, bevel=0.012))
    parts.append(box("zapata", (-1.2, 2.78, rail_z - 0.07), (-0.66, 2.92, rail_z + 0.07), "MI_WoodTrim", uv="band", band=WOOD_DARK, bevel=0.015))
    parts.append(box("beam", (-1.0, 2.92, rail_z - 0.08), (1.0, 3.06, rail_z + 0.08), "MI_WoodTrim", uv="band", band=WOOD_DARK, bevel=0.012))
    return join("ENV_Solana_Bay", parts)


@recipe("ENV_Solana_Wing", "CREATE_DERIVED")
def solana_wing():
    """Masonry wing wall (cortavientos) closing one end of a solana: 0.3 m thick, as deep as the solana, one storey,
    in the building's wall material (MI_Plaster slot, palette remapped) with an ashlar coping. Slot frame at the
    facade end; the wing projects along +z."""
    parts = [box("wing", (-0.15, -0.1, WALL_FACE - 0.05), (0.15, 3.0, 1.12), "MI_Plaster", uv="box", bevel=0.01),
             box("cope", (-0.18, 3.0, WALL_FACE - 0.05), (0.18, 3.1, 1.16), "ENV_Stone_Sandstone", uv="band", band=ROCK_SLAB, bevel=0.01)]
    return join("ENV_Solana_Wing", parts)


@recipe("ENV_Quoin_Ashlar", "CREATE_DERIVED")
def quoin_ashlar():
    """Ashlar quoins for one storey (3 m) of an exposed building corner: ten courses alternating long and short
    blocks on the two faces, 3 cm proud of the render — slimmer than the kit pilaster the owner rejected. Local frame
    as the kit corner piece: the outer corner is at (WALL_FACE, WALL_FACE), faces towards +x and +z."""
    c = WALL_FACE
    parts = []
    h = 0.3
    o, e, i = c + 0.03, 0.012, c - 0.06      # proud face, arris chamfer, inner line inside the wall
    for k in range(10):
        y0 = k * h + 0.004
        y1 = (k + 1) * h - 0.004
        long_front = k % 2 == 0
        lf, ls = (0.5, 0.26) if long_front else (0.28, 0.46)
        # outline (x, z) around the L; the last two edges run inside the wall
        pts = [(c - lf, i), (c - lf, o), (o - e, o), (o, o - e), (o, i), (o, c - ls), (i, c - ls), (i, i)]
        caps = [[0, 1, 2, 3, 4, 7], [7, 4, 5, 6]]
        parts.append(prism_xz(f"q{k}", pts, y0, y1, "ENV_Stone_Sandstone", band=ROCK_SLAB, caps=caps, hidden=(6, 7)))
    return join("ENV_Quoin_Ashlar", parts)


@recipe("ENV_Quoin_Slim", "CREATE_DERIVED")
def quoin_slim():
    """Slim quoins for one storey of a seen corner (owner audit 2026-09-29: the ashlar quoins were "repetitivos y
    gruesos"): twelve 0.25 m courses of short/long blocks (0.34 / 0.2 m), only 1.2 cm proud, fine arris. Families use
    it for dressed-stone corners on rendered houses and, painted, for rendered corner bands."""
    c = WALL_FACE
    parts = []
    h = 0.25
    o, e, i = c + 0.012, 0.006, c - 0.05
    for k in range(12):
        y0 = k * h + 0.003
        y1 = (k + 1) * h - 0.003
        lf, ls = (0.34, 0.2) if k % 2 == 0 else (0.2, 0.34)
        pts = [(c - lf, i), (c - lf, o), (o - e, o), (o, o - e), (o, i), (o, c - ls), (i, c - ls), (i, i)]
        caps = [[0, 1, 2, 3, 4, 7], [7, 4, 5, 6]]
        parts.append(prism_xz(f"q{k}", pts, y0, y1, "ENV_Stone_Sandstone", band=ROCK_SLAB, caps=caps, hidden=(6, 7)))
    return join("ENV_Quoin_Slim", parts)


def prism_xz(name, pts, y0, y1, mat, band=None, caps=None, hidden=()):
    """Vertical prism over an (x, z) outline between y0 and y1 (Unity frame). caps: convex pieces of the outline
    (point indices) for top and bottom, so concave outlines triangulate correctly; hidden: side faces (edge i from
    point i to i+1) dropped after the normals resolve, where they sit inside a wall."""
    bm = bmesh.new()
    lo = [bm.verts.new(U(x, y0, z)) for x, z in pts]
    hi = [bm.verts.new(U(x, y1, z)) for x, z in pts]
    n = len(pts)
    drop = []
    for k in range(n):
        f = bm.faces.new([lo[k], lo[(k + 1) % n], hi[(k + 1) % n], hi[k]])
        if k in hidden:
            drop.append(f)
    for poly in caps or [list(range(n))]:
        bm.faces.new([lo[k] for k in poly][::-1])
        bm.faces.new([hi[k] for k in poly])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if drop:
        bmesh.ops.delete(bm, geom=drop, context="FACES_ONLY")
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    if band:
        uv_band(ob, band)
    else:
        uv_box(ob)
    return ob


@recipe("ENV_Window_Wide_Ashlar", "CREATE_DERIVED")
def window_wide_ashlar():
    """Wide window for rendered walls in the casco manner: sandstone surround (jambs in alternating blocks, lintel
    with ears, projecting sill) around the kit opening (±0.6, 1.05-2.31) and a recessed glazed sash. Replaces the
    kit's white timber trim window where the grammar asks for ashlar surrounds."""
    c = WALL_FACE
    st = "ENV_Stone_Sandstone"
    parts = []
    ys = [1.05, 1.365, 1.68, 1.995, 2.31]
    for k in range(4):
        w = 0.24 if k % 2 == 0 else 0.17
        for sx in (-1, 1):
            xa, xb = sorted((sx * 0.6, sx * (0.6 + w)))
            parts.append(box(f"j{k}{sx}", (xa, ys[k] + 0.004, c - 0.12), (xb, ys[k + 1] - 0.004, c + 0.03), st, uv="band", band=ROCK_SLAB))
    parts.append(box("lintel", (-0.9, 2.31, c - 0.12), (0.9, 2.57, c + 0.035), st, uv="band", band=ROCK_SLAB, bevel=0.012))
    parts.append(box("sill", (-0.82, 0.97, c - 0.12), (0.82, 1.05, c + 0.08), st, uv="band", band=ROCK_SLAB, bevel=0.01))
    x0, x1, y0, y1, zf, zb = -0.6, 0.6, 1.05, 2.31, -0.02, -0.1
    parts += _frame_rect("sash", x0, x1, y0, y1, zf, zb, 0.07)
    parts.append(box("mul", (-0.03, y0 + 0.07, zb + 0.01), (0.03, y1 - 0.07, zf - 0.01), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    parts.append(box("tr", (x0 + 0.07, 1.86, zb + 0.01), (x1 - 0.07, 1.91, zf - 0.01), "MI_WoodTrim", uv="band", band=WOOD_LIGHT))
    parts.append(box("glass", (x0 + 0.07, y0 + 0.07, -0.07), (x1 - 0.07, y1 - 0.07, -0.06), "MI_WindowGlass"))
    return join("ENV_Window_Wide_Ashlar", parts)


@recipe("ENV_Escudo", "CREATE_DERIVED")
def escudo():
    """Generic casona shield (escudo) in sandstone, 0.7 x 1.0 m: moulded cartouche, heater-shaped field with a plain
    cross-quartering, crest scroll on top and a corbel below. Heraldry-neutral: no real family arms."""
    c = WALL_FACE
    st = "ENV_Stone_Sandstone"

    def slab(name, pts, z0, z1, mat, bevel=0.0):
        bm = bmesh.new()
        f = [bm.verts.new(U(x, y, z1)) for x, y in pts]
        b = [bm.verts.new(U(x, y, z0)) for x, y in pts]
        bm.faces.new(f)
        bm.faces.new(b[::-1])
        n = len(pts)
        for i in range(n):
            bm.faces.new([f[i], b[i], b[(i + 1) % n], f[(i + 1) % n]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = new_object(name, bm)
        ob.data.materials.append(material(mat))
        if bevel:
            do_bevel(ob, bevel)
        uv_band(ob, ROCK_SLAB)
        return ob

    def heater(w, h, y0, n=16):
        right = [(w * (1 - (t ** 2.2) * 0.98), y0 + h - h * t) for t in (i / n for i in range(n + 1))]
        left = [(-x, y) for x, y in reversed(right)]
        return [(-w, y0 + h)] + [(w, y0 + h)] + right[1:] + left[:-1]

    parts = [slab("cartouche", heater(0.44, 1.02, 0.12), c - 0.02, c + 0.08, st, 0.012),
             slab("field", heater(0.36, 0.9, 0.2), c + 0.08, c + 0.115, st),
             box("barV", (-0.03, 0.34, c + 0.11), (0.03, 1.08, c + 0.14), st, uv="band", band=ROCK_SLAB),
             box("barH", (-0.34, 0.74, c + 0.11), (0.34, 0.8, c + 0.14), st, uv="band", band=ROCK_SLAB),
             box("crown", (-0.3, 1.14, c - 0.01), (0.3, 1.24, c + 0.1), st, uv="band", band=ROCK_SLAB, bevel=0.012),
             box("corbel", (-0.16, -0.04, c - 0.02), (0.16, 0.14, c + 0.07), st, uv="band", band=ROCK_SLAB, bevel=0.012)]
    for k, x in enumerate((-0.22, 0.0, 0.22)):
        parts.append(sphere(f"fleuron{k}", (x, 1.3, c + 0.04), 0.06, st, segments=8))
    for sx in (-1, 1):  # mantling scrolls at the flanks, not at the top (a top pair read as vase handles)
        parts.append(torus(f"scroll{sx}", (sx * 0.5, 0.62, c + 0.03), 0.08, 0.025, st, axis="z", segments=12))
        parts.append(torus(f"scroll2{sx}", (sx * 0.47, 0.95, c + 0.03), 0.06, 0.02, st, axis="z", segments=12))
    return join("ENV_Escudo", parts)


@recipe("ENV_Bridge_Arch", "CREATE_DERIVED")
def bridge_arch():
    """Stone arch under a casco bridge, as a 1 m wide slice along z that the district builder scales to the deck
    width and along x to the span: segmental arch (span 10 m, springing 3.4 m below the deck, crown 0.6 m below it),
    a ring of dressed voussoirs on both faces, rubble spandrels up to a moulded string course, rubble soffit.
    Deck top at y = 0 (the builder lays the paved deck on it)."""
    span, y_spring, y_crown = 10.0, -3.4, -0.6
    half = span / 2
    rise = y_crown - y_spring
    radius = (half * half + rise * rise) / (2 * rise)
    cy = y_crown - radius
    parts = []
    n = 17
    a0 = math.asin(half / radius)
    ring_t = 0.5

    def arc_pt(a, r):
        return (r * math.sin(a), cy + r * math.cos(a))

    for zf, zb in ((0.5, 0.2), (-0.2, -0.5)):
        for k in range(n):
            t0, t1 = -a0 + 2 * a0 * k / n, -a0 + 2 * a0 * (k + 1) / n
            gap = 0.012
            p = [arc_pt(t0 + gap, radius), arc_pt(t1 - gap, radius), arc_pt(t1 - gap, radius + ring_t), arc_pt(t0 + gap, radius + ring_t)]
            ob = loft(f"v{k}{zf}", [(zb, p), (zf, p)], "ENV_Stone_Sandstone")
            uv_band(ob, ROCK_SLAB)
            parts.append(ob)
    # spandrels: from the extrados up to the string course, both faces (x beyond the arch to the abutments)
    for zf, zb in ((0.5, 0.35), (-0.35, -0.5)):
        pts = []
        m = 24
        for k in range(m + 1):
            a = -a0 + 2 * a0 * k / m
            pts.append(arc_pt(a, radius + ring_t))
        pts = [(half + 0.8, y_spring)] + pts[::-1] + [(-half - 0.8, y_spring), (-half - 0.8, -0.3), (half + 0.8, -0.3)]
        bm = bmesh.new()
        f = [bm.verts.new(U(x, y, zf)) for x, y in pts]
        b = [bm.verts.new(U(x, y, zb)) for x, y in pts]
        bm.faces.new(f)
        bm.faces.new(b[::-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        sp = new_object(f"spandrel{zf}", bm)
        sp.data.materials.append(material("MI_UnevenBrick"))
        uv_box(sp)
        parts.append(sp)
    # soffit: the arch intrados as a vault under the slice
    m = 24
    bm = bmesh.new()
    rows = []
    for k in range(m + 1):
        a = -a0 + 2 * a0 * k / m
        x, y = arc_pt(a, radius)
        rows.append((bm.verts.new(U(x, y, 0.5)), bm.verts.new(U(x, y, -0.5))))
    for (a1, b1), (a2, b2) in zip(rows, rows[1:]):
        bm.faces.new([a1, a2, b2, b1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    so = new_object("soffit", bm)
    so.data.materials.append(material("MI_UnevenBrick"))
    uv_box(so)
    for p in so.data.polygons:  # face down, into the arch
        if p.normal.z > 0:
            p.flip()
    parts.append(so)
    parts.append(box("string", (-half - 0.9, -0.42, -0.56), (half + 0.9, -0.28, 0.56), "ENV_Stone_Sandstone", uv="band", band=ROCK_SLAB, bevel=0.02))
    parts.append(box("fill", (-half - 0.8, -0.28, -0.5), (half + 0.8, -0.02, 0.5), "MI_UnevenBrick", uv="box"))
    return join("ENV_Bridge_Arch", parts)


@recipe("ENV_Fountain_Trough", "CREATE_DERIVED", smooth=35)
def fountain_trough():
    """Neighbourhood fountain of the Cantabrian towns (fuente de caños): a sandstone ashlar back wall framed by two
    pilasters under a moulded cornice, a semicircular crown with ball finials (bolas), a plain plaque, two bronze
    spouts pouring into a long stone trough (pilón), all on a granite apron. Back against a wall at z = 0, facing +z;
    2.9 m wide, 3.1 m high. Invented; replaces the pillar-and-box version (owner: "esa fuente... está fatal")."""
    ds, ash, gr = "ENV_Dressed_Arenisca", "ENV_Mason_Silleria_Arenisca", "ENV_PropMat_Granito"
    parts = [rbox("apron", (-1.62, 0.0, 0.0), (1.62, 0.08, 1.55), gr, r=0.025),
             rbox("plinth", (-1.36, 0.08, 0.0), (1.36, 0.34, 0.42), ds, r=0.02, uv="band", band=ROCK_SLAB),
             box("body", (-1.12, 0.34, 0.0), (1.12, 1.96, 0.3), ash),
             rbox("pilL", (-1.34, 0.34, 0.0), (-1.1, 1.96, 0.4), ds, r=0.02, uv="band", band=ROCK_SLAB),
             rbox("pilR", (1.1, 0.34, 0.0), (1.34, 1.96, 0.4), ds, r=0.02, uv="band", band=ROCK_SLAB),
             rbox("capL", (-1.38, 1.9, 0.0), (-1.06, 1.97, 0.44), ds, r=0.012, uv="band", band=ROCK_SLAB),
             rbox("capR", (1.06, 1.9, 0.0), (1.38, 1.97, 0.44), ds, r=0.012, uv="band", band=ROCK_SLAB),
             rbox("cornice", (-1.46, 1.97, 0.0), (1.46, 2.11, 0.48), ds, r=0.025, uv="band", band=ROCK_SLAB),
             rbox("cornice2", (-1.36, 2.11, 0.0), (1.36, 2.17, 0.4), ds, r=0.015, uv="band", band=ROCK_SLAB),
             rbox("plaque", (-0.42, 1.28, 0.28), (0.42, 1.7, 0.335), ds, r=0.012, uv="band", band=ROCK_SLAB),
             rbox("plaque_in", (-0.34, 1.34, 0.3), (0.34, 1.64, 0.35), ds, r=0.008, uv="band", band=ROCK_SLAB)]
    # semicircular crown with a thin moulded edge
    crown = [(-0.78, 2.17)] + [(0.78 * math.cos(math.radians(180 - 180 * k / 16)), 2.17 + 0.62 * math.sin(math.radians(180 - 180 * k / 16))) for k in range(1, 16)] + [(0.78, 2.17)]
    crown = [(x, y) for x, y in crown][::-1]
    parts.append(slab_xy("crown", crown[::-1], 0.04, 0.3, ds, band=ROCK_SLAB, r=0.015))
    # ball finials: on the pilasters and at the crown's apex
    for x, y, z, rr in ((-1.2, 2.17, 0.2, 0.13), (1.2, 2.17, 0.2, 0.13), (0.0, 2.79, 0.17, 0.11)):
        parts.append(lathe(f"fin{x}", [(0.1, y), (0.1, y + 0.08), (0.07, y + 0.1)], ds, segments=10, center=(x, z)))
        parts.append(sphere(f"ball{x}", (x, y + 0.1 + rr, z), rr, ds, segments=12))
    # two spouts with rosettes, the streams falling into the trough
    for x in (-0.46, 0.46):
        parts.append(cylinder(f"rose{x}", (x, 0.98, 0.31), 0.085, 0.03, "ENV_Bronze", segments=12, axis="z"))
        tip = (x, 0.95, 0.66)
        parts.append(sweep(f"spout{x}", [(x, 0.99, 0.3), (x, 0.985, 0.5), tip], 0.026, "ENV_Bronze", segments=10))
        parts.append(water_jet(f"jet{x}", tip, (0.0, 1.0), 0.14, 0.64, radius=0.018))
    # trough: floor + four rounded walls, water, an overflow notch spout on the right
    x0, x1, z0, z1, y0, y1, t = -1.24, 1.24, 0.34, 1.16, 0.08, 0.74, 0.13
    parts += [box("tb", (x0, y0, z0), (x1, y0 + 0.1, z1), gr),
              rbox("tf", (x0, y0, z1 - t), (x1, y1, z1), gr, r=0.035),
              rbox("tk", (x0, y0, z0), (x1, y1, z0 + t), gr, r=0.035),
              rbox("tl", (x0, y0, z0), (x0 + t, y1, z1), gr, r=0.035),
              rbox("tr", (x1 - t, y0, z0), (x1, y1, z1), gr, r=0.035),
              box("water", (x0 + t, y1 - 0.11, z0 + t), (x1 - t, y1 - 0.1, z1 - t), "ENV_Water_Port"),
              tube("overflow", (x1 - 0.02, 0.62, 0.75), (x1 + 0.1, 0.6, 0.75), 0.02, "ENV_Bronze", segments=8)]
    return join("ENV_Fountain_Trough", parts)


@recipe("ENV_River_Stairs", "CREATE_DERIVED")
def river_stairs():
    """Bajada al río: stone steps running down the face of the channel wall from the bank (y = 0) to a landing just
    above the water (3 m lower), 1.3 m wide, with an iron handrail on the open side. Runs along +x; the wall face is
    at z = 0 and the steps stand in front of it (+z, over the water)."""
    parts = []
    n = 14
    rise, tread, w = 3.0 / n, 0.34, 1.3
    for i in range(n):
        y = -rise * (i + 1)
        parts.append(box(f"st{i}", (i * tread, y, 0.0), (i * tread + tread + 0.02, y + rise, w), "ENV_Stone_Granite", uv="band", band=ROCK_SLAB, bevel=0.01))
        parts.append(box(f"fl{i}", (i * tread, -3.5, 0.02), (i * tread + tread + 0.02, y, w - 0.02), "MI_UnevenBrick"))
    lx = n * tread
    parts.append(box("landing", (lx, -3.0 - 0.12, 0.0), (lx + 1.5, -3.0, w), "ENV_Stone_Granite", uv="band", band=ROCK_SLAB, bevel=0.012))
    parts.append(box("landfill", (lx, -3.5, 0.02), (lx + 1.5, -3.12, w - 0.02), "MI_UnevenBrick"))
    parts.append(box("cheek", (-0.05, -3.5, w), (lx + 1.55, -0.02, w + 0.25), "MI_UnevenBrick"))
    parts.append(box("cope", (-0.08, -0.02, w - 0.02), (0.6, 0.1, w + 0.3), "ENV_Stone_Granite", uv="band", band=ROCK_SLAB, bevel=0.01))
    for i in range(0, n + 1, 4):
        x = min(i * tread, lx)
        y = -rise * i
        parts.append(tube(f"post{i}", (x, y, w + 0.12), (x, y + 0.95, w + 0.12), 0.02, "ENV_Metal_Iron", segments=6))
    parts.append(tube("rail", (0.0, 0.95, w + 0.12), (lx, 0.95 - 3.0, w + 0.12), 0.022, "ENV_Metal_Iron", segments=8))
    parts.append(tube("rail2", (lx, -2.05, w + 0.12), (lx + 1.5, -2.05, w + 0.12), 0.022, "ENV_Metal_Iron", segments=8))
    return join("ENV_River_Stairs", parts)


@recipe("ENV_Kiosk_Plaza", "CREATE_DERIVED")
def kiosk_plaza():
    """Octagonal plaza kiosk (templete de música): stone base with two steps, eight slim cast-iron columns with
    brackets, a frieze, a tiled octagonal roof with a finial. About 7 m across, 6 m high: a landmark for the river
    plaza (the real plaza has one) without copying any real building."""
    parts = []
    n = 8
    r_base, r_col = 3.3, 2.9

    def ring(r, y, rot=math.pi / n):
        return [(r * math.cos(rot + 2 * math.pi * i / n), r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]

    def prism(name, pts, y0, y1, mat, band=ROCK_SLAB):
        bm = bmesh.new()
        lo = [bm.verts.new(U(x, y0, z)) for x, z in pts]
        hi = [bm.verts.new(U(x, y1, z)) for x, z in pts]
        bm.faces.new(lo[::-1])
        bm.faces.new(hi)
        for i in range(len(pts)):
            bm.faces.new([lo[i], lo[(i + 1) % len(pts)], hi[(i + 1) % len(pts)], hi[i]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = new_object(name, bm)
        ob.data.materials.append(material(mat))
        if band:
            uv_band(ob, band)
        else:
            uv_box(ob)
        return ob

    parts.append(prism("step1", ring(r_base + 0.6, 0), 0.0, 0.2, "ENV_Stone_Granite"))
    parts.append(prism("step2", ring(r_base + 0.3, 0), 0.2, 0.4, "ENV_Stone_Granite"))
    parts.append(prism("base", ring(r_base, 0), 0.4, 0.95, "ENV_Stone_Sandstone"))
    parts.append(prism("floor", ring(r_base - 0.05, 0), 0.95, 1.0, "ENV_Stone_Granite"))
    for i, (x, z) in enumerate(ring(r_col, 0)):
        parts.append(lathe(f"col{i}", [(0.1, 1.0), (0.1, 1.12), (0.065, 1.2), (0.055, 3.6), (0.09, 3.7), (0.12, 3.78)], "ENV_Metal_Iron", segments=8, center=(x, z)))
        parts.append(tube(f"brk{i}", (x * 0.97, 3.3, z * 0.97), (x * 0.86, 3.75, z * 0.86), 0.025, "ENV_Metal_Iron", segments=6))
    parts.append(prism("frieze", ring(r_col + 0.18, 0), 3.78, 4.1, "MI_WoodTrim", band=WOOD_DARK))
    # railing between the columns
    pts = ring(r_col, 0)
    for i in range(n):
        if i == 0:
            continue  # the entrance gap faces +x
        a, b = pts[i], pts[(i + 1) % n]
        parts.append(tube(f"rail{i}", (a[0], 1.9, a[1]), (b[0], 1.9, b[1]), 0.02, "ENV_Metal_Iron", segments=6))
        for k in range(1, 6):
            t = k / 6
            x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            parts.append(tube(f"bal{i}{k}", (x, 1.0, z), (x, 1.9, z), 0.012, "ENV_Metal_Iron", segments=5))
    # octagonal roof: tiled pyramid, slight eaves
    bm = bmesh.new()
    eave = [bm.verts.new(U(x, 4.1, z)) for x, z in ring(r_col + 0.7, 0)]
    apex = bm.verts.new(U(0, 6.0, 0))
    for i in range(n):
        bm.faces.new([eave[i], eave[(i + 1) % n], apex])
    bm.faces.new(eave[::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    roof = new_object("roof", bm)
    roof.data.materials.append(material("ENV_Roof_Terracotta"))
    uv_box(roof, scale=0.35)
    parts.append(roof)
    parts.append(lathe("finial", [(0.08, 5.95), (0.1, 6.1), (0.05, 6.3), (0.08, 6.45), (0.0, 6.7)], "ENV_Metal_Iron", segments=8))
    return join("ENV_Kiosk_Plaza", parts)


# ---------------------------------------------------------------- owner audit 2026-09-29: contemporary layer, signage,
# plants, ground contact, plaza landmark, river, tower identity

def face_quad(name, x0, x1, y0, y1, z, mat, flip=False):
    """Single quad in the x/y plane at depth z with UVs 0..1 (sign faces: one texture per panel)."""
    bm = bmesh.new()
    vs = [bm.verts.new(U(x, y, z)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    f = bm.faces.new(vs[::-1] if flip else vs)
    bm.normal_update()
    ob = new_object(name, bm)
    ob.data.materials.append(material(mat))
    layer = _uv_layer(ob.data).data
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for li, uv in zip(ob.data.polygons[0].loop_indices, uvs):
        # U() mirrors x: keep the texture reading left-to-right from the street (+z)
        layer[li].uv = (1 - uv[0], uv[1]) if not flip else uv
    return ob


def fix_face_normal(ob, towards):
    """Make the single-face object face the given Unity-frame direction."""
    me = ob.data
    n = me.polygons[0].normal
    want = U(*towards) - U(0, 0, 0)
    if n.dot(want) < 0:
        me.flip_normals()
    return ob


@recipe("ENV_Sign_Panel", "ORIGINAL")
def sign_panel():
    """Lettering panel 1 x 1 m (scaled per sign): a 15 mm board whose front face maps one sign texture 0..1. The
    district remaps ENV_Sign_Board to the business sign material and scales it to the fascia or wall."""
    body = box("body", (-0.5, -0.5, -0.015), (0.5, 0.5, 0.0), "MI_WoodTrim", uv="band", band=WOOD_DARK)
    face = fix_face_normal(face_quad("face", -0.5, 0.5, -0.5, 0.5, 0.001, "ENV_Sign_Board"), (0, 0, 1))
    return join("ENV_Sign_Panel", [body, face])


@recipe("ENV_Blade_Sign", "ORIGINAL", smooth=40)
def blade_sign():
    """Projecting light-box sign (modern shops, pharmacy cross): round wall plate and steel arm, a 0.6 m box with
    rounded edges; both faces carry the sign texture (ENV_Sign_Board remapped per business)."""
    y0, y1, z0, z1 = 2.75, 3.35, WALL_FACE + 0.18, WALL_FACE + 0.78
    parts = [lathe("plate", [(0.0, 0.0), (0.09, 0.0), (0.09, 0.02), (0.0, 0.02)], "ENV_Metal_Galvanised", segments=16),
             rbox("arm", (-0.025, 3.07, WALL_FACE), (0.025, 3.13, z0 + 0.02), "ENV_Metal_Galvanised", r=0.008),
             rbox("case", (-0.055, y0, z0), (0.055, y1, z1), "ENV_Metal_Galvanised", r=0.025, seg=3)]
    plate = parts[0]
    plate.rotation_euler = (math.radians(90), 0, 0)
    plate.location = U(0, 3.1, WALL_FACE)
    apply_transform(plate)
    for sx in (-1, 1):
        q = bmesh.new()
        vs = [q.verts.new(U(sx * 0.0565, y, z)) for y, z in ((y0 + 0.035, z0 + 0.035), (y0 + 0.035, z1 - 0.035), (y1 - 0.035, z1 - 0.035), (y1 - 0.035, z0 + 0.035))]
        q.faces.new(vs)
        ob = new_object(f"face{sx}", q)
        ob.data.materials.append(material("ENV_Sign_Board"))
        layer = _uv_layer(ob.data).data
        for li, uv in zip(ob.data.polygons[0].loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            layer[li].uv = uv if sx > 0 else (1 - uv[0], uv[1])
        fix_face_normal(ob, (sx, 0, 0))
        parts.append(ob)
    return join("ENV_Blade_Sign", parts)


@recipe("ENV_AFrame_Board", "ORIGINAL", smooth=35)
def aframe_board():
    """Bar A-frame chalkboard (pizarra de caballete) 1 m: two framed boards hinged at the top — chunky timber stiles
    and rails with rounded edges around a dark board, the chalk face (ENV_Sign_Board, remapped per business) on the
    outside of each, iron hinges and a spreader bar."""
    parts = []
    h, lean, zt = 1.0, 0.25, 0.03
    L = math.hypot(h, lean - zt)
    for s in (1, -1):
        zb = s * lean
        ty, tz = h / L, (s * zt - zb) / L          # up along the board
        ny, nz = -tz * s, ty * s                   # outward normal
        ny, nz = (ny, nz) if nz * s > 0 else (-ny, -nz)
        def at(v, w=0.0):
            return (v * ty + w * ny, zb + v * tz + w * nz)
        for x0, x1 in ((-0.31, -0.26), (0.26, 0.31)):
            parts.append(beam(f"stile{s}{x0}", at(0.0), at(L), x0, x1, 0.032, "MI_WoodTrim", r=0.009, band=WOOD_DARK))
        parts.append(beam(f"top{s}", at(L - 0.09), at(L - 0.01), -0.26, 0.26, 0.032, "MI_WoodTrim", r=0.009, band=WOOD_DARK))
        parts.append(beam(f"bot{s}", at(0.1), at(0.18), -0.26, 0.26, 0.032, "MI_WoodTrim", r=0.009, band=WOOD_DARK))
        parts.append(beam(f"panel{s}", at(0.18), at(L - 0.09), -0.26, 0.26, 0.014, "ENV_PropMat_Oscuro", r=0.0))
        q = bmesh.new()
        (ay, az), (by, bz) = at(0.2, 0.0085), at(L - 0.11, 0.0085)
        vs = [q.verts.new(U(x, y, z)) for x, y, z in ((-0.245, ay, az), (0.245, ay, az), (0.245, by, bz), (-0.245, by, bz))]
        q.faces.new(vs)
        ob = new_object(f"chalk{s}", q)
        ob.data.materials.append(material("ENV_Sign_Board"))
        layer = _uv_layer(ob.data).data
        for li, uv in zip(ob.data.polygons[0].loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            layer[li].uv = (1 - uv[0], uv[1]) if s > 0 else uv
        fix_face_normal(ob, (0, ny, nz))
        parts.append(ob)
    for hx in (-0.2, 0.2):
        parts.append(cylinder(f"hinge{hx}", (hx, h - 0.005, 0.0), 0.016, 0.09, "ENV_PropMat_Negro", segments=10, axis="x"))
    parts.append(sweep("spreader", [(-0.24, 0.36, -0.17), (-0.24, 0.36, 0.17)], 0.008, "ENV_PropMat_Negro", segments=6))
    parts.append(sweep("spreader2", [(0.24, 0.36, -0.17), (0.24, 0.36, 0.17)], 0.008, "ENV_PropMat_Negro", segments=6))
    return join("ENV_AFrame_Board", parts)


@recipe("ENV_ATM", "ORIGINAL", smooth=35)
def atm():
    """Cash machine set in a bank's ground floor: stainless surround, hood, screen, keypad, card and cash slots."""
    z = WALL_FACE
    parts = [box("surround", (-0.38, 0.75, z - 0.02), (0.38, 1.85, z + 0.05), "ENV_Metal_Galvanised", bevel=0.01),
             box("hood", (-0.38, 1.78, z), (0.38, 1.86, z + 0.2), "ENV_Metal_Galvanised", bevel=0.01),
             box("screen", (-0.2, 1.38, z + 0.05), (0.2, 1.66, z + 0.058), "ENV_Screen"),
             box("keys", (-0.14, 1.08, z + 0.05), (0.14, 1.26, z + 0.1), "ENV_Plastic_Grey", bevel=0.006),
             box("shelf", (-0.3, 1.02, z + 0.05), (0.3, 1.06, z + 0.16), "ENV_Metal_Galvanised", bevel=0.005),
             box("cash", (-0.16, 0.9, z + 0.05), (0.16, 0.95, z + 0.06), "ENV_Plastic_Black"),
             box("card", (0.2, 1.3, z + 0.05), (0.28, 1.34, z + 0.07), "ENV_Plastic_Black")]
    return join("ENV_ATM", parts)


@recipe("ENV_AC_Unit", "ORIGINAL", smooth=40)
def ac_unit():
    """Split air-conditioning outdoor unit on wall brackets: rounded white case, round fan grille (rings and spokes
    over the dark fan), louvred side panel, insulated refrigerant pipes into a white trunking — the 21st-century
    addition every Spanish facade has somewhere."""
    z = WALL_FACE
    W, D = "ENV_PropMat_Blanco", "ENV_PropMat_Oscuro"
    fz = z + 0.36
    parts = [rbox("case", (-0.4, 0.0, z + 0.07), (0.4, 0.56, fz), W, r=0.028),
             cylinder("fan", (-0.1, 0.28, fz - 0.004), 0.2, 0.012, D, segments=24, axis="z"),
             rbox("sidepanel", (0.17, 0.06, fz - 0.004), (0.36, 0.5, fz + 0.004), D, r=0.004)]
    for k, rr in enumerate((0.2, 0.14, 0.08)):
        parts.append(torus(f"ring{k}", (-0.1, 0.28, fz + 0.006), rr, 0.009, W, axis="z", segments=24))
    parts.append(rbox("spokeH", (-0.3, 0.272, fz), (0.1, 0.288, fz + 0.012), W, r=0.004))
    parts.append(rbox("spokeV", (-0.108, 0.08, fz), (-0.092, 0.48, fz + 0.012), W, r=0.004))
    for k in range(8):
        y = 0.09 + k * 0.05
        parts.append(rbox(f"louvre{k}", (0.18, y, fz + 0.002), (0.35, y + 0.022, fz + 0.016), W, r=0.004))
    for sx in (-0.3, 0.3):
        parts.append(rbox(f"brk{sx}", (sx - 0.022, -0.06, z), (sx + 0.022, -0.02, z + 0.44), "ENV_PropMat_Galv", r=0.006))
        parts.append(rbox(f"brv{sx}", (sx - 0.022, -0.06, z), (sx + 0.022, 0.32, z + 0.035), "ENV_PropMat_Galv", r=0.006))
    parts.append(sweep("pipe1", [(0.4, 0.1, z + 0.14), (0.47, 0.1, z + 0.1), (0.47, 0.2, z + 0.04)], 0.018, D, segments=8))
    parts.append(sweep("pipe2", [(0.4, 0.16, z + 0.2), (0.47, 0.16, z + 0.12), (0.47, 0.26, z + 0.04)], 0.014, D, segments=8))
    parts.append(rbox("trunk", (0.43, 0.24, z), (0.51, 1.35, z + 0.06), W, r=0.01))
    return join("ENV_AC_Unit", parts)


@recipe("ENV_Alarm_Box", "ORIGINAL", smooth=40)
def alarm_box():
    """Burglar-alarm siren box over a shop: rounded white moulded case, coloured flash lens, red band."""
    z = WALL_FACE
    return join("ENV_Alarm_Box", [rbox("case", (-0.14, 0.0, z), (0.14, 0.34, z + 0.09), "ENV_PropMat_Blanco", r=0.03, seg=3),
                                  rbox("lens", (-0.065, 0.235, z + 0.07), (0.065, 0.31, z + 0.108), "ENV_Plastic_Blue", r=0.012),
                                  rbox("band", (-0.142, 0.1, z + 0.05), (0.142, 0.135, z + 0.094), "ENV_Plastic_Red", r=0.006)])


@recipe("ENV_Intercom", "ORIGINAL", smooth=35)
def intercom():
    """Door-entry panel beside a portal (portero automático): aluminium plate, speaker grille, a column of buttons."""
    z = WALL_FACE
    parts = [box("plate", (-0.07, 1.1, z), (0.07, 1.45, z + 0.025), "ENV_Metal_Galvanised", bevel=0.006),
             box("grille", (-0.045, 1.36, z + 0.025), (0.045, 1.42, z + 0.03), "ENV_Plastic_Black")]
    for k in range(4):
        parts.append(box(f"b{k}", (-0.03, 1.14 + k * 0.05, z + 0.025), (0.03, 1.175 + k * 0.05, z + 0.035), "ENV_Plastic_Grey"))
    return join("ENV_Intercom", parts)


@recipe("ENV_Extractor_Vent", "ORIGINAL", smooth=40)
def extractor_vent():
    """Kitchen/bathroom extractor outlet: rounded louvred plastic grille."""
    z = WALL_FACE
    parts = [rbox("frame", (-0.13, 0.0, z), (0.13, 0.26, z + 0.035), "ENV_Plastic_Grey", r=0.01)]
    for k in range(5):
        parts.append(rbox(f"l{k}", (-0.11, 0.03 + k * 0.045, z + 0.03), (0.11, 0.052 + k * 0.045, z + 0.05), "ENV_Plastic_Grey", r=0.005))
    return join("ENV_Extractor_Vent", parts)


@recipe("ENV_Telecom_Box", "ORIGINAL", smooth=40)
def telecom_box():
    """Telecom/electric junction box: rounded grey case with a lid seam, the cable dropping into it in a clip line."""
    z = WALL_FACE
    parts = [rbox("box", (-0.18, 0.0, z), (0.18, 0.46, z + 0.13), "ENV_Plastic_Grey", r=0.018),
             rbox("lid", (-0.16, 0.03, z + 0.12), (0.16, 0.43, z + 0.142), "ENV_Plastic_Grey", r=0.01),
             sweep("cable", [(0.1, 0.44, z + 0.07), (0.1, 0.6, z + 0.04), (0.1, 1.6, z + 0.035)], 0.012, "ENV_Rubber", segments=6)]
    for y in (0.8, 1.2):
        parts.append(rbox(f"clip{y}", (0.08, y, z), (0.12, y + 0.025, z + 0.055), "ENV_Plastic_Grey", r=0.005))
    return join("ENV_Telecom_Box", parts)


@recipe("ENV_Gas_Pipe", "ORIGINAL", smooth=35)
def gas_pipe():
    """Natural-gas riser: yellow painted pipe up the facade from a meter box, with clamps."""
    z = WALL_FACE
    parts = [box("meter", (-0.2, 0.3, z), (0.2, 0.75, z + 0.18), "ENV_Plastic_Grey", bevel=0.012),
             tube("riser", (0.12, 0.75, z + 0.06), (0.12, 3.1, z + 0.06), 0.017, "ENV_Plastic_Yellow", segments=8)]
    for y in (1.2, 2.0, 2.8):
        parts.append(box(f"clamp{y}", (0.09, y, z), (0.15, y + 0.03, z + 0.09), "ENV_Metal_Galvanised"))
    return join("ENV_Gas_Pipe", parts)


def _container(name, x, colour, lid):
    parts = [box(f"{name}b", (x - 0.55, 0.12, -0.5), (x + 0.55, 1.25, 0.5), colour, bevel=0.06),
             box(f"{name}l", (x - 0.58, 1.25, -0.53), (x + 0.58, 1.38, 0.53), lid, bevel=0.05),
             box(f"{name}m", (x - 0.2, 1.1, 0.5), (x + 0.2, 1.2, 0.54), "ENV_Plastic_Black")]
    for sx in (-0.4, 0.4):
        for sz in (-0.35, 0.35):
            parts.append(cylinder(f"{name}w{sx}{sz}", (x + sx, 0.06, sz), 0.06, 0.05, "ENV_Rubber", segments=10, axis="x"))
    return parts


@recipe("ENV_Recycling_Bins", "ORIGINAL", smooth=50)
def recycling_bins():
    """Street recycling point (contenedores de carga trasera): packaging (yellow), paper (blue) and general waste
    (grey) 800 l bins — tapered moulded bodies with rounded corners, overhanging domed lids, front ribs and label,
    handle bar, foot pedal and castors. Paint-worn plastic prop materials, grime at the foot."""
    parts = []
    # y: tapered body, overhanging domed lid, front ribs, handle, pedal, label, four castors
    parts += [vloft("ybody", [(0.17, rrect(0.5, 0.41, 0.09, -1.3)), (1.1, rrect(0.56, 0.46, 0.1, -1.3)),
                                     (1.14, rrect(0.58, 0.48, 0.1, -1.3))], "ENV_PropMat_Amarillo"),
              vloft("ylid", [(1.14, rrect(0.61, 0.52, 0.1, -1.3)), (1.2, rrect(0.61, 0.52, 0.1, -1.3)),
                                    (1.27, rrect(0.57, 0.46, 0.12, -1.3)), (1.31, rrect(0.5, 0.36, 0.12, -1.3))], "ENV_PropMat_Amarillo"),
              sweep("yhandle", [(-1.3 - 0.3, 1.2, 0.52), (-1.3 - 0.3, 1.2, 0.58), (-1.3 + 0.3, 1.2, 0.58), (-1.3 + 0.3, 1.2, 0.52)], 0.018, "ENV_PropMat_Oscuro", segments=8),
              rbox("ypedal", (-1.3 - 0.16, 0.16, 0.38), (-1.3 + 0.16, 0.2, 0.52), "ENV_PropMat_Oscuro", r=0.01),
              beam("ylabel", (0.72, 0.4425), (1.0, 0.4555), -1.3 - 0.2, -1.3 + 0.2, 0.012, "ENV_PropMat_Blanco", r=0.004)]
    for rx in (-0.34, 0.34):
        parts.append(beam(f"yrib{rx}", (0.25, 0.415 + 0.004), (1.08, 0.458 + 0.004), -1.3 + rx - 0.025, -1.3 + rx + 0.025, 0.03, "ENV_PropMat_Amarillo", r=0.01))
    for wx in (-0.38, 0.38):
        for wz in (-0.3, 0.3):
            parts.append(cylinder(f"yw{wx}{wz}", (-1.3 + wx, 0.085, wz), 0.085, 0.055, "ENV_PropMat_Oscuro", segments=14, axis="x"))
            parts.append(rbox(f"yfork{wx}{wz}", (-1.3 + wx - 0.04, 0.1, wz - 0.05), (-1.3 + wx + 0.04, 0.2, wz + 0.05), "ENV_PropMat_Oscuro", r=0.01))

    # b: tapered body, overhanging domed lid, front ribs, handle, pedal, label, four castors
    parts += [vloft("bbody", [(0.17, rrect(0.5, 0.41, 0.09, 0.0)), (1.1, rrect(0.56, 0.46, 0.1, 0.0)),
                                     (1.14, rrect(0.58, 0.48, 0.1, 0.0))], "ENV_PropMat_Azul"),
              vloft("blid", [(1.14, rrect(0.61, 0.52, 0.1, 0.0)), (1.2, rrect(0.61, 0.52, 0.1, 0.0)),
                                    (1.27, rrect(0.57, 0.46, 0.12, 0.0)), (1.31, rrect(0.5, 0.36, 0.12, 0.0))], "ENV_PropMat_Azul"),
              sweep("bhandle", [(0.0 - 0.3, 1.2, 0.52), (0.0 - 0.3, 1.2, 0.58), (0.0 + 0.3, 1.2, 0.58), (0.0 + 0.3, 1.2, 0.52)], 0.018, "ENV_PropMat_Oscuro", segments=8),
              rbox("bpedal", (0.0 - 0.16, 0.16, 0.38), (0.0 + 0.16, 0.2, 0.52), "ENV_PropMat_Oscuro", r=0.01),
              beam("blabel", (0.72, 0.4425), (1.0, 0.4555), 0.0 - 0.2, 0.0 + 0.2, 0.012, "ENV_PropMat_Blanco", r=0.004)]
    for rx in (-0.34, 0.34):
        parts.append(beam(f"brib{rx}", (0.25, 0.415 + 0.004), (1.08, 0.458 + 0.004), 0.0 + rx - 0.025, 0.0 + rx + 0.025, 0.03, "ENV_PropMat_Azul", r=0.01))
    for wx in (-0.38, 0.38):
        for wz in (-0.3, 0.3):
            parts.append(cylinder(f"bw{wx}{wz}", (0.0 + wx, 0.085, wz), 0.085, 0.055, "ENV_PropMat_Oscuro", segments=14, axis="x"))
            parts.append(rbox(f"bfork{wx}{wz}", (0.0 + wx - 0.04, 0.1, wz - 0.05), (0.0 + wx + 0.04, 0.2, wz + 0.05), "ENV_PropMat_Oscuro", r=0.01))

    # g: tapered body, overhanging domed lid, front ribs, handle, pedal, label, four castors
    parts += [vloft("gbody", [(0.17, rrect(0.5, 0.41, 0.09, 1.3)), (1.1, rrect(0.56, 0.46, 0.1, 1.3)),
                                     (1.14, rrect(0.58, 0.48, 0.1, 1.3))], "ENV_PropMat_Gris"),
              vloft("glid", [(1.14, rrect(0.61, 0.52, 0.1, 1.3)), (1.2, rrect(0.61, 0.52, 0.1, 1.3)),
                                    (1.27, rrect(0.57, 0.46, 0.12, 1.3)), (1.31, rrect(0.5, 0.36, 0.12, 1.3))], "ENV_PropMat_Gris"),
              sweep("ghandle", [(1.3 - 0.3, 1.2, 0.52), (1.3 - 0.3, 1.2, 0.58), (1.3 + 0.3, 1.2, 0.58), (1.3 + 0.3, 1.2, 0.52)], 0.018, "ENV_PropMat_Oscuro", segments=8),
              rbox("gpedal", (1.3 - 0.16, 0.16, 0.38), (1.3 + 0.16, 0.2, 0.52), "ENV_PropMat_Oscuro", r=0.01),
              beam("glabel", (0.72, 0.4425), (1.0, 0.4555), 1.3 - 0.2, 1.3 + 0.2, 0.012, "ENV_PropMat_Blanco", r=0.004)]
    for rx in (-0.34, 0.34):
        parts.append(beam(f"grib{rx}", (0.25, 0.415 + 0.004), (1.08, 0.458 + 0.004), 1.3 + rx - 0.025, 1.3 + rx + 0.025, 0.03, "ENV_PropMat_Gris", r=0.01))
    for wx in (-0.38, 0.38):
        for wz in (-0.3, 0.3):
            parts.append(cylinder(f"gw{wx}{wz}", (1.3 + wx, 0.085, wz), 0.085, 0.055, "ENV_PropMat_Oscuro", segments=14, axis="x"))
            parts.append(rbox(f"gfork{wx}{wz}", (1.3 + wx - 0.04, 0.1, wz - 0.05), (1.3 + wx + 0.04, 0.2, wz + 0.05), "ENV_PropMat_Oscuro", r=0.01))

    return join("ENV_Recycling_Bins", parts)


@recipe("ENV_Bike_Rack", "ORIGINAL", smooth=40)
def bike_rack():
    """Three galvanised Sheffield hoops (0.82 m, 0.8 m apart) on round base flanges, each with a low tie bar for the
    wheel: continuous bent 60 mm tube, thick enough to read from across the street."""
    parts = []
    for x in (-0.8, 0.0, 0.8):
        pts = [(x - 0.31, 0.0, 0.0), (x - 0.31, 0.6, 0.0)] + arc(x - 0.1, 0.6, 0.21, 180, 90, 6)[1:] + arc(x + 0.1, 0.6, 0.21, 90, 0, 6) + [(x + 0.31, 0.0, 0.0)]
        parts.append(sweep(f"hoop{x}", pts, 0.03, "ENV_PropMat_Galv", segments=12))
        parts.append(sweep(f"tie{x}", [(x - 0.31, 0.3, 0.0), (x + 0.31, 0.3, 0.0)], 0.018, "ENV_PropMat_Galv", segments=10))
        for fx in (x - 0.31, x + 0.31):
            parts.append(lathe(f"flange{fx}", [(0.075, 0.0), (0.075, 0.008), (0.045, 0.02), (0.0, 0.02)], "ENV_PropMat_Galv", segments=16, center=(fx, 0.0)))
    return join("ENV_Bike_Rack", parts)


@recipe("ENV_Solar_Panel", "ORIGINAL")
def solar_panel():
    """Thermal solar panel with tank on a small frame, for a flat bit of roof or a south slope."""
    parts = [box("panel", (-0.5, 0.35, -0.9), (0.5, 0.4, 0.9), "ENV_Screen", bevel=0.01),
             box("frame", (-0.52, 0.3, -0.92), (0.52, 0.35, 0.92), "ENV_Metal_Galvanised")]
    parts.append(cylinder("tank", (0.0, 0.62, -1.0), 0.2, 1.0, "ENV_Paint_White", segments=12, axis="x"))
    return join("ENV_Solar_Panel", parts)


@recipe("ENV_Chimney_Stone", "CREATE_DERIVED")
def chimney_stone():
    """Rendered/stone chimney stack with a projecting cap and two tiles laid as a little roof (casco chimney)."""
    parts = [box("stack", (-0.3, 0.0, -0.3), (0.3, 1.3, 0.3), "MI_Plaster", bevel=0.02),
             box("cap", (-0.38, 1.3, -0.38), (0.38, 1.38, 0.38), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.015)]
    for s in (-1, 1):
        parts.append(box(f"t{s}", (-0.34, 1.42, 0.0 if s > 0 else -0.34), (0.34, 1.47, 0.34 if s > 0 else 0.0), "MI_RoundTiles"))
    for sx in (-0.22, 0.22):
        parts.append(box(f"p{sx}", (sx - 0.05, 1.38, -0.05), (sx + 0.05, 1.44, 0.05), "MI_RockTrim", uv="band", band=ROCK_SLAB))
    return join("ENV_Chimney_Stone", parts)


@recipe("ENV_Chimney_Flue", "ORIGINAL", smooth=35)
def chimney_flue():
    """Galvanised stove flue with a conical rain cap and a guy wire stub (a later addition on many roofs)."""
    return join("ENV_Chimney_Flue", [cylinder("pipe", (0, 0.8, 0), 0.08, 1.6, "ENV_Metal_Galvanised", segments=10),
                                     lathe("cap", [(0.18, 1.72), (0.02, 1.9)], "ENV_Metal_Galvanised", segments=10),
                                     tube("brace", (0, 1.2, 0), (0.45, 0.2, 0.0), 0.008, "ENV_Metal_Galvanised", segments=4)])


def _plant_crown(prefix, rng_seed, n, r, h, mat, base=0.0, spread=1.0):
    import random
    rnd = random.Random(rng_seed)
    out = []
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0, r * 0.55) * spread
        s = rnd.uniform(0.55, 0.85) * r * 0.55
        out.append(lump(f"{prefix}{i}", (math.cos(a) * d, base + rnd.uniform(0, h - s), math.sin(a) * d), (s, s * 0.8, s), mat, seed=rng_seed + i, rough=0.15))
    return out


@recipe("ENV_Laurel_Stem", "ORIGINAL", smooth=40)
def laurel_stem():
    """Stem of a bay-laurel standard in a pot (laurel a la puerta); the clipped head is a Quaternius bush in the
    ENV_Plant_Laurel wrapper (modules.json)."""
    return join("ENV_Laurel_Stem", [sweep("stem", [(0, -0.02, 0), (0.01, 0.5, 0.0), (0.0, 0.95, 0.01)], 0.022, "ENV_Src_Bark_NormalTree", segments=8)])


@recipe("ENV_Pot_Glazed", "ORIGINAL", smooth=40)
def pot_glazed():
    """Glazed ceramic pot (blue by default; remapped to green/ochre): foot ring, round belly, collar, soil."""
    prof = [(0.0, 0.0), (0.11, 0.0), (0.125, 0.012), (0.13, 0.03), (0.17, 0.07), (0.205, 0.14), (0.222, 0.22), (0.21, 0.3),
            (0.185, 0.34), (0.19, 0.35), (0.2, 0.37), (0.196, 0.385), (0.18, 0.39), (0.172, 0.37)]
    return join("ENV_Pot_Glazed", [lathe("pot", prof, "ENV_Ceramic_Blue", segments=20),
                                   lathe("soil", [(0.0, 0.35), (0.175, 0.35)], "ENV_Soil", segments=20)])


@recipe("ENV_Pot_Tin", "ORIGINAL", smooth=35)
def pot_tin():
    """Old olive-oil tin reused as a planter (lata): square galvanised can with a rolled rim and a faded painted band."""
    parts = [rbox("tin", (-0.12, 0.0, -0.12), (0.12, 0.31, 0.12), "ENV_PropMat_Galv", r=0.012),
             rbox("band", (-0.123, 0.1, -0.123), (0.123, 0.22, 0.123), "ENV_PropMat_Amarillo", r=0.008),
             box("soil", (-0.108, 0.285, -0.108), (0.108, 0.3, 0.108), "ENV_Soil")]
    for k, (a, b) in enumerate((((-0.12, 0.315, -0.12), (0.12, 0.315, -0.12)), ((0.12, 0.315, -0.12), (0.12, 0.315, 0.12)),
                                ((0.12, 0.315, 0.12), (-0.12, 0.315, 0.12)), ((-0.12, 0.315, 0.12), (-0.12, 0.315, -0.12)))):
        parts.append(tube(f"rim{k}", a, b, 0.009, "ENV_PropMat_Galv", segments=8))
    return join("ENV_Pot_Tin", parts)


@recipe("ENV_Planter_Box", "CREATE_DERIVED", smooth=35)
def planter_box():
    """Timber window/doorstep box 0.8 m: corner posts, two rows of planks each side with a shadow gap, little feet and
    soil (flowers placed by the dresser). Kit MI_WoodTrim."""
    W = "MI_WoodTrim"
    parts = []
    for sx in (-0.38, 0.38):
        for sz in (-0.11, 0.11):
            parts.append(rbox(f"post{sx}{sz}", (sx - 0.028, 0.0, sz - 0.028), (sx + 0.028, 0.27, sz + 0.028), W, r=0.008, uv="band", band=WOOD_DARK))
    for i, (y0, y1) in enumerate(((0.03, 0.14), (0.148, 0.258))):
        for sz in (-1, 1):
            parts.append(rbox(f"pl{i}{sz}", (-0.36, y0, sz * 0.118 - 0.012), (0.36, y1, sz * 0.118 + 0.012), W, r=0.006, uv="band", band=WOOD_LIGHT))
        for sx in (-1, 1):
            parts.append(rbox(f"pe{i}{sx}", (sx * 0.378 - 0.012, y0, -0.1), (sx * 0.378 + 0.012, y1, 0.1), W, r=0.006, uv="band", band=WOOD_LIGHT))
    parts.append(box("soil", (-0.36, 0.2, -0.1), (0.36, 0.225, 0.1), "ENV_Soil"))
    return join("ENV_Planter_Box", parts)


@recipe("ENV_Trough_Stone", "CREATE_DERIVED", smooth=35)
def trough_stone():
    """Old granite trough (pila) reused as a planter by a door: a hollowed block with thick rounded rims, worn at the
    foot, soil inside (plants placed by the dresser at y = 0.36)."""
    M = "ENV_PropMat_Granito"
    parts = [rbox("floor", (-0.56, 0.0, -0.26), (0.56, 0.16, 0.26), M, r=0.035)]
    for sz in (-1, 1):
        parts.append(rbox(f"side{sz}", (-0.56, 0.1, sz * 0.26 - (0.1 if sz > 0 else 0.0)), (0.56, 0.44, sz * 0.26 + (0.0 if sz > 0 else 0.1)), M, r=0.035))
    for sx in (-1, 1):
        parts.append(rbox(f"end{sx}", (sx * 0.56 - (0.11 if sx > 0 else 0.0), 0.1, -0.2), (sx * 0.56 + (0.0 if sx > 0 else 0.11), 0.44, 0.2), M, r=0.035))
    parts.append(box("soil", (-0.46, 0.37, -0.17), (0.46, 0.39, 0.17), "ENV_Soil"))
    return join("ENV_Trough_Stone", parts)


@recipe("ENV_Door_Step", "CREATE_DERIVED")
def door_step():
    """Worn granite door step (umbral) 1.3 m, 15 cm: the portal meets the street on a stone, not on the paving."""
    return join("ENV_Door_Step", [box("step", (-0.65, -0.02, 0.0), (0.65, 0.15, 0.34), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.025)])


@recipe("ENV_Threshold_Slab", "CREATE_DERIVED")
def threshold_slab():
    """Flush stone slab in front of a shop or portal (walkable, 2 cm proud with a chamfer)."""
    return join("ENV_Threshold_Slab", [box("slab", (-0.8, -0.02, 0.0), (0.8, 0.02, 0.55), "MI_RockTrim", uv="band", band=ROCK_SLAB, bevel=0.012)])


@recipe("ENV_Drain_Outlet", "ORIGINAL", smooth=35)
def drain_outlet():
    """Drain outlet through the river wall: iron pipe mouth with a lip, a little stone apron under it."""
    return join("ENV_Drain_Outlet", [cylinder("pipe", (0, 0, 0.12), 0.14, 0.3, "ENV_Metal_Iron", segments=12, axis="z"),
                                     torus("lip", (0, 0, 0.27), 0.14, 0.025, "ENV_Metal_Iron", axis="z", segments=12),
                                     cylinder("dark", (0, 0, 0.26), 0.11, 0.02, "ENV_Plastic_Black", segments=12, axis="z")])


@recipe("ENV_Bench_Stone", "CREATE_DERIVED", smooth=35)
def bench_stone():
    """Stone bench (poyo) 1.8 m: one thick granite seat with a rounded front edge on two squat supports, plain dressed
    granite with no joints (a monolith, not masonry), damp at the foot, moss on top from the prop material."""
    parts = [rbox("seat", (-0.9, 0.35, -0.24), (0.9, 0.47, 0.24), "ENV_PropMat_Granito", r=0.04, seg=3)]
    for sx in (-0.6, 0.6):
        parts.append(rbox(f"leg{sx}", (sx - 0.17, 0.0, -0.2), (sx + 0.17, 0.37, 0.2), "ENV_PropMat_Granito", r=0.03))
    return join("ENV_Bench_Stone", parts)


@recipe("ENV_Fountain_Monument", "CREATE_DERIVED", smooth=35)
def fountain_monument():
    """The plaza's landmark (owner: "algo que haga que el jugador diga: estoy aquí"): a northern-Spanish four-spout
    plaza fountain — an open octagonal basin of sandstone ashlar with a granite coping and the water showing, on two
    granite steps; a moulded granite pier with four bronze masks and spouts pouring into the basin; on top, a
    cast-iron five-lantern candelabra that lights the plaza at night. ~9 m across the steps, 7.4 m high. Invented;
    no real monument copied. (Cohesion pass: the old coping was a solid lid, so the basin read as a plinth, and the
    streams read as black legs.)"""
    parts = []
    n = 8

    def ring(r, rot=math.pi / 8):
        return [(r * math.cos(rot + 2 * math.pi * i / n), r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]

    def prism(name, pts, y0, y1, mat):
        bm = bmesh.new()
        lo = [bm.verts.new(U(x, y0, z)) for x, z in pts]
        hi = [bm.verts.new(U(x, y1, z)) for x, z in pts]
        bm.faces.new(lo[::-1])
        bm.faces.new(hi)
        for i in range(len(pts)):
            bm.faces.new([lo[i], lo[(i + 1) % len(pts)], hi[(i + 1) % len(pts)], hi[i]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = new_object(name, bm)
        ob.data.materials.append(material(mat))
        do_bevel(ob, 0.03, 2)
        uv_box(ob)
        return ob

    gr = "ENV_PropMat_Granito"
    parts.append(prism("step1", ring(4.4), 0.0, 0.16, gr))
    parts.append(prism("step2", ring(3.95), 0.16, 0.32, gr))
    # basin: ashlar wall with a plinth course, rounded granite coping as an open ring, water 20 cm below the coping
    parts.append(revolve_poly("basin_wall", [(3.46, 0.32), (3.46, 0.44), (3.38, 0.48), (3.38, 0.93), (2.99, 0.93), (2.99, 0.32)],
                              "ENV_Mason_Silleria_Arenisca_G", closed=True))
    parts.append(revolve_poly("coping", [(3.4, 0.92), (3.53, 0.96), (3.56, 1.02), (3.53, 1.08), (3.44, 1.11), (3.02, 1.11),
                                         (2.96, 1.08), (2.95, 0.98), (2.99, 0.92)], gr, closed=True))
    parts.append(prism("water", ring(3.0), 0.32, 0.9, "ENV_Water_Port"))
    # pier: plinth in the water, torus, shaft with a collar that carries the masks, flared capital
    parts.append(revolve_poly("pier", [(0.0, 0.32), (0.82, 0.32), (0.82, 1.0), (0.74, 1.05), (0.76, 1.12), (0.66, 1.2),
                                        (0.56, 1.28), (0.53, 1.8), (0.6, 1.86), (0.6, 2.3), (0.52, 2.36), (0.48, 3.2),
                                        (0.55, 3.26), (0.66, 3.38), (0.74, 3.5), (0.76, 3.62), (0.62, 3.68), (0.0, 3.68)], gr))
    for k in range(4):
        a = k * math.pi / 2
        x, z = math.cos(a), math.sin(a)
        ap = 0.6 * math.cos(math.pi / 8)          # the collar's flat
        parts.append(sphere(f"mask{k}", (x * ap, 2.08, z * ap), 0.14, "ENV_Bronze", segments=12))
        tip = (x * (ap + 0.38), 2.02, z * (ap + 0.38))
        parts.append(sweep(f"spout{k}", [(x * (ap + 0.05), 2.06, z * (ap + 0.05)), (x * (ap + 0.24), 2.05, z * (ap + 0.24)), tip], 0.032, "ENV_Bronze", segments=10))
        parts.append(water_jet(f"jet{k}", tip, (x, z), 0.75, 0.9))
    # candelabra: iron column, four curved arms with lanterns and a crowning lantern
    parts.append(lathe("post", [(0.18, 3.68), (0.18, 3.8), (0.1, 3.95), (0.07, 5.8), (0.11, 5.9), (0.13, 6.0)], "ENV_Metal_Iron", segments=10))

    def lantern(prefix, x, y, z):
        return [lathe(prefix + "b", [(0.07, y), (0.13, y + 0.06), (0.13, y + 0.1)], "ENV_Metal_Iron", segments=6, center=(x, z)),
                lathe(prefix + "g", [(0.12, y + 0.1), (0.15, y + 0.45), (0.0, y + 0.46)], "ENV_Lamp_Glass", segments=6, center=(x, z)),
                lathe(prefix + "c", [(0.18, y + 0.45), (0.05, y + 0.62), (0.0, y + 0.7)], "ENV_Metal_Iron", segments=6, center=(x, z))]

    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        x, z = math.cos(a) * 0.95, math.sin(a) * 0.95
        pts = [(x * t / 6, 5.2 + 0.55 * math.sin(t / 6 * math.pi * 0.8), z * t / 6) for t in range(7)]
        parts.append(sweep(f"arm{k}", pts, 0.03, "ENV_Metal_Iron", segments=8))
        parts += lantern(f"l{k}", x, pts[-1][1] - 0.05, z)
    parts += lantern("ltop", 0, 6.0, 0)
    return join("ENV_Fountain_Monument", parts)


@recipe("ENV_Tree_Bench_Ring", "CREATE_DERIVED", smooth=35)
def tree_bench_ring():
    """Round granite bench around the plaza's singular tree (the shade where the old men sit): twelve rounded seat
    stones on six squat supports, inner radius 1.3 m. The tree itself is a Quaternius CommonTree (modules.json)."""
    parts = []
    segs = 12
    for k in range(segs):
        a0, a1 = 2 * math.pi * k / segs + 0.004, 2 * math.pi * (k + 1) / segs - 0.004
        bm = bmesh.new()
        vs = []
        for r in (1.3, 1.78):
            for a in (a0, a1):
                for y in (0.36, 0.47):
                    vs.append(bm.verts.new(U(r * math.cos(a), y, r * math.sin(a))))
        for f in ((0, 2, 3, 1), (4, 5, 7, 6), (1, 3, 7, 5), (0, 4, 6, 2), (0, 1, 5, 4), (2, 6, 7, 3)):
            bm.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = new_object(f"seat{k}", bm)
        ob.data.materials.append(material("ENV_PropMat_Granito"))
        do_bevel(ob, 0.03, 2)
        uv_box(ob)
        parts.append(ob)
        if k % 2 == 0:
            mid = a1
            cx, cz = 1.54 * math.cos(mid), 1.54 * math.sin(mid)
            parts.append(rbox(f"leg{k}", (cx - 0.15, 0.0, cz - 0.15), (cx + 0.15, 0.38, cz + 0.15), "ENV_PropMat_Granito", r=0.03))
    return join("ENV_Tree_Bench_Ring", parts)


@recipe("ENV_Parapet_Stone_2m", "CREATE_DERIVED")
def parapet_stone():
    """Bridge/river parapet 2 m: masonry body (kit rubble slot, remapped per bridge) under a rounded dressed coping
    with drip; 1.0 m high, 0.45 m thick. Local frame: runs along x, centred on z = 0, sits on y = 0."""
    parts = [box("body", (-1.0, 0.0, -0.2), (1.0, 0.86, 0.2), "MI_UnevenBrick", uv="box"),
             box("cope", (-1.0, 0.86, -0.26), (1.0, 1.0, 0.26), "MI_RockTrim", uv="band", band=ROCK_ASHLAR, bevel=0.035)]
    return join("ENV_Parapet_Stone_2m", parts)


@recipe("ENV_Clock_Face", "ORIGINAL")
def clock_face():
    """Tower clock: 1.3 m white enamel dial in a stone ring, twelve iron hour marks and two hands (at 10 past 4)."""
    z = 0.0
    parts = [cylinder("ring", (0, 0, z + 0.06), 0.78, 0.12, "MI_RockTrim", segments=24, axis="z"),
             cylinder("dial", (0, 0, z + 0.125), 0.65, 0.02, "ENV_Paint_White", segments=24, axis="z")]
    for k in range(12):
        a = k * math.pi / 6
        r0, r1 = 0.5, 0.6
        parts.append(tube(f"m{k}", (math.sin(a) * r0, math.cos(a) * r0, z + 0.14), (math.sin(a) * r1, math.cos(a) * r1, z + 0.14), 0.022 if k % 3 == 0 else 0.012, "ENV_Metal_Iron", segments=4))
    for ang, L, w in ((math.radians(120 + 5), 0.34, 0.025), (math.radians(60), 0.5, 0.016)):
        parts.append(tube(f"hand{L}", (0, 0, z + 0.15), (math.sin(ang) * L, math.cos(ang) * L, z + 0.15), w, "ENV_Metal_Iron", segments=4))
    parts.append(cylinder("hub", (0, 0, z + 0.16), 0.04, 0.03, "ENV_Metal_Iron", segments=10, axis="z"))
    return join("ENV_Clock_Face", parts)


@recipe("ENV_Bell", "ORIGINAL", smooth=35)
def bell():
    """Bronze bell with yoke for the belfry openings."""
    prof = [(0.0, 0.62), (0.12, 0.6), (0.16, 0.5), (0.18, 0.3), (0.24, 0.12), (0.3, 0.02), (0.31, 0.0), (0.27, 0.0)]
    return join("ENV_Bell", [lathe("bell", prof, "ENV_Bronze", segments=16), box("yoke", (-0.4, 0.62, -0.06), (0.4, 0.74, 0.06), "MI_WoodTrim", uv="band", band=WOOD_DARK)])


@recipe("ENV_Weathervane", "ORIGINAL")
def weathervane():
    """Iron weathervane: rod, cardinal cross and an arrow with a cockerel-less swallowtail vane."""
    parts = [tube("rod", (0, 0, 0), (0, 1.3, 0), 0.015, "ENV_Metal_Iron", segments=6),
             tube("ns", (0, 0.7, -0.35), (0, 0.7, 0.35), 0.01, "ENV_Metal_Iron", segments=4),
             tube("ew", (-0.35, 0.7, 0), (0.35, 0.7, 0), 0.01, "ENV_Metal_Iron", segments=4),
             tube("arrow", (-0.5, 1.15, 0), (0.55, 1.15, 0), 0.012, "ENV_Metal_Iron", segments=4),
             box("tail", (-0.55, 1.05, -0.005), (-0.3, 1.28, 0.005), "ENV_Metal_Iron"),
             sphere("ball", (0, 0.95, 0), 0.05, "ENV_Metal_Iron", segments=8)]
    return join("ENV_Weathervane", parts)



@recipe("ENV_Stain_Quad", "ORIGINAL")
def stain_quad():
    """Weathering decal quad 1 x 1 m (x centred, y 0..1) lying 4 mm off the wall face; the dresser picks the stain
    cell by material (ENV_Stain_*) and scales it to the cause (a downpipe foot, a sill, a corner, a repair)."""
    return join("ENV_Stain_Quad", [fix_face_normal(face_quad("q", -0.5, 0.5, 0.0, 1.0, WALL_FACE + 0.004, "ENV_Stain_Downpipe"), (0, 0, 1))])

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
        if name in SMOOTH:
            for o in bpy.context.selected_objects:
                o.select_set(False)
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(SMOOTH[name]), keep_sharp_edges=True)
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
