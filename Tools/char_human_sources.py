"""Author the bounded CHAR heads through MPFB 2.0.17's public services.

Blender --background --python Tools/char_human_sources.py --
  --mpfb-source <pinned MPFB checkout> --system-assets <CC0 pack> [--only id]
MPFB remains an external authoring tool. Only CC0 mesh/texture outputs enter
the game. The existing CHAR Humanoid rig is retained by char_human.py.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix

ROOT=Path(__file__).resolve().parents[1]
PIN='afb9f530a7c2741dedb8df0ebae2e0b183caec21'

def bake_occlusion(head,path):
    """Bounded geometry AO, not painted directional light or copied artwork."""
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16
    mat=head.data.materials[0];mat.use_nodes=True;nodes=mat.node_tree.nodes
    output=nodes.get('Material Output');bsdf=nodes.get('Principled BSDF')
    ao=nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.055
    emission=nodes.new('ShaderNodeEmission');mat.node_tree.links.new(ao.outputs['Color'],emission.inputs['Color'])
    mat.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    image=bpy.data.images.new('HeadGeometryAO',1024,1024,alpha=False);image.colorspace_settings.name='Non-Color'
    image.generated_color=(1,1,1,1)
    target=nodes.new('ShaderNodeTexImage');target.image=image;nodes.active=target
    bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
    bpy.ops.object.bake(type='EMIT',margin=8,use_clear=False)
    path.parent.mkdir(parents=True,exist_ok=True);image.filepath_raw=str(path);image.file_format='PNG';image.save()
    mat.node_tree.links.new(bsdf.outputs[0],output.inputs['Surface'])
    for node in (ao,emission,target):nodes.remove(node)
    bpy.data.images.remove(image)
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mpfb-source',required=True);parser.add_argument('--system-assets',required=True)
    parser.add_argument('--only');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    mpfb_root=Path(args.mpfb_source).resolve();assets=Path(args.system_assets).resolve()
    import subprocess
    actual=subprocess.check_output(['git','-C',str(mpfb_root),'rev-parse','HEAD'],text=True).strip()
    if actual!=PIN:raise ValueError('MPFB authoring version changed')
    sys.path.insert(0,str(mpfb_root/'src'))
    import mpfb,addon_utils
    # Isolated batch authoring profile; no persistent user preference changes.
    bpy.utils.extension_path_user=lambda package: str(mpfb_root.parent/'MPFB_CHAR_User')
    addon_utils.enable('mpfb',default_set=True,persistent=False)
    from mpfb.services.humanservice import HumanService
    from mpfb.services.targetservice import TargetService
    forms=json.loads((ROOT/'Docs/asset_catalog/char_naturalism_forms.json').read_text())['heads']
    data=json.loads((ROOT/'Docs/asset_catalog/char_recipes.json').read_text())
    profiles={p['id']:p for p in json.loads((ROOT/'Docs/asset_catalog/char_body_profiles.json').read_text())['profiles']}
    out=ROOT/'Art/Characters/HumanHeads';out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for recipe in data['recipes']:
        if args.only and recipe['id']!=args.only:continue
        # Keep MPFB registered while clearing only the authoring objects.
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        rid=recipe['id'];form=forms[recipe['headForm']];profile=profiles[recipe['profile']]
        sex=form['sex'];macro=TargetService.get_default_macro_info_dict()
        macro['gender']=1.0 if sex=='male' else 0.0
        age=profile.get('age','adult')
        macro['age']=.83 if age=='older' or recipe.get('face')=='older' else .60 if recipe.get('face')=='mature' else .42
        macro['race']={'caucasian':1.0,'african':0.0,'asian':0.0}
        macro['weight']=.6 if 'stocky' in recipe['profile'] or 'heavy' in recipe['profile'] else .48
        body=HumanService.create_human(macro_detail_dict=macro)
        target_root=mpfb_root/'src/mpfb/data/targets'
        targets={}
        def target(path,weight):
            if abs(weight)<.015:return
            source=target_root/(path+'.target.gz')
            if not source.exists():raise ValueError('Missing admitted anatomical target '+path)
            TargetService.load_target(body,str(source),weight=weight)
            targets[path]=round(weight,4)
        # Moderate human morphological differences; the previous Quaternius
        # facial warp is not applied to these meshes.
        target('head/head-scale-horiz-'+('incr' if profile.get('faceWidth',1)>1 else 'decr'),abs(profile.get('faceWidth',1)-1)*2)
        target('chin/chin-width-'+('incr' if profile['jaw']>1 else 'decr'),abs(profile['jaw']-1)*2.5)
        target('chin/chin-prominent-'+('incr' if profile.get('chin',0)>0 else 'decr'),abs(profile.get('chin',0))*.3)
        target('nose/nose-volume-'+('incr' if profile['nose']>1 else 'decr'),abs(profile['nose']-1)*2)
        target('nose/nose-scale-horiz-'+('incr' if profile.get('noseWidth',1)>1 else 'decr'),abs(profile.get('noseWidth',1)-1)*2)
        target('mouth/mouth-scale-horiz-'+('incr' if profile.get('mouthWidth',1)>1 else 'decr'),abs(profile.get('mouthWidth',1)-1)*2)
        for side in ('l','r'):
            target('cheek/'+side+'-cheek-volume-'+('incr' if profile['cheeks']>1 else 'decr'),abs(profile['cheeks']-1)*2.4)
            target('eyes/'+side+'-eye-trans-'+('out' if profile.get('eyeSpacing',1)>1 else 'in'),abs(profile.get('eyeSpacing',1)-1)*1.6)
        if rid in ('dock-worker','mechanic','bruiser'):target('head/head-square',.18)
        elif rid in ('market-worker','shopkeeper','local-fan'):target('head/head-round',.17)
        elif rid in ('office-worker','older-resident','eccentric'):target('head/head-oval',.20)
        if profile.get('bridge',0)>0:target('nose/nose-hump-incr',.16)
        elif rid in ('older-resident','eccentric'):target('nose/nose-curve-convex',.18)
        expression=form['expression'];smile=expression['smile']
        target('mouth/mouth-angles-'+('up' if smile>=0 else 'down'),abs(smile)*.90)
        if expression['mood']=='grumpy':
            for side in ('left','right'):target('expression/units/caucasian/eyebrows-'+side+'-down',.24)
        elif expression['mood'] in ('happy','welcoming'):
            target('expression/units/caucasian/mouth-upward-retraction',.26 if expression['mood']=='happy' else .14)
        # Resting lids cover a little of the iris. The same admitted units
        # supply real closure deltas for blinking; no additional face bones.
        blink_keys={};blink_sources=[]
        for side,label in [('left','BlinkLeftDelta'),('right','BlinkRightDelta')]:
            path=target_root/('expression/units/caucasian/eye-'+side+'-closure.target.gz')
            resting=.10 if expression['mood']=='grumpy' else .07
            blink_keys[label]=TargetService.load_target(body,str(path),weight=resting,name='CHAR_'+label)
            targets['expression/units/caucasian/eye-'+side+'-closure']=resting
            blink_sources.append({'path':path.relative_to(mpfb_root).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        # Core assets have CC0 headers and fit through MPFB's own barycentric
        # correspondence. No third-party likeness or photograph is adopted.
        parts=[];source_files=[]
        def part(kind,folder,name,semantic):
            path=assets/folder/name/(name+'.mhclo')
            obj=HumanService.add_mhclo_asset(str(path),body,asset_type=kind,subdiv_levels=0,
                set_up_rigging=False,import_subrig=False,import_weights=False)
            obj.name=semantic;parts.append(obj)
            source_files.extend(p for p in path.parent.iterdir() if p.is_file() and p.suffix in ('.obj','.mhclo','.mhmat','.png'))
            return obj
        eyes=part('Eyes','eyes','high-poly','HumanEyes')
        part('Eyebrows','eyebrows','eyebrow002' if sex=='female' else 'eyebrow001','HumanBrows')
        styles={'crop':'short04','receding':'short04','sidepart':'short01','low_bun':'ponytail01',
            'pony':'ponytail01','ponytail':'ponytail01','bob':'bob01','wavy_bob':'bob01','short_waves':'short03'}
        hairstyle=styles[recipe['hairStyle']]
        part('Hair','hair',hairstyle,'HumanHair')
        deps=bpy.context.evaluated_depsgraph_get()
        # Bake the authored macro and anatomical targets plus the body-only
        # helper mask. All helper, proxy and joint geometry is excluded.
        baked=[]
        for obj in [body]+parts:
            evaluated=obj.evaluated_get(deps)
            mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
            old_name=obj.name
            new=bpy.data.objects.new('HumanHead' if obj==body else old_name,mesh)
            bpy.context.scene.collection.objects.link(new)
            mesh.transform(obj.matrix_world)
            if obj==body:
                # Preserve deltas as mesh attributes through the head/neck
                # crop. Blender's point-vector attributes interpolate at cuts.
                for label,key in blink_keys.items():
                    saved=key.value;key.value=1.0;bpy.context.view_layer.update();deps.update()
                    closed=bpy.data.meshes.new_from_object(obj.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
                    if len(closed.vertices)!=len(mesh.vertices):raise ValueError('Blink changes head topology')
                    attr=mesh.attributes.new(label,'FLOAT_VECTOR','POINT')
                    for vertex in mesh.vertices:
                        attr.data[vertex.index].vector=(obj.matrix_world@closed.vertices[vertex.index].co)-vertex.co
                    bpy.data.meshes.remove(closed);key.value=saved;bpy.context.view_layer.update();deps.update()
            baked.append(new)
        crown=max(v.co.z for v in baked[0].data.vertices)
        eye_z=sum(v.co.z for v in baked[1].data.vertices)/len(baked[1].data.vertices)
        # Crop below the throat, not through the chin. The bridge blends this
        # short neck into the retained source body's compatible neck skin.
        bm=bmesh.new();bm.from_mesh(baked[0].data)
        cut=crown-2*(crown-eye_z)-.080
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,
            plane_co=(0,0,cut),plane_no=(0,0,1),clear_inner=True)
        bm.to_mesh(baked[0].data);bm.free()
        for obj in [body]+parts:bpy.data.objects.remove(obj,do_unlink=True)
        for obj in baked:
            obj.name=obj.name.split('.')[0]
            if obj.name=='HumanBrows':
                center=sum(v.co.z for v in obj.data.vertices)/len(obj.data.vertices)
                for vertex in obj.data.vertices:vertex.co.z=center+(vertex.co.z-center)*(.70 if sex=='female' else .85)
            obj.vertex_groups.clear()
            obj.data.transform(Matrix.Rotation(math.pi,4,'Z'))
            for label in blink_keys:
                if label in obj.data.attributes:
                    rotation=Matrix.Rotation(math.pi,3,'Z')
                    for value in obj.data.attributes[label].data:value.vector=rotation@value.vector
            semantic={'HumanHead':'human_skin','HumanEyes':'human_eye','HumanBrows':'human_brow',
                'HumanLashes':'human_lash','HumanHair':'human_hair'}[obj.name]
            obj.data.materials.clear();mat=bpy.data.materials.new(semantic);obj.data.materials.append(mat)
            for poly in obj.data.polygons:poly.use_smooth=True;poly.material_index=0
        # Fit a visible forehead and both eyes. The stock bob's long central
        # fringe obscures an eye; it is swept up while the side/back locks keep
        # their length and source strand UVs. Older residents get a short cut.
        hair=next(o for o in baked if o.name=='HumanHair')
        head=next(o for o in baked if o.name=='HumanHead')
        forehead_y=max(v.co.y for v in head.data.vertices if eye_z+.025<v.co.z<eye_z+.070)
        for vertex in hair.data.vertices:
            p=vertex.co
            frontal=max(0,min(1,(p.y-(forehead_y-.045))/.025))
            central=max(0,min(1,(.090-abs(p.x))/.022))
            gate=frontal*central
            floor=eye_z+.032+.016*math.exp(-(p.x/.050)**2)
            if p.z<floor:p.z+=(floor-p.z)*gate
            if recipe['hairStyle']=='short_waves' and p.z<eye_z-.040:
                p.z=eye_z-.040+(p.z-(eye_z-.040))*.40
            if recipe['hairStyle']=='wavy_bob':
                p.x+=.0015*math.sin((p.z-eye_z)*105)*max(0,min(1,(crown-p.z)/.12))
        if recipe['hairStyle']=='low_bun':
            # Compress the lower rear ponytail into a small gathered knot.
            tail=[v for v in hair.data.vertices if v.co.z<eye_z+.015 and v.co.y<-.030]
            if tail:
                lo=min(v.co.z for v in tail);hi=eye_z+.015
                for vertex in tail:
                    t=(hi-vertex.co.z)/max(hi-lo,1e-5)
                    vertex.co.z=hi-.038*math.sin(t*math.pi*.72)
                    vertex.co.y=-.075-.035*math.sin(t*math.pi)
                    vertex.co.x*=.75
        hair.data.update()
        ao_path=out/'occlusion'/(rid+'.png');occlusion=bake_occlusion(head,ao_path)
        skin_age='old' if macro['age']>.75 else 'middleage' if macro['age']>.55 else 'young'
        skin_name=skin_age+'_caucasian_'+sex
        skin_mat=assets/'skins'/skin_name/(skin_name+'.mhmat')
        source_files.extend(p for p in skin_mat.parent.iterdir() if p.is_file() and p.suffix in ('.png','.mhmat'))
        master=out/(rid+'.blend')
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True,check_existing=False)
        row={'id':rid,'sex':sex,'skin':skin_name,'hair':hairstyle,'hairStyle':recipe['hairStyle'],
            'occlusion':occlusion,'blinkSources':blink_sources,'crown':crown,'eyeHeight':eye_z,'cut':cut,
            'targets':targets,'path':master.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(master.read_bytes()).hexdigest(),
            'meshes':[{'name':o.name,'vertices':len(o.data.vertices),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)} for o in baked],
            'sourceFiles':[{'path':p.relative_to(assets).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(source_files))]}
        rows.append(row);print('HUMAN_HEAD',rid,'crown',round(crown,4),'eye',round(eye_z,4),'mesh',row['meshes'],flush=True)
    report=out/'source_manifest.json'
    if args.only and report.exists():
        prior=json.loads(report.read_text())['heads']
        rows=[x for x in prior if x['id']!=args.only]+rows
    report.write_bytes((json.dumps({'schemaVersion':1,'mpfbVersion':'2.0.17','mpfbCommit':PIN,
        'assetLicense':'CC0-1.0','systemPackSha256':'b542127a8e25547c7c29c19f2d1d2adb9a664c80396ecd694095dbc8028a0107','heads':rows},indent=2)+'\n').encode())

if __name__=='__main__':main()
