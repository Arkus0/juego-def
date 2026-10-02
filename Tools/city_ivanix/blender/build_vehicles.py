"""Vehicles for the town in the "Dreamcast+" manner (Docs/design/CITY_STYLE_DCPLUS.md): clean silhouettes, few polygons
well placed, and every part painted (tools/vehicle_textures.py): the body paint carries its horizon line and sill
shadow, the glass its sky and head restraints, lights their reflectors, plates their numbers, wheels their steel rims.
UVs are laid here by projection (see vehicle_textures.py for the conventions). Generic designs of Spanish streets
around 2000; no real make.

Run:  blender -b -P build_vehicles.py -- <out_dir>
Exports one FBX per model (Y up, metres) and a Workbench preview PNG of each.
"""

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

OUT = Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else Path.cwd()
OUT.mkdir(parents=True, exist_ok=True)

COLORS = {
    "Paint": (0.62, 0.10, 0.08, 1), "Glass": (0.06, 0.09, 0.12, 1), "Plastic": (0.10, 0.10, 0.11, 1),
    "Rubber": (0.04, 0.04, 0.045, 1), "Hub": (0.62, 0.64, 0.66, 1), "LightFront": (0.92, 0.92, 0.86, 1),
    "LightRear": (0.75, 0.06, 0.05, 1), "Plate": (0.95, 0.95, 0.93, 1), "Chrome": (0.75, 0.76, 0.78, 1),
    "Grille": (0.1, 0.1, 0.11, 1), "TX_VanDecal_0": (0.2, 0.5, 0.25, 1),
}


def uv_set(ob, fn):
    """UVs from a function of the vertex position (object space) for every loop of the mesh."""
    me = ob.data
    uvl = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            uvl.data[li].uv = fn(me.vertices[me.loops[li].vertex_index].co)


def uv_planar(ob, axes, flip_u=False):
    """Each piece's own face normalised to 0..1 on two axes (0 x, 1 y, 2 z) of its object space."""
    a, b = axes
    cs = [v.co for v in ob.data.vertices]
    lo = [min(c[i] for c in cs) for i in range(3)]
    hi = [max(c[i] for c in cs) for i in range(3)]
    def f(c):
        u = (c[a] - lo[a]) / max(1e-6, hi[a] - lo[a])
        return (1 - u if flip_u else u, (c[b] - lo[b]) / max(1e-6, hi[b] - lo[b]))
    uv_set(ob, f)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = COLORS.get(name, (0.5, 0.5, 0.5, 1))
    return m


def ring(sec):
    """Cross-section at one station: 10 points, y >= 0 then mirrored (counterclockwise seen from +x)."""
    hw, zb, zbelt, ztop, thw = sec["hw"], sec["zb"], sec["zbelt"], sec["ztop"], sec["thw"]
    right = [(hw * 0.90, zb), (hw, zb + 0.22), (hw, zbelt), (thw, ztop - 0.05), (thw * 0.55, ztop)]
    left = [(-y, z) for (y, z) in reversed(right)]
    return right + left


def body(name, sections, glass_spans, pillar_xs=(), rear_window=True):
    """Lofted body. glass_spans: station intervals (x_from, x_to) carrying glass from the beltline to the roof edge;
    the windscreen and the rear window are the top faces of the first and last span. pillar_xs: stations whose
    following interval stays body colour (a pillar)."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    bm = bmesh.new()
    rings = [[bm.verts.new((sec["x"], y, z)) for (y, z) in ring(sec)] for sec in sections]
    n = len(rings[0])
    tags = []
    for i, (a, b) in enumerate(zip(rings[:-1], rings[1:])):
        for k in range(n):
            f = bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
            tags.append((f, i, k))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for mname in ("Paint", "Glass", "Plastic"):
        me.materials.append(material(mname))
    xs = [s_["x"] for s_ in sections]
    side_glass = {2, 6}          # ring segment p2->p3 on each side (beltline to roof edge)
    top = {3, 4, 5}              # roof edge and top centre
    first = (glass_spans[0][0] + glass_spans[0][1]) / 2
    last = (glass_spans[-1][0] + glass_spans[-1][1]) / 2
    for f, i, k in tags:
        x0, x1 = xs[i], xs[i + 1]
        mid = (x0 + x1) / 2
        in_glass = any(min(a_, b_) - 1e-3 <= mid <= max(a_, b_) + 1e-3 for (a_, b_) in glass_spans)
        pillar = any(abs(x0 - px) < 1e-3 for px in pillar_xs)
        if in_glass and not pillar and k in side_glass:
            f.material_index = 1
        if k in top and (abs(mid - first) < 1e-3 or (rear_window and abs(mid - last) < 1e-3)):
            f.material_index = 1
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    x_lo, x_hi = min(xs), max(xs)
    uv_set(ob, lambda c: ((c.x - x_lo) / (x_hi - x_lo), c.z / 2.0))
    return ob


def box(name, loc, size, mat, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(material(mat))
    if bevel > 0:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        mod = ob.modifiers.new('bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


def wheel(name, loc, r=0.30, w=0.19):
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=r, depth=w, location=loc, rotation=(math.pi / 2, 0, 0))
    t = bpy.context.active_object
    t.name = name
    t.data.materials.append(material("Rubber"))
    t.data.materials.append(material("Hub"))
    for f in t.data.polygons:
        if abs(f.normal.y) > 0.9:
            f.material_index = 1
        f.use_smooth = abs(f.normal.y) < 0.9
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    uv_planar(t, (0, 2))
    return t


def flare(name, x, s, hw, r=0.40, z=0.30):
    """Wheel arch: a dark half ring standing proud of the body side."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=0.06, location=(x, s * (hw + 0.005), z), rotation=(math.pi / 2, 0, 0))
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < z - 0.02], context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.materials.append(material("Plastic"))
    return ob


def details(front_x, rear_x, belt_f, belt_r, hw, wheel_xs, doors):
    parts = []
    for s in (-1, 1):
        hl = box("hl", (front_x + 0.01, s * (hw - 0.27), belt_f - 0.11), (0.04, 0.30, 0.13), "LightFront")
        uv_planar(hl, (1, 2), flip_u=s > 0)                     # the indicator outboard on both sides
        tl = box("tl", (rear_x - 0.01, s * (hw - 0.16), belt_r - 0.05), (0.04, 0.20, 0.22), "LightRear")
        uv_planar(tl, (1, 2))
        parts += [hl, tl]
        parts.append(box("mirror", (front_x - 1.02, s * (hw + 0.08), belt_f + 0.17), (0.13, 0.08, 0.10), "Plastic"))
        # the side rubbing strip, the door gaps and handles: a 1990s car reads by them
        parts.append(box("moldura", ((front_x + rear_x) / 2, s * (hw + 0.012), 0.52), (front_x - rear_x - 0.6, 0.025, 0.07), "Plastic"))
        for dx in doors:
            parts.append(box("gap", (dx, s * (hw + 0.004), 0.58), (0.012, 0.012, 0.66), "Plastic"))
            parts.append(box("handle", (dx - 0.18, s * (hw + 0.012), 0.74), (0.12, 0.02, 0.03), "Chrome"))
        for wx in wheel_xs:
            parts.append(flare("arch", wx, s, hw))
    parts.append(box("bumperF", (front_x + 0.03, 0, 0.32), (0.12, 2 * hw + 0.04, 0.20), "Plastic", bevel=0.045))
    parts.append(box("bumperR", (rear_x - 0.03, 0, 0.34), (0.12, 2 * hw + 0.02, 0.20), "Plastic", bevel=0.045))
    gr = box("grille", (front_x + 0.012, 0, belt_f - 0.11), (0.04, 0.44, 0.10), "Grille")
    uv_planar(gr, (1, 2))
    pf = box("plateF", (front_x + 0.095, 0, 0.33), (0.02, 0.52, 0.11), "Plate")
    uv_planar(pf, (1, 2))                                        # seen from the front: +y is the viewer's right
    pr = box("plateR", (rear_x - 0.095, 0, 0.55), (0.02, 0.52, 0.11), "Plate")
    uv_planar(pr, (1, 2), flip_u=True)                           # seen from behind: -y is the viewer's right
    parts += [gr, pf, pr]
    return parts


def decal(x0, x1, z0, z1, sec, side):
    """Trade lettering on the van's side panel, following the inward slope of the side above the beltline."""
    def y_at(z):
        t = (z - sec["zbelt"]) / max(1e-6, (sec["ztop"] - 0.05) - sec["zbelt"])
        return sec["hw"] + (sec["thw"] - sec["hw"]) * min(1.0, max(0.0, t)) + 0.008
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.verify()
    vs = [bm.verts.new((x, side * y_at(z), z)) for (x, z) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1))]
    f = bm.faces.new(vs if side < 0 else list(reversed(vs)))
    for loop in f.loops:
        c = loop.vert.co
        u = (c.x - x0) / (x1 - x0)
        loop[uvl].uv = (u if side < 0 else 1 - u, (c.z - z0) / (z1 - z0))
    me = bpy.data.meshes.new("decal")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("decal", me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(material("TX_VanDecal_0"))
    return ob


def uv_sanitize(objs):
    """One UV layer named UVMap on every part before joining (a part whose layer has another name would come out of
    the join with its UVs zeroed in the first channel)."""
    for o in objs:
        if o.type != "MESH":
            continue
        ls = o.data.uv_layers
        if len(ls) == 0:
            ls.new(name="UVMap")
        ls[0].name = "UVMap"
        while len(ls) > 1:
            ls.remove(ls[1])


def join(objs, name):
    uv_sanitize(objs)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.join()
    ob = bpy.context.active_object
    ob.name = name
    # front of every prop faces Blender -Y (Unity +Z after the FBX axis conversion), origin on the ground
    ob.rotation_euler = (0, 0, -math.pi / 2)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(38))
    return ob


def preview(path):
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_WORKBENCH"
    scn.display.shading.light = "STUDIO"
    scn.display.shading.color_type = "MATERIAL"
    scn.display.shading.show_shadows = True
    scn.render.resolution_x, scn.render.resolution_y = 900, 520
    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (5.2, -4.6, 2.4)
    cam.rotation_euler = (Vector((0, 0, 0.7)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 45
    scn.camera = cam
    scn.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def export(ob, path):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                             axis_forward="-Z", axis_up="Y", object_types={"MESH"}, mesh_smooth_type="FACE", bake_space_transform=True)


def hatch():
    reset()
    S = [
        dict(x=1.93, hw=0.76, zb=0.24, zbelt=0.60, ztop=0.66, thw=0.68),
        dict(x=1.80, hw=0.81, zb=0.20, zbelt=0.70, ztop=0.78, thw=0.74),
        dict(x=0.95, hw=0.83, zb=0.19, zbelt=0.80, ztop=0.88, thw=0.78),
        dict(x=0.88, hw=0.83, zb=0.19, zbelt=0.81, ztop=0.94, thw=0.77),
        dict(x=0.22, hw=0.83, zb=0.19, zbelt=0.86, ztop=1.40, thw=0.64),
        dict(x=0.12, hw=0.83, zb=0.19, zbelt=0.86, ztop=1.41, thw=0.64),
        dict(x=-0.52, hw=0.83, zb=0.19, zbelt=0.87, ztop=1.42, thw=0.64),
        dict(x=-0.62, hw=0.83, zb=0.19, zbelt=0.87, ztop=1.42, thw=0.64),
        dict(x=-1.22, hw=0.83, zb=0.19, zbelt=0.88, ztop=1.42, thw=0.64),
        dict(x=-1.38, hw=0.83, zb=0.19, zbelt=0.88, ztop=1.40, thw=0.65),
        dict(x=-1.78, hw=0.82, zb=0.20, zbelt=0.86, ztop=1.18, thw=0.66),
        dict(x=-1.93, hw=0.79, zb=0.24, zbelt=0.80, ztop=1.00, thw=0.66),
    ]
    b = body("Body", S, glass_spans=[(0.88, 0.22), (0.12, -1.22), (-1.38, -1.78)], pillar_xs=(0.22, -0.52, -1.22))
    parts = [b] + details(1.93, -1.93, 0.66, 0.84, 0.83, (1.22, -1.22), doors=(0.10, -0.95))
    for x in (1.22, -1.22):
        for s_ in (-1, 1):
            parts.append(wheel("w", (x, s_ * 0.72, 0.30)))
    ob = join(parts, "CITY_Car_Hatch")
    preview(OUT / "CITY_Car_Hatch_preview.png")
    export(ob, OUT / "CITY_Car_Hatch.fbx")


def van():
    reset()
    S = [
        dict(x=2.05, hw=0.79, zb=0.26, zbelt=0.66, ztop=0.72, thw=0.70),
        dict(x=1.90, hw=0.84, zb=0.22, zbelt=0.78, ztop=0.86, thw=0.78),
        dict(x=1.25, hw=0.86, zb=0.21, zbelt=0.92, ztop=1.02, thw=0.80),
        dict(x=1.18, hw=0.86, zb=0.21, zbelt=0.93, ztop=1.08, thw=0.80),
        dict(x=0.65, hw=0.87, zb=0.21, zbelt=0.98, ztop=1.80, thw=0.80),
        dict(x=0.55, hw=0.87, zb=0.21, zbelt=0.98, ztop=1.81, thw=0.80),
        dict(x=-0.20, hw=0.87, zb=0.21, zbelt=0.98, ztop=1.82, thw=0.80),
        dict(x=-1.95, hw=0.87, zb=0.21, zbelt=0.98, ztop=1.82, thw=0.80),
        dict(x=-2.10, hw=0.85, zb=0.24, zbelt=0.96, ztop=1.78, thw=0.78),
    ]
    b = body("Body", S, glass_spans=[(1.18, 0.65), (0.55, -0.20)], pillar_xs=(0.65,), rear_window=False)
    parts = [b] + details(2.05, -2.10, 0.74, 0.96, 0.87, (1.35, -1.40), doors=(0.55, -0.25))
    parts += [decal(-1.85, -0.35, 1.08, 1.62, S[6], side) for side in (-1, 1)]
    for x in (1.35, -1.40):
        for s_ in (-1, 1):
            parts.append(wheel("w", (x, s_ * 0.75, 0.31), r=0.31))
    ob = join(parts, "CITY_Van")
    preview(OUT / "CITY_Van_preview.png")
    export(ob, OUT / "CITY_Van.fbx")


hatch()
van()
print("VEHICLES_DONE", OUT)
