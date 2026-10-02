"""Trees and bushes for the town in the Dreamcast+ manner: a modelled trunk and branches, the foliage as clumps of
painted leaf cards whose normals point out of the crown (the era's trick: the cards light like a volume).

Run:  blender -b -P build_nature.py -- <out_dir>
Materials are named after the textures (TX_*), Unity's CityPropsLibrary maps them to DC Plus materials.
"""

import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

OUT = Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else Path.cwd()
OUT.mkdir(parents=True, exist_ok=True)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, color=(0.5, 0.5, 0.5, 1)):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = color
    return m


def tube(bm, p0, p1, r0, r1, sides=7):
    """A tapered tube between two points (trunk or branch), UVs wrapped round it."""
    d = (p1 - p0)
    L = d.length
    z = d.normalized()
    x = z.cross(Vector((0, 0, 1)) if abs(z.z) < 0.9 else Vector((1, 0, 0))).normalized()
    y = z.cross(x)
    ring0, ring1 = [], []
    for k in range(sides):
        a = 2 * math.pi * k / sides
        off = x * math.cos(a) + y * math.sin(a)
        ring0.append(bm.verts.new(p0 + off * r0))
        ring1.append(bm.verts.new(p1 + off * r1))
    uv = bm.loops.layers.uv.verify()
    for k in range(sides):
        f = bm.faces.new((ring0[k], ring0[(k + 1) % sides], ring1[(k + 1) % sides], ring1[k]))
        f.material_index = 0
        u0, u1 = k / sides, (k + 1) / sides
        for loop, (u, v) in zip(f.loops, ((u0, 0), (u1, 0), (u1, L / 2), (u0, L / 2))):
            loop[uv].uv = (u, v)
    return ring1


def cards(bm, centre, radii, n, size, rng, mat_index=1, shell=0.65):
    """Crossed leaf cards in an ellipsoid crown; returns the faces made (for the outward normals)."""
    uv = bm.loops.layers.uv.verify()
    faces = []
    for i in range(n):
        # mostly on the shell of the crown, a few inside to fill it
        u, v = rng.uniform(0, 2 * math.pi), rng.uniform(-0.85, 1.0)
        rr = rng.uniform(shell, 1.0)
        p = centre + Vector((math.cos(u) * math.sqrt(1 - v * v) * radii.x, math.sin(u) * math.sqrt(1 - v * v) * radii.y, v * radii.z)) * rr
        s = size * rng.uniform(0.8, 1.2)
        rot = Euler((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(0, math.pi))).to_matrix()
        for k in range(2):
            m = rot @ Matrix.Rotation(k * math.pi / 2, 3, "Z")
            corners = [p + m @ Vector((dx * s / 2, 0, dz * s / 2)) for dx, dz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            vs = [bm.verts.new(c) for c in corners]
            f = bm.faces.new(vs)
            f.material_index = mat_index
            for loop, (a, b) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
                loop[uv].uv = (a, b)
            faces.append(f)
    return faces


def finish(bm, name, materials, crown_centres, leaf_index=1):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    for m in materials:
        me.materials.append(m)
    # foliage normals point out of the nearest crown centre: the clump lights as a volume
    normals = []
    for loop in me.loops:
        v = me.vertices[loop.vertex_index].co
        poly = me.polygons[loop.index // 4] if False else None
        normals.append(None)
    loop_normals = []
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            if poly.material_index == leaf_index:
                c = min(crown_centres, key=lambda cc: (cc - v).length)
                loop_normals.append(((v - c).normalized() + Vector((0, 0, 0.35))).normalized())
            else:
                loop_normals.append(poly.normal.copy())
    me.normals_split_custom_set([tuple(n) for n in loop_normals])
    return ob


def preview(path, target=(0, 0, 3), dist=12):
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_WORKBENCH"
    scn.display.shading.light = "STUDIO"
    scn.display.shading.color_type = "TEXTURE"
    scn.render.resolution_x, scn.render.resolution_y = 520, 620
    scn.render.film_transparent = False
    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    t = Vector(target)
    cam.location = t + Vector((dist * 0.75, -dist * 0.66, dist * 0.18))
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    scn.camera = cam
    scn.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def textured(name, tex):
    m = mat(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    img = bpy.data.images.load(str(Path(OUT).parent / "Textures" / f"{tex}.png"), check_existing=True)
    tn = nt.nodes.new("ShaderNodeTexImage")
    tn.image = img
    nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tn.outputs["Alpha"], bsdf.inputs["Alpha"])
    return m


def export(ob, path):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                             axis_forward="-Z", axis_up="Y", object_types={"MESH"}, mesh_smooth_type="OFF", bake_space_transform=True)


def platano():
    reset()
    rng = random.Random(31)
    bm = bmesh.new()
    base, fork = Vector((0, 0, 0)), Vector((0.05, 0.02, 3.0))
    tube(bm, base, fork, 0.24, 0.17, 9)
    crowns = []
    for k in range(4):
        a = k * math.pi / 2 + rng.uniform(-0.3, 0.3)
        tip = fork + Vector((math.cos(a) * 1.8, math.sin(a) * 1.8, 2.2))
        tube(bm, fork, tip, 0.13, 0.06, 7)
        crowns.append(tip + Vector((0, 0, 0.6)))
    centre = Vector((0, 0, 5.6))
    faces = []
    for c in crowns:
        faces += cards(bm, c, Vector((1.7, 1.7, 1.3)), 16, 2.0, rng)
    faces += cards(bm, centre, Vector((2.8, 2.8, 1.8)), 22, 2.3, rng)
    ob = finish(bm, "CITY_Tree_Platano", [textured("TX_Bark_Platano", "TX_Bark_Platano"), textured("TX_Leaves_Platano", "TX_Leaves_Platano")], crowns + [centre])
    preview(OUT / "CITY_Tree_Platano_preview.png", (0, 0, 3.6), 14)
    export(ob, OUT / "CITY_Tree_Platano.fbx")


def magnolio():
    reset()
    rng = random.Random(41)
    bm = bmesh.new()
    fork = Vector((0, 0, 1.6))
    tube(bm, Vector((0, 0, 0)), fork, 0.2, 0.15, 8)
    crowns = [Vector((0, 0, 3.4))]
    for k in range(3):
        a = k * 2.1
        tip = fork + Vector((math.cos(a) * 1.1, math.sin(a) * 1.1, 1.6))
        tube(bm, fork, tip, 0.1, 0.05, 6)
        crowns.append(tip)
    for c in crowns:
        cards(bm, c, Vector((1.6, 1.6, 1.5)), 18, 1.7, rng, shell=0.5)
    ob = finish(bm, "CITY_Tree_Magnolio", [textured("TX_Bark_Oscura", "TX_Bark_Oscura"), textured("TX_Leaves_Magnolio", "TX_Leaves_Magnolio")], crowns)
    preview(OUT / "CITY_Tree_Magnolio_preview.png", (0, 0, 2.6), 10)
    export(ob, OUT / "CITY_Tree_Magnolio.fbx")


def manzano():
    """An old apple tree of a huerta: short leaning trunk, low wide crown on four spreading limbs."""
    reset()
    rng = random.Random(71)
    bm = bmesh.new()
    fork = Vector((0.25, 0.1, 1.3))
    tube(bm, Vector((0, 0, 0)), fork, 0.19, 0.15, 8)
    crowns = []
    for k in range(4):
        a = k * math.pi / 2 + rng.uniform(-0.4, 0.4)
        tip = fork + Vector((math.cos(a) * 1.5, math.sin(a) * 1.5, rng.uniform(0.9, 1.4)))
        tube(bm, fork, tip, 0.1, 0.05, 6)
        crowns.append(tip + Vector((0, 0, 0.3)))
    centre = Vector((0.25, 0.1, 2.9))
    for c in crowns:
        cards(bm, c, Vector((1.3, 1.3, 0.9)), 12, 1.5, rng, shell=0.5)
    cards(bm, centre, Vector((2.0, 2.0, 1.0)), 14, 1.7, rng, shell=0.4)
    ob = finish(bm, "CITY_Tree_Manzano", [textured("TX_Bark_Oscura", "TX_Bark_Oscura"), textured("TX_Leaves_Manzano", "TX_Leaves_Manzano")], crowns + [centre])
    preview(OUT / "CITY_Tree_Manzano_preview.png", (0, 0, 2.0), 9)
    export(ob, OUT / "CITY_Tree_Manzano.fbx")


def palmera():
    reset()
    rng = random.Random(51)
    bm = bmesh.new()
    pts = [Vector((0, 0, 0)), Vector((0.15, 0, 2.5)), Vector((0.4, 0.05, 5.0)), Vector((0.55, 0.1, 7.2))]
    for a, b in zip(pts[:-1], pts[1:]):
        tube(bm, a, b, 0.32 if a.z < 0.1 else 0.26, 0.26, 9)
    top = pts[-1]
    uv = bm.loops.layers.uv.verify()
    for k in range(22):
        a = k * 2 * math.pi / 22 * 2.618 % (2 * math.pi)            # golden-angle spread
        elev = math.radians(rng.uniform(-55, 45))                      # young fronds up, old ones hanging
        out = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-out.y, out.x, 0))
        L, w = rng.uniform(2.6, 3.4), rng.uniform(0.38, 0.5)
        rows = []
        for t in (0.0, 0.34, 0.68, 1.0):
            # the rib arches out and down: elevation at the root, gravity pulling the tip
            ang = elev - t * t * math.radians(rng.uniform(55, 75))
            rows.append(top + out * (L * t * math.cos(ang * 0.6)) + Vector((0, 0, L * t * math.sin(ang) * 0.8)))
        vs = [(bm.verts.new(q - side * w * (1 - 0.5 * i / 3)), bm.verts.new(q + side * w * (1 - 0.5 * i / 3))) for i, q in enumerate(rows)]
        for i in range(3):
            f = bm.faces.new((vs[i][0], vs[i][1], vs[i + 1][1], vs[i + 1][0]))
            f.material_index = 1
            for loop, (u, v) in zip(f.loops, ((0, i / 3), (1, i / 3), (1, (i + 1) / 3), (0, (i + 1) / 3))):
                loop[uv].uv = (u, v)
    ob = finish(bm, "CITY_Tree_Palmera", [textured("TX_Bark_Palmera", "TX_Bark_Palmera"), textured("TX_Frond_Palmera", "TX_Frond_Palmera")], [top + Vector((0, 0, -0.8))])
    preview(OUT / "CITY_Tree_Palmera_preview.png", (0.3, 0, 4.5), 14)
    export(ob, OUT / "CITY_Tree_Palmera.fbx")


def hortensia(tag, tex):
    reset()
    rng = random.Random(61 + len(tag))
    bm = bmesh.new()
    centre = Vector((0, 0, 0.45))
    cards(bm, centre, Vector((0.75, 0.75, 0.5)), 12, 0.95, rng, mat_index=0, shell=0.3)
    ob = finish(bm, f"CITY_Hortensia_{tag}", [textured(tex, tex)], [centre + Vector((0, 0, -0.2))], leaf_index=0)
    preview(OUT / f"CITY_Hortensia_{tag}_preview.png", (0, 0, 0.5), 3.2)
    export(ob, OUT / f"CITY_Hortensia_{tag}.fbx")


platano()
magnolio()
manzano()
palmera()
hortensia("Azul", "TX_Hortensia_Azul")
hortensia("Rosa", "TX_Hortensia_Rosa")
print("NATURE_DONE", OUT)
