"""Street and port props in the Dreamcast+ manner: each one a single entity (nothing in it can collide with itself).
Fishing boat (variants by name/colour in Unity), market stall, bar terrace set, butane bottle, Correos letter box,
gumball machine. Materials named by role or by texture (TX_*), mapped to DC Plus materials in Unity.

Run:  blender -b -P build_street.py -- <out_dir>
"""

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

OUT = Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else Path.cwd()
OUT.mkdir(parents=True, exist_ok=True)
TEX = OUT.parent / "Textures"
C = {
    "HullWhite": (0.93, 0.92, 0.88, 1), "HullBand": (0.12, 0.28, 0.6, 1), "Antifouling": (0.55, 0.12, 0.08, 1), "DeckWood": (0.55, 0.4, 0.25, 1),
    "CabinWhite": (0.94, 0.93, 0.9, 1), "Glass": (0.08, 0.1, 0.13, 1), "Mast": (0.25, 0.22, 0.2, 1), "Metal": (0.62, 0.64, 0.66, 1),
    "TableWood": (0.62, 0.48, 0.32, 1), "Cloth": (0.85, 0.82, 0.74, 1), "PlasticWhite": (0.95, 0.95, 0.93, 1), "Alu": (0.78, 0.79, 0.8, 1),
    "ParasolCanvas": (0.9, 0.88, 0.8, 1), "Butane": (0.95, 0.42, 0.08, 1), "Correos": (0.98, 0.78, 0.05, 1), "CorreosBlue": (0.08, 0.2, 0.5, 1),
    "Gumball": (0.1, 0.55, 0.25, 1), "GumGlass": (0.75, 0.82, 0.86, 1), "Crate": (0.66, 0.5, 0.32, 1), "Rubber": (0.05, 0.05, 0.05, 1),
    "BootTop": (0.1, 0.1, 0.11, 1), "CapRail": (0.42, 0.3, 0.2, 1), "BulwarkIn": (0.86, 0.85, 0.8, 1), "Strake": (0.2, 0.19, 0.18, 1),
    "Ropa_A": (0.16, 0.22, 0.42, 1), "Ropa_B": (0.62, 0.14, 0.12, 1), "Ropa_C": (0.86, 0.82, 0.72, 1), "Ropa_D": (0.22, 0.4, 0.26, 1),
    "Queso": (0.92, 0.84, 0.58, 1), "Miel": (0.78, 0.46, 0.08, 1), "TapaMiel": (0.86, 0.72, 0.2, 1), "Botella": (0.42, 0.52, 0.36, 1),
    "Corcho": (0.6, 0.45, 0.3, 1), "Carton": (0.7, 0.56, 0.38, 1),
    "Salvavidas": (0.95, 0.38, 0.08, 1), "NetGreen": (0.2, 0.36, 0.28, 1), "Rope": (0.72, 0.62, 0.42, 1), "LightFront": (0.95, 0.94, 0.88, 1),
}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    if name.startswith("TX_"):
        m.use_nodes = True
        img = bpy.data.images.load(str(TEX / f"{name}.png"), check_existing=True)
        tn = m.node_tree.nodes.new("ShaderNodeTexImage")
        tn.image = img
        m.node_tree.links.new(tn.outputs["Color"], m.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    else:
        m.diffuse_color = C.get(name, (0.5, 0.5, 0.5, 1))
    return m


def box(loc, size, m, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        md = ob.modifiers.new("b", "BEVEL")
        md.width, md.segments = bevel, 2
        bpy.ops.object.modifier_apply(modifier=md.name)
    ob.data.materials.append(mat(m))
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=1.0)
    bpy.ops.object.mode_set(mode="OBJECT")
    return ob


def cyl(loc, r, h, m, rot=(0, 0, 0), verts=12, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.data.materials.append(mat(m))
    for f in ob.data.polygons:
        f.use_smooth = True
    return ob


def quad(corners, m, uvs=((0, 0), (1, 0), (1, 1), (0, 1))):
    me = bpy.data.meshes.new("q")
    bm = bmesh.new()
    vs = [bm.verts.new(c) for c in corners]
    f = bm.faces.new(vs)
    uv = bm.loops.layers.uv.verify()
    for loop, u in zip(f.loops, uvs):
        loop[uv].uv = u
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("q", me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat(m))
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


def join(objs, name, turn=0.0):
    """Join the parts, bake every transform (origin on the ground at 0,0,0) and turn the piece so its front faces
    Blender -Y, i.e. Unity +Z after the FBX axis conversion."""
    uv_sanitize(objs)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    ob = bpy.context.active_object
    ob.name = name
    ob.rotation_euler = (0, 0, turn)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
    return ob


def export(ob, path):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                             axis_forward="-Z", axis_up="Y", object_types={"MESH"}, mesh_smooth_type="FACE", bake_space_transform=True)


def preview(path, target, dist):
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_WORKBENCH"
    scn.display.shading.light = "STUDIO"
    scn.display.shading.color_type = "TEXTURE"
    scn.display.shading.show_shadows = True
    scn.render.resolution_x, scn.render.resolution_y = 720, 480
    cd = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cd)
    bpy.context.collection.objects.link(cam)
    t = Vector(target)
    cam.location = t + Vector((dist * 0.8, -dist * 0.62, dist * 0.42))
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    scn.camera = cam
    scn.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def _cr(p0, p1, p2, p3, t):
    """Catmull-Rom between p1 and p2."""
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


def _stations(ctrl, per=4):
    """Smooth hull stations from a few control stations (each a tuple of floats)."""
    out = []
    n = len(ctrl)
    for i in range(n - 1):
        p0, p1, p2, p3 = ctrl[max(0, i - 1)], ctrl[i], ctrl[i + 1], ctrl[min(n - 1, i + 2)]
        for k in range(per):
            t = k / per
            out.append(tuple(_cr(a, b, c, d, t) for a, b, c, d in zip(p0, p1, p2, p3)))
    out.append(ctrl[-1])
    return out


def boat():
    """A Cantabrian inshore fishing boat (lancha, ~7 m) the way the era modelled it: a hull lofted through smooth
    stations with a real bulwark (outer face, capping rail, inner face down to the deck), antifouling exactly below the
    waterline, a dark boot-top, white topsides, the coloured sheer band on the bulwark, a rubbing strake that follows
    the hull, the boat's name painted at the bow, a wheelhouse with windows all round, mast with crosstree and lamp,
    tyre fenders, the net drum at the stern and a lifebuoy. Waterline at z = 0, bow +X before the turn."""
    reset()
    #        x,    half-beam, sheer z, keel z, bulwark h
    ctrl = [(-3.45, 1.02, 0.80, -0.42, 0.30), (-2.6, 1.20, 0.76, -0.55, 0.30), (-1.2, 1.30, 0.74, -0.64, 0.30),
            (0.4, 1.26, 0.78, -0.64, 0.32), (1.8, 1.0, 0.90, -0.56, 0.36), (2.9, 0.52, 1.08, -0.42, 0.40), (3.55, 0.03, 1.24, -0.18, 0.42)]
    st = _stations(ctrl, 4)
    bm = bmesh.new()
    rings, sheer, deckz_at = [], [], []
    for x, b, sh, kd, bw in st:
        b = max(b, 0.03)
        half = [(0.0, kd), (0.3 * b, kd * 0.84), (0.62 * b, kd * 0.52), (0.86 * b, kd * 0.2), (0.95 * b, 0.0),
                (0.985 * b, 0.12), (1.0 * b, 0.42 * sh), (1.02 * b, sh), (1.035 * b, sh + bw),
                (max(0.0, 1.035 * b - 0.09), sh + bw), (max(0.0, 1.035 * b - 0.09), sh - 0.04), (0.0, sh - 0.0)]
        pts = [Vector((x, y, z)) for (y, z) in half] + [Vector((x, -y, z)) for (y, z) in reversed(half[1:-1])]
        rings.append([bm.verts.new(p) for p in pts])
        sheer.append((x, 1.02 * b, sh))
        deckz_at.append((x, sh - 0.04))
    n = len(rings[0])
    seg_mat = {0: 2, 1: 2, 2: 2, 3: 2, 4: 4, 5: 0, 6: 0, 7: 1, 8: 5, 9: 6, 10: 3}   # by segment of the half ring
    uv = bm.loops.layers.uv.verify()
    for i, (a, b2) in enumerate(zip(rings[:-1], rings[1:])):
        for k in range(n):
            k2 = (k + 1) % n
            f = bm.faces.new((a[k], a[k2], b2[k2], b2[k]))
            seg = k if k < 11 else (n - 1 - k)                    # mirror side uses the same segment index
            f.material_index = seg_mat.get(seg, 0)
            for loop, (u, v) in zip(f.loops, ((i / 6, k / 4), (i / 6, (k + 1) / 4), ((i + 1) / 6, (k + 1) / 4), ((i + 1) / 6, k / 4))):
                loop[uv].uv = (u, v)
    t = bm.faces.new(list(reversed(rings[0])))                 # transom
    t.material_index = 0
    tip = bm.faces.new(rings[-1])
    bmesh.ops.triangulate(bm, faces=[t, tip], quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("hull")
    bm.to_mesh(me)
    bm.free()
    hull = bpy.data.objects.new("hull", me)
    bpy.context.collection.objects.link(hull)
    for m in ("HullWhite", "HullBand", "Antifouling", "DeckWood", "BootTop", "CapRail", "BulwarkIn"):
        me.materials.append(mat(m))
    for f in me.polygons:
        f.use_smooth = f.material_index in (0, 2, 4)
    parts = [hull]

    def deck_z(x):
        best = min(deckz_at, key=lambda d: abs(d[0] - x))
        return best[1]

    # rubbing strake: a square tube swept along the sheer, just below it, offset out of the hull
    for side in (-1, 1):
        sbm = bmesh.new()
        prev = None
        for (x, y, z) in sheer[1:-2]:
            c = Vector((x, side * (y + 0.035), z - 0.06))
            q = [sbm.verts.new(c + Vector((0, side * dy, dz))) for dy, dz in ((-0.04, -0.035), (0.03, -0.035), (0.03, 0.035), (-0.04, 0.035))]
            if prev:
                for k in range(4):
                    sbm.faces.new((prev[k], prev[(k + 1) % 4], q[(k + 1) % 4], q[k]))
            prev = q
        bmesh.ops.recalc_face_normals(sbm, faces=sbm.faces)
        sme = bpy.data.meshes.new("strake")
        sbm.to_mesh(sme)
        sbm.free()
        so = bpy.data.objects.new("strake", sme)
        bpy.context.collection.objects.link(so)
        sme.materials.append(mat("Strake"))
        parts.append(so)

    # the name, painted on both bows following the topsides
    for side in (-1, 1):
        sel = [s_ for s_ in sheer if 1.0 <= s_[0] <= 2.75]
        nbm = bmesh.new()
        nuv = nbm.loops.layers.uv.verify()
        cols = []
        for (x, y, z) in sel:
            yb = y * 0.995
            cols.append((nbm.verts.new((x, side * (yb + 0.012), z - 0.42)), nbm.verts.new((x, side * (yb + 0.012), z - 0.12))))
        L = len(cols) - 1
        for i in range(L):
            a, b2 = cols[i], cols[i + 1]
            f = nbm.faces.new((a[0], b2[0], b2[1], a[1]))
            # readable from outside: the starboard (-Y) side reads bow-wards, the port side stern-wards
            u0, u1 = (i / L, (i + 1) / L) if side < 0 else (1 - i / L, 1 - (i + 1) / L)
            for loop, uvv in zip(f.loops, ((u0, 0), (u1, 0), (u1, 1), (u0, 1))):
                loop[nuv].uv = uvv
        nme = bpy.data.meshes.new("name")
        nbm.to_mesh(nme)
        nbm.free()
        no = bpy.data.objects.new("name", nme)
        bpy.context.collection.objects.link(no)
        nme.materials.append(mat("TX_BoatName_0"))
        parts.append(no)

    # wheelhouse aft of midships: windows all round, a door aft, the roof with overhang, a searchlight and an aerial
    wx, dz = -1.0, deck_z(-1.0)
    parts.append(box((wx, 0, dz + 0.62), (1.45, 1.25, 1.24), "CabinWhite", bevel=0.04))
    parts.append(box((wx, 0, dz + 1.28), (1.7, 1.45, 0.08), "HullBand", bevel=0.02))
    for k, yy in enumerate((-0.38, 0.0, 0.38)):
        parts.append(box((wx + 0.728, yy, dz + 0.96), (0.02, 0.32, 0.34), "Glass"))
    for side in (-1, 1):
        for xx in (wx - 0.3, wx + 0.3):
            parts.append(box((xx, side * 0.628, dz + 0.96), (0.42, 0.02, 0.32), "Glass"))
    parts.append(box((wx - 0.728, 0.2, dz + 0.55), (0.02, 0.52, 1.0), "Strake"))
    parts.append(cyl((wx + 0.4, 0.4, dz + 1.42), 0.09, 0.2, "Metal", verts=10))
    parts.append(cyl((wx - 0.5, -0.5, dz + 1.9), 0.012, 1.2, "Metal", verts=5))
    # lifebuoy on the wheelhouse side
    bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.06, major_segments=14, minor_segments=6,
                                     location=(wx + 0.05, -0.655, dz + 0.55), rotation=(math.pi / 2, 0, 0))
    lb = bpy.context.active_object
    lb.data.materials.append(mat("Salvavidas"))
    parts.append(lb)
    # mast forward: tapered pole, crosstree, masthead lamp, two stays
    mx = 1.25
    mz = deck_z(mx)
    parts.append(cyl((mx, 0, mz + 1.7), 0.06, 3.4, "Mast", verts=8, r2=0.035))
    parts.append(box((mx, 0, mz + 2.9), (0.08, 0.9, 0.06), "Mast"))
    parts.append(cyl((mx, 0, mz + 3.45), 0.05, 0.12, "LightFront", verts=8))
    for (tx, ty, tz) in ((3.4, 0, sheer[-2][2] + 0.3), (-0.2, 0.9, deck_z(-0.2) + 0.3), (-0.2, -0.9, deck_z(-0.2) + 0.3)):
        a, b2 = Vector((mx, 0, mz + 2.85)), Vector((tx, ty, tz))
        mid, d = (a + b2) / 2, (b2 - a)
        rot = d.to_track_quat("Z", "Y").to_euler()
        parts.append(cyl(tuple(mid), 0.008, d.length, "Mast", rot=tuple(rot), verts=4))
    # tyre fenders hanging over the side
    for side in (-1, 1):
        for xx in (-2.1, -0.7, 0.6):
            y = min(sheer, key=lambda s_: abs(s_[0] - xx))[1]
            bpy.ops.mesh.primitive_torus_add(major_radius=0.2, minor_radius=0.075, major_segments=12, minor_segments=6,
                                             location=(xx, side * (y + 0.09), 0.5), rotation=(math.pi / 2, 0, 0))
            ty_ = bpy.context.active_object
            ty_.data.materials.append(mat("Rubber"))
            parts.append(ty_)
    # net drum at the stern on two cheeks, a fish box and a coil on deck
    sx_ = -2.75
    sz_ = deck_z(sx_)
    parts.append(cyl((sx_, 0, sz_ + 0.45), 0.3, 1.1, "NetGreen", rot=(math.pi / 2, 0, 0), verts=14))
    for side in (-1, 1):
        parts.append(box((sx_, side * 0.6, sz_ + 0.4), (0.5, 0.06, 0.8), "Strake"))
    parts.append(box((0.3, 0.45, deck_z(0.3) + 0.15), (0.6, 0.4, 0.3), "Crate", bevel=0.01))
    parts.append(cyl((0.4, -0.5, deck_z(0.4) + 0.06), 0.22, 0.12, "Rope", verts=12))
    ob = join(parts, "CITY_Boat_Lancha", turn=-math.pi / 2)
    preview(OUT / "CITY_Boat_Lancha_preview.png", (0, 0, 0.8), 9)
    export(ob, OUT / "CITY_Boat_Lancha.fbx")


def _frame(parts, lona):
    """The stall's tube frame and canvas: uprights, the roof sloping to the customers (front +Y), a front valance,
    a back curtain so the stall reads as one solid thing from behind."""
    for x in (-1.08, 1.08):
        parts.append(cyl((x, -0.62, 1.16), 0.022, 2.32, "Metal", verts=8))
        parts.append(cyl((x, 0.72, 1.0), 0.022, 2.0, "Metal", verts=8))
    for y, z in ((-0.62, 2.31), (0.72, 1.99)):
        parts.append(cyl((0, y, z), 0.018, 2.2, "Metal", rot=(0, math.pi / 2, 0), verts=6))
    parts.append(quad([(-1.14, -0.7, 2.33), (1.14, -0.7, 2.33), (1.14, 0.82, 1.97), (-1.14, 0.82, 1.97)], lona, uvs=((0, 0), (3, 0), (3, 1), (0, 1))))
    parts.append(quad([(-1.14, 0.82, 1.97), (1.14, 0.82, 1.97), (1.14, 0.82, 1.74), (-1.14, 0.82, 1.74)], lona, uvs=((0, 0), (3, 0), (3, 0.14), (0, 0.14))))
    for x in (-1.14, 1.14):
        parts.append(quad([(x, -0.7, 2.33), (x, 0.82, 1.97), (x, 0.82, 1.82), (x, -0.7, 2.16)], lona, uvs=((0, 1), (1.6, 1), (1.6, 0.86), (0, 0.86))))
    parts.append(quad([(-1.1, -0.64, 0.05), (1.1, -0.64, 0.05), (1.1, -0.64, 2.3), (-1.1, -0.64, 2.3)], lona, uvs=((0, 0), (3, 0), (3, 2.4), (0, 2.4))))


def _table(parts, skirt, z=0.78):
    parts.append(box((0, 0.05, z), (2.0, 0.9, 0.05), "TableWood", bevel=0.01))
    parts.append(quad([(-1.0, 0.505, z - 0.02), (1.0, 0.505, z - 0.02), (1.0, 0.505, 0.06), (-1.0, 0.505, 0.06)], skirt, uvs=((0, 1), (3, 1), (3, 0), (0, 0))))
    for x in (-0.95, 0.95):
        for y in (-0.36, 0.46):
            parts.append(cyl((x, y, z / 2), 0.018, z, "Metal", verts=6))


def _crate(parts, x, y, z, tex, tilt=0.0, w=0.56, d=0.4, h=0.2):
    """A crate of produce: the box and its top of fruit, tilted towards the customers on a stepped display."""
    parts.append(box((x, y, z + h / 2), (w, d, h), "Crate", bevel=0.008, rot=(tilt, 0, 0)))
    c, s_ = math.cos(tilt), math.sin(tilt)
    hz = h / 2 + 0.004
    def p(dx, dy):                       # the crate's top face, in the crate's own (tilted) frame
        return (x + dx, y + dy * c - hz * s_, z + h / 2 + dy * s_ + hz * c)
    parts.append(quad([p(-w / 2 + 0.03, -d / 2 + 0.03), p(w / 2 - 0.03, -d / 2 + 0.03), p(w / 2 - 0.03, d / 2 - 0.03), p(-w / 2 + 0.03, d / 2 - 0.03)], tex))


def _card(parts, x, y, z, tex, w=0.16, h=0.1, stick=True):
    # seen from the customers' side (+Y before the turn) the viewer's right is -X: wound and mapped that way
    parts.append(quad([(x + w / 2, y, z), (x - w / 2, y, z), (x - w / 2, y, z + h), (x + w / 2, y, z + h)], tex))
    if stick:
        parts.append(cyl((x, y - 0.005, z - 0.06), 0.004, 0.14, "TableWood", verts=4))


def stall_fruta():
    """Fruit and vegetables: produce in crates on a stepped display, prices on sticks, a hanging scale, the stock
    under the table."""
    reset()
    parts = []
    _frame(parts, "TX_Lona_Rojo")
    _table(parts, "TX_Lona_Rojo")
    goods = ("TX_Produce_Naranjas", "TX_Produce_Lechugas", "TX_Produce_Manzanas", "TX_Produce_Pimientos", "TX_Produce_Manzanas", "TX_Produce_Naranjas")
    for i, x in enumerate((-0.62, 0.0, 0.62)):
        _crate(parts, x, 0.24, 0.805, goods[i], tilt=-0.22)
        parts.append(box((x, -0.2, 0.86), (0.56, 0.4, 0.1), "Crate", bevel=0.006))
        _crate(parts, x, -0.2, 0.91, goods[i + 3], tilt=-0.22)
        _card(parts, x + 0.18, 0.47, 1.06, f"TX_Precio_{i}")
    parts.append(cyl((0.82, 0.55, 1.5), 0.15, 0.025, "Metal", verts=14))
    parts.append(cyl((0.82, 0.55, 1.74), 0.006, 0.48, "Metal", verts=4))
    for x, z in ((-0.55, 0.11), (0.05, 0.11), (-0.55, 0.33)):
        parts.append(box((x, -0.25, z), (0.56, 0.4, 0.22), "Crate", bevel=0.006))
    parts.append(box((0.6, -0.3, 0.2), (0.5, 0.4, 0.4), "Carton", bevel=0.01))
    ob = join(parts, "CITY_Market_Stall_Fruta", turn=math.pi)
    preview(OUT / "CITY_Market_Stall_Fruta_preview.png", (0, 0, 1.0), 5.0)
    export(ob, OUT / "CITY_Market_Stall_Fruta.fbx")


def stall_ropa():
    """Clothes: garments hanging from the front beam, folded piles on a low table, the cardboard price sign."""
    reset()
    parts = []
    _frame(parts, "TX_Lona_Azul")
    parts.append(box((0, -0.05, 0.7), (1.9, 0.75, 0.04), "TableWood", bevel=0.01))
    for x in (-0.9, 0.9):
        for y in (-0.38, 0.28):
            parts.append(cyl((x, y, 0.35), 0.018, 0.7, "Metal", verts=6))
    cols = ("Ropa_A", "Ropa_B", "Ropa_C", "Ropa_D", "Ropa_B", "Ropa_A")
    for i, x in enumerate((-0.6, 0.0, 0.6)):
        for j, y in enumerate((-0.2, 0.12)):
            n = 3 + (i + j) % 3
            for k in range(n):
                parts.append(box((x + 0.01 * ((k % 2) * 2 - 1), y, 0.75 + k * 0.055), (0.42, 0.3, 0.05), cols[(i * 2 + j + k) % 6], bevel=0.01))
    parts.append(cyl((0, 0.8, 1.86), 0.012, 2.1, "Metal", rot=(0, math.pi / 2, 0), verts=6))
    for k, x in enumerate((-0.85, -0.55, -0.25, 0.05, 0.35, 0.65, 0.9)):
        cell = k % 4
        u0, v0 = (cell % 2) * 0.5, (cell // 2) * 0.5
        a = (k - 3) * 0.06
        dx, dy = math.cos(a) * 0.24, math.sin(a) * 0.24
        parts.append(quad([(x - dx, 0.8 - dy, 1.12), (x + dx, 0.8 + dy, 1.12), (x + dx, 0.8 + dy, 1.84), (x - dx, 0.8 - dy, 1.84)], "TX_Ropa",
                          uvs=((u0, v0), (u0 + 0.5, v0), (u0 + 0.5, v0 + 0.5), (u0, v0 + 0.5))))
        parts.append(cyl((x, 0.8, 1.86), 0.003, 0.05, "Metal", verts=4))
    _card(parts, 0.0, 0.345, 0.73, "TX_Cartel_Ropa", w=0.5, h=0.3, stick=False)
    ob = join(parts, "CITY_Market_Stall_Ropa", turn=math.pi)
    preview(OUT / "CITY_Market_Stall_Ropa_preview.png", (0, 0, 1.0), 5.0)
    export(ob, OUT / "CITY_Market_Stall_Ropa.fbx")


def stall_quesos():
    """Products of the valleys: cheeses, sobaos and quesadas in their boxes, honey and orujo, a chalkboard."""
    reset()
    parts = []
    _frame(parts, "TX_Lona_Verde")
    _table(parts, "TX_Lona_Verde")
    for i, (x, y) in enumerate(((-0.75, 0.2), (-0.45, 0.25), (-0.6, -0.12), (-0.3, -0.05))):
        r = 0.13 if i % 2 == 0 else 0.1
        parts.append(cyl((x, y, 0.805 + 0.05), r, 0.1, "Queso", verts=16))
    parts.append(cyl((-0.6, -0.12, 0.96), 0.12, 0.09, "Queso", verts=16))
    for k in range(3):
        for j in range(3 - k):
            x = 0.0 + (j - (2 - k) / 2) * 0.2
            parts.append(box((x, 0.18, 0.84 + k * 0.065), (0.19, 0.13, 0.06), "Carton", bevel=0.004))
            yf = 0.18 + 0.065 + 0.002
            parts.append(quad([(x + 0.09, yf, 0.84 + k * 0.065 - 0.028), (x - 0.09, yf, 0.84 + k * 0.065 - 0.028),
                               (x - 0.09, yf, 0.84 + k * 0.065 + 0.028), (x + 0.09, yf, 0.84 + k * 0.065 + 0.028)], "TX_Sobaos"))
    for j in range(5):
        for k in range(2):
            parts.append(cyl((0.45 + j * 0.1, 0.25 - k * 0.12, 0.865), 0.042, 0.12, "Miel", verts=10))
            parts.append(cyl((0.45 + j * 0.1, 0.25 - k * 0.12, 0.935), 0.044, 0.02, "TapaMiel", verts=10))
    for j in range(3):
        parts.append(cyl((0.55 + j * 0.12, -0.2, 0.95), 0.035, 0.28, "Botella", verts=10))
        parts.append(cyl((0.55 + j * 0.12, -0.2, 1.11), 0.012, 0.06, "Corcho", verts=6))
    # the chalkboard on its easel beside the stall
    lean = 0.18                                   # the board leans back on its easel
    parts.append(box((1.05, 0.95, 0.46), (0.52, 0.03, 0.84), "TableWood", rot=(lean, 0, 0)))
    def on_board(lx, lz, ly=0.018):
        return (1.05 + lx, 0.95 + ly * math.cos(lean) - lz * math.sin(lean), 0.46 + ly * math.sin(lean) + lz * math.cos(lean))
    parts.append(quad([on_board(0.24, -0.38), on_board(-0.24, -0.38), on_board(-0.24, 0.38), on_board(0.24, 0.38)], "TX_Cartel_Quesos"))
    ob = join(parts, "CITY_Market_Stall_Quesos", turn=math.pi)
    preview(OUT / "CITY_Market_Stall_Quesos_preview.png", (0, 0, 1.0), 5.0)
    export(ob, OUT / "CITY_Market_Stall_Quesos.fbx")


def terrace():
    """A bar terrace set as one piece: aluminium table, four white plastic chairs, the parasol pole through the
    table's own hole (designed, not colliding). Footprint 2.2 x 2.2 m."""
    reset()
    parts = [cyl((0, 0, 0.72), 0.4, 0.03, "Alu", verts=20), cyl((0, 0, 0.36), 0.03, 0.72, "Alu", verts=8), cyl((0, 0, 0.02), 0.25, 0.04, "Alu", verts=16)]
    for k in range(4):
        a = k * math.pi / 2
        cx, cy = math.cos(a) * 0.72, math.sin(a) * 0.72
        rot = (0, 0, a + math.pi / 2)
        parts.append(box((cx, cy, 0.44), (0.42, 0.42, 0.04), "PlasticWhite", bevel=0.015, rot=rot))
        back = (math.cos(a) * 0.92, math.sin(a) * 0.92, 0.66)
        parts.append(box(back, (0.42, 0.04, 0.42), "PlasticWhite", bevel=0.015, rot=(0, 0, a + math.pi / 2)))
        for lx in (-0.17, 0.17):
            for ly in (-0.17, 0.17):
                px = cx + lx * math.cos(a + math.pi / 2) - ly * math.sin(a + math.pi / 2)
                py = cy + lx * math.sin(a + math.pi / 2) + ly * math.cos(a + math.pi / 2)
                parts.append(cyl((px, py, 0.21), 0.018, 0.42, "PlasticWhite", verts=6))
    parts.append(cyl((0, 0, 1.25), 0.02, 2.5, "Alu", verts=8))
    parts.append(cyl((0, 0, 2.25), 1.1, 0.45, "ParasolCanvas", verts=8, r2=0.05))
    ob = join(parts, "CITY_Terrace_Set")
    preview(OUT / "CITY_Terrace_Set_preview.png", (0, 0, 0.9), 5.0)
    export(ob, OUT / "CITY_Terrace_Set.fbx")


def small_icons():
    reset()
    b = [cyl((0, 0, 0.3), 0.15, 0.55, "Butane", verts=16), cyl((0, 0, 0.62), 0.07, 0.1, "Metal", verts=10), cyl((0, 0, 0.03), 0.16, 0.06, "Butane", verts=16)]
    ob = join(b, "CITY_Butane")
    export(ob, OUT / "CITY_Butane.fbx")
    reset()
    m = [box((0, 0, 0.55), (0.42, 0.34, 0.6), "Correos", bevel=0.05), cyl((0, 0, 0.88), 0.21, 0.34, "Correos", rot=(math.pi / 2, 0, 0), verts=16),
         box((0, 0.172, 0.72), (0.26, 0.01, 0.05), "Rubber"), box((0, 0.172, 0.52), (0.2, 0.01, 0.1), "CorreosBlue"), cyl((0, 0, 0.12), 0.06, 0.24, "Correos", verts=8)]
    ob = join(m, "CITY_Buzon_Correos", turn=math.pi)
    export(ob, OUT / "CITY_Buzon_Correos.fbx")
    reset()
    g = [box((0, 0, 0.25), (0.34, 0.3, 0.5), "Gumball", bevel=0.03), box((0, 0, 0.72), (0.3, 0.26, 0.42), "GumGlass", bevel=0.02),
         box((0, 0, 0.96), (0.34, 0.3, 0.06), "Gumball", bevel=0.02), cyl((0, 0.16, 0.36), 0.05, 0.04, "Metal", rot=(math.pi / 2, 0, 0))]
    ob = join(g, "CITY_Gumball", turn=math.pi)
    preview(OUT / "CITY_Icons_preview.png", (0, 0, 0.5), 2.2)
    export(ob, OUT / "CITY_Gumball.fbx")


boat()
stall_fruta()
stall_ropa()
stall_quesos()
terrace()
small_icons()
print("STREET_DONE", OUT)
