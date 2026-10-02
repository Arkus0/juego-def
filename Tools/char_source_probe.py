"""Bounded real-source census; run with Blender --background --python this_file."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
VAULT = Path('C:/Juego2-Assets')
CAT = json.loads((ROOT / 'Docs/evidence/WP-PROD-ASSET-00/catalog.json').read_text())
print('CAT_KEYS', list(CAT))
entries = {x['id']: x for x in CAT['items']}
ids = ['base:regular_male_fullbody', 'base:regular_female_fullbody',
       'base:teen_male_fullbody', 'base:hair_simpleparted', 'base:hair_bob',
       'outfits:male_peasant', 'outfits:female_peasant', 'outfits:male_ranger',
       'outfits:female_ranger']
result = []
for id in ids:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    entry = entries[id]
    print('ENTRY', entry)
    path = VAULT / entry['sourcePath']
    bpy.ops.import_scene.fbx(filepath=str(path))
    objects = []
    for o in bpy.data.objects:
        row = {'name': o.name, 'type': o.type, 'scale': list(o.scale),
               'rotation': list(o.rotation_euler), 'location': list(o.location)}
        if o.type == 'MESH':
            verts = [o.matrix_world @ v.co for v in o.data.vertices]
            row.update(vertices=len(verts), faces=len(o.data.polygons),
                bounds=[[min(v[i] for v in verts) for i in range(3)],
                        [max(v[i] for v in verts) for i in range(3)]],
                materials=[m.name if m else None for m in o.data.materials],
                groups=[g.name for g in o.vertex_groups],
                modifiers=[m.type for m in o.modifiers])
        if o.type == 'ARMATURE':
            row['bones'] = [{'name': b.name, 'parent': b.parent.name if b.parent else None,
                'head': list(o.matrix_world @ b.head_local), 'tail': list(o.matrix_world @ b.tail_local)} for b in o.data.bones]
        objects.append(row)
    result.append({'id': id, 'objects': objects})
out = ROOT / 'Docs/evidence/WP-PROD-CHAR-01/source_census.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({'blender': bpy.app.version_string, 'sources': result}, indent=2))
print('CENSUS_WRITTEN', out)
