"""Bounded Chilyer reproduction + real Modular Outfits donor comparison.

Run: blender --background --python-exit-code 1 --python Tools/char_reuse_spike.py
No vendor source writes. Probe output is evidence, not a production prefab.
"""
import bpy, bmesh, json, sys, hashlib, math
from pathlib import Path
from mathutils import Vector, Matrix
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Tools/vendor/chilyer'))
from body_topo import build_bodytopo_garment
VAULT = Path('C:/Juego2-Assets')
OUT = ROOT / 'Docs/evidence/WP-PROD-CHAR-01'
ENTRIES = {x['id']: x for x in json.loads((ROOT / 'Docs/evidence/WP-PROD-ASSET-00/catalog.json').read_text())['items']}

def load(id):
    e = ENTRIES[id]
    p = VAULT / e['sourcePath']
    assert hashlib.sha256(p.read_bytes()).hexdigest() == e['sourceSha256'], id
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(p))
    bpy.context.view_layer.update()
    objects = [o for o in bpy.data.objects if o not in before]
    for o in objects:
        if o.type == 'MESH':
            mw = o.matrix_world.copy()
            o.data.transform(mw)
            o.matrix_world = Matrix.Identity(4)
    return next((o for o in objects if o.type == 'ARMATURE'), None), [o for o in objects if o.type == 'MESH']

def cull(o, predicate):
    bm=bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not predicate(f)],context='FACES')
    bm.to_mesh(o.data); bm.free(); o.data.update()

def color(o,rgba):
    m=bpy.data.materials.new(o.name+'_probe'); m.diffuse_color=(*rgba,1)
    o.data.materials.clear(); o.data.materials.append(m)
    for p in o.data.polygons: p.material_index=0

def pose(arm):
    for n,a in [('upperarm_l',-65),('upperarm_r',65)]:
        b=arm.pose.bones.get(n)
        if b: b.rotation_mode='XYZ'; b.rotation_euler[1]=math.radians(a)

def render(path):
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO'; scene.display.shading.studiolight_rotate_z=0.6
    scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='BOTH'
    scene.world=bpy.data.worlds.new('ProbeWorld')
    scene.display.shading.background_type='WORLD'; scene.world.color=(.16,.17,.19)
    scene.render.resolution_x=1600; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    data=bpy.data.cameras.new('Camera'); cam=bpy.data.objects.new('Camera',data); scene.collection.objects.link(cam)
    cam.location=(2,6,2.4); target=Vector((0,0,.95)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'; data.ortho_scale=2.6; scene.camera=cam
    scene.render.resolution_x=720;scene.render.resolution_y=900
    scene.render.filepath=str(path); bpy.ops.render.render(write_still=True)

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    reports=[]
    for i,mode in enumerate(['bad_fullbody_peasant','head_peasant','head_ranger_stripped','bodytopo']):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        before=set(bpy.data.objects)
        arm,base=load('base:regular_male_fullbody')
        body=max(base,key=lambda o:len(o.data.vertices))
        for o in base: color(o,(.64,.39,.24) if o==body else (.14,.10,.08))
        if mode=='bodytopo':
            # World-space body topology; plain long-sleeved civilian sweater.
            result=build_bodytopo_garment(body,'Crew_sweater',lambda x,y,z: .96<z<1.535 and abs(x)<.64,
                    base_color=(.06,.16,.22,1),push_distance=.015,min_island_size=35)
            report={k:v for k,v in result.items() if k!='object'}
            result2=build_bodytopo_garment(body,'Trousers',lambda x,y,z:.13<z<1.04,
                    base_color=(.07,.085,.10,1),push_distance=.018,min_island_size=35)
            report['trousers']={k:v for k,v in result2.items() if k!='object'}
            cull(body,lambda f:f.calc_center_median().z>1.52 or abs(f.calc_center_median().x)>.635 or f.calc_center_median().z<.14)
            reports.append({'probe':mode,**report})
        else:
            donor,meshes=load('outfits:male_ranger' if 'ranger' in mode else 'outfits:male_peasant')
            donor_bones={b.name:b for b in donor.data.bones}; base_bones={b.name:b for b in arm.data.bones}
            maxdelta=max(((donor.matrix_world@donor_bones[n].head_local)-(arm.matrix_world@b.head_local)).length for n,b in base_bones.items() if n in donor_bones)
            kept=[]
            for o in meshes:
                if 'ranger' in mode and any(s in o.name for s in ['Hood','Pauldron','Bracer','Belt']):
                    bpy.data.objects.remove(o,do_unlink=True); continue
                mw=o.matrix_world.copy(); o.parent=arm; o.matrix_world=mw
                for m in o.modifiers:
                    if m.type=='ARMATURE':m.object=arm
                color(o,(.11,.22,.27) if 'Body' in o.name or 'Arms' in o.name else (.07,.075,.08))
                kept.append(o.name)
            bpy.data.objects.remove(donor,do_unlink=True)
            if mode!='bad_fullbody_peasant':
                headgroups={g.index for g in body.vertex_groups if g.name in ['Head','neck_01']}
                allowed={v.index for v in body.data.vertices if max(v.groups,key=lambda g:g.weight).group in headgroups}
                cull(body,lambda f:all(v.index in allowed for v in f.verts))
            reports.append({'probe':mode,'sharedBones':len(set(base_bones)&set(donor_bones)),'maxRestHeadDeltaMeters':maxdelta,'retainedMeshes':kept})
        hairarm,hair=load('base:hair_simpleparted')
        for o in hair:
            o.data.transform(Matrix.Rotation(math.pi,4,'Z'))
            g=o.vertex_groups.new(name='Head');g.add(list(range(len(o.data.vertices))),1,'REPLACE')
            mod=o.modifiers.new('Armature','ARMATURE');mod.object=arm
            o.parent=arm; o.matrix_world=Matrix.Identity(4);color(o,(.075,.045,.022))
        render(OUT/('reuse_'+mode+'.png'))
    (OUT/'reuse_spike.json').write_text(json.dumps({'blender':bpy.app.version_string,'probes':reports},indent=2))
    print('REUSE_SPIKE_COMPLETE')

if __name__=='__main__':main()
