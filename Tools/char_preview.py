"""Fast shape preview of built civilian FBX files (Blender workbench, T-pose, flat material colours).

Use it to judge garment/hair/proportion changes in seconds before running the Unity review:

  blender --background --python Tools/char_build.py -- --only waiter-veteran --output C:/Temp/char-try
  blender --background --python Tools/char_preview.py -- C:/Temp/char-try C:/Temp/preview.png waiter-veteran,fishmonger 0,90 full

Arguments after --: <fbx_dir> <out_png> <id,id,...> [view angles, default 0,45,90,180] [zoom: full|torso|head].
One PNG per angle is written next to <out_png> (<stem>_v<angle>.png). Colours are approximations; Unity materials are authoritative.
"""
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
fbx_dir, out, ids = Path(args[0]), Path(args[1]), args[2].split(',')
views = [float(v) for v in (args[3] if len(args) > 3 else '0,45,90,180').split(',')]
zoom = args[4] if len(args) > 4 else 'full'
bpy.ops.wm.read_factory_settings(use_empty=True)
roots, spacing = [], 1.15
for i, cid in enumerate(ids):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx_dir / (cid + '.fbx')))
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == 'ARMATURE')
    arm.location = Vector(((i - (len(ids) - 1) / 2) * spacing, 0, 0))
    roots.append(arm)
    for o in new:
        if o.type == 'MESH':
            for m in o.data.materials:
                bsdf = m.node_tree.nodes.get('Principled BSDF') if m and m.node_tree else None
                if bsdf:
                    m.diffuse_color = bsdf.inputs['Base Color'].default_value
bpy.context.view_layer.update()
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.color_type = 'MATERIAL'
sc.world = bpy.data.worlds.new('w')
sc.world.color = (.55, .6, .65)
n, width = len(ids), len(ids) * spacing + .4
zc, height = {'full': (.95, 2.05), 'torso': (1.25, 1.2), 'head': (1.6, .75)}[zoom]
sc.render.resolution_x = int(600 * n if zoom == 'full' else 500 * n)
sc.render.resolution_y = int(sc.render.resolution_x * height / width)
cam = bpy.data.cameras.new('c')
cam.type = 'ORTHO'
cam.ortho_scale = width
cam_obj = bpy.data.objects.new('c', cam)
sc.collection.objects.link(cam_obj)
cam_obj.location = (0, 8, zc)
cam_obj.rotation_euler = (math.pi / 2, 0, math.pi)
sc.camera = cam_obj
for angle in views:
    for arm in roots:
        arm.rotation_euler = (0, 0, math.radians(angle))
    bpy.context.view_layer.update()
    sc.render.filepath = str(out.with_name(f'{out.stem}_v{int(angle)}.png'))
    bpy.ops.render.render(write_still=True)
print('CHAR_PREVIEW_DONE', len(views))
