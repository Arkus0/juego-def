"""Seat an admitted anatomical head on CHAR's existing Humanoid rig.

This bridge consumes inspectable CC0 MPFB outputs, never MPFB program logic.
No bones or animation authorities are added.
"""
import hashlib,json,math
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from char_manifest import admitted_head

ROOT=Path(__file__).resolve().parents[1]

def replace_head(recipe,body,arm,metrics,bind,bind_rigid,surface_weights,neck_support):
    entry=admitted_head(recipe)
    source=ROOT/entry['path']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=entry['sha256']:
        raise ValueError('Human head identity changed '+recipe['id'])
    # Join beneath the shirt opening. Keeping the old throat above a flat
    # shoulder cut left visible skin shards around several new necklines.
    crown=metrics['crown'];hh=metrics['headHeight'];join=crown-hh-.060
    old_skull=[v.co for v in body.data.vertices if v.co.z>crown-.090 and abs(v.co.x)<.22]
    old_width=max(abs(v.x) for v in old_skull)
    old_y=(min(v.y for v in old_skull)+max(v.y for v in old_skull))/2
    old_depth=(max(v.y for v in old_skull)-min(v.y for v in old_skull))/2
    source_hh=2*(entry['crown']-entry['eyeHeight']);scale=hh/source_hh
    # The old skin remains available for the anatomical neck boundary and
    # compatible weights. Hands and exposed legs are retained.
    body.data.calc_loop_triangles()
    triangles=[tuple(t.vertices) for t in body.data.loop_triangles]
    tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],triangles,all_triangles=True)
    ring=[v.co for v in body.data.vertices if abs(v.co.z-join)<.018 and abs(v.co.x)<.11]
    neck_y=(min(v.y for v in ring)+max(v.y for v in ring))/2 if ring else -.018
    with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
        loaded.objects=list(available.objects)
    parts=[o for o in loaded.objects if o and o.type=='MESH']
    for obj in parts:bpy.context.scene.collection.objects.link(obj)
    head=next(o for o in parts if o.name.startswith('HumanHead'))
    # Source heads face +Y, as do the retained body and clothing.
    headring=[v.co for v in head.data.vertices if abs(v.co.z-(entry['crown']-source_hh-.028/scale))<.02]
    source_y=(min(v.y for v in headring)+max(v.y for v in headring))/2 if headring else .01
    shift_y=neck_y-source_y*scale
    for obj in parts:
        for v in obj.data.vertices:
            v.co=Vector((v.co.x*scale,v.co.y*scale+shift_y,(v.co.z-entry['crown'])*scale+crown))
        obj.data.update()
    # The admitted head includes the beginning of the clavicles. Below the
    # jaw, continue its own measured throat section to the concealed seam;
    # this head-only bridge must not retain the source shoulder flare.
    head.data.calc_loop_triangles()
    anatomical_tree=BVHTree.FromPolygons([v.co for v in head.data.vertices],
        [tuple(t.vertices) for t in head.data.loop_triangles],all_triangles=True)
    throat_z=crown-hh-.012
    bm=bmesh.new();bm.from_mesh(head.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,
        plane_co=(0,0,join-.006),plane_no=(0,0,1),clear_inner=True)
    for vertex in bm.verts:
        if vertex.co.z<throat_z:
            direction=Vector((vertex.co.x,vertex.co.y-neck_y,0))
            if direction.length<1e-5:continue
            direction.normalize()
            section_origin=Vector((0,neck_y,throat_z))
            hit=anatomical_tree.ray_cast(section_origin+direction*.25,-direction,.50)[0]
            if hit is None:raise ValueError('No anatomical lower throat section '+recipe['id'])
            allowance=1+.06*min(1,(throat_z-vertex.co.z)/.060)
            radius=Vector((hit.x,hit.y-neck_y,0)).length*allowance
            if Vector((vertex.co.x,vertex.co.y-neck_y,0)).length>radius:
                vertex.co.x=direction.x*radius;vertex.co.y=neck_y+direction.y*radius
    bm.to_mesh(head.data);bm.free();head.data.update()
    facials=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Facial')]
    for obj in list(bpy.data.objects):
        if obj not in parts and obj.type=='MESH' and obj.name.startswith(('Eyes','Eyebrows','Brows','Hair','Scalp')):
            bpy.data.objects.remove(obj,do_unlink=True)
    for obj in parts:
        # Transfer the original throat's actual spine/clavicle/neck weights.
        # A generic Head->neck ramp lifted the low throat out of crewneck
        # shirts during Humanoid retargeting, although rest meshes fitted.
        obj.vertex_groups.clear()
        if obj==head:
            hg=obj.vertex_groups.new(name='Head')
            hg.add([v.index for v in obj.data.vertices],1,'REPLACE')
            surface_weights(neck_support,obj,[v for v in obj.data.vertices if v.co.z<crown-hh+.032])
            bind(obj,arm)
        else:bind_rigid(obj,arm,'Head')
    bm=bmesh.new();bm.from_mesh(body.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,
        plane_co=(0,0,join),plane_no=(0,0,1))
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z>join and abs(f.calc_center_median().x)<.24],context='FACES')
    bm.to_mesh(body.data);bm.free();body.data.update()
    # Each neckline keeps its authored height/opening, then follows the new
    # throat rather than the discarded Quaternius neck. This is one shared
    # fitting pass for all garment families and reuses the actual skin weights.
    head.data.calc_loop_triangles()
    necktree=BVHTree.FromPolygons([v.co for v in head.data.vertices],
        [tuple(t.vertices) for t in head.data.loop_triangles],all_triangles=True)
    for garment in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Top_','Outer_','Inner_','Collar','Waistcoat_panel_sewn','Work_vest_panel_sewn','Apron_shoulder_tie','Overall_strap','Backpack_strap'))]:
        bm=bmesh.new();bm.from_mesh(garment.data)
        edges=[e for e in bm.edges if e.is_boundary and e.calc_length()>.016
            and all(v.co.z>join+.015 and abs(v.co.x)<.16 for v in e.verts)]
        if edges:bmesh.ops.subdivide_edges(bm,edges=edges,cuts=2,use_grid_fill=False)
        bm.verts.index_update()
        high=[v for v in bm.verts if v.is_boundary and v.co.z>join+.015 and abs(v.co.x)<.16]
        neck_seam=max((v.co.z for v in high),default=join+.02)
        changed=[]
        for vertex in bm.verts:
            if not vertex.is_boundary or vertex.co.z<join+.015 or abs(vertex.co.x)>.16:continue
            d=Vector((vertex.co.x,vertex.co.y-neck_y,0))
            if d.length<1e-6:continue
            d.normalize()
            if vertex.co.z>neck_seam-.018:
                vertex.co.z=neck_seam-.005*max(0,d.y)
            hit=necktree.ray_cast(Vector((0,neck_y,vertex.co.z)),d,.25)[0]
            if hit is None:continue
            margin=(.022 if garment.name.startswith('Waistcoat_panel_sewn') else
                .041 if garment.name.startswith('Work_vest_panel_sewn') else
                .018 if garment.name.startswith('Outer_') else
                .020 if garment.name.startswith(('Apron_shoulder_tie','Overall_strap','Backpack_strap')) else .009)
            vertex.co=hit+d*margin
            changed.append(vertex.index)
        bm.to_mesh(garment.data);bm.free();garment.data.update()
        surface_weights(head,garment,[garment.data.vertices[i] for i in changed])
    # A continuous sewn facing bridges the anatomical throat to the original
    # shirt. Sparse shoulder triangles cannot define a smooth crewneck alone.
    # Measure every ring against both skin and cloth; no skin compression is
    # used to disguise an ill-fitting visible collar.
    shirt=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Top_','Inner_'))]
    rim_points=[v.co.z for o in shirt for v in o.data.vertices
        if abs(v.co.x)<.14 and join+.015<v.co.z<crown-hh+.080]
    if rim_points:
        rim=max(rim_points)
        # Remove the concealed clavicle section before measuring the facing.
        # Measuring it first generated a white shoulder-shaped collar skirt.
        bm=bmesh.new();bm.from_mesh(head.data)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,
            plane_co=(0,0,rim-.020),plane_no=(0,0,1),clear_inner=True)
        bm.to_mesh(head.data);bm.free();head.data.update()
        head.data.calc_loop_triangles()
        necktree=BVHTree.FromPolygons([v.co for v in head.data.vertices],
            [tuple(t.vertices) for t in head.data.loop_triangles],all_triangles=True)
        support=next((o for o in shirt if o.name.startswith('Inner_')),shirt[0])
        support.data.calc_loop_triangles()
        shirttree=BVHTree.FromPolygons([v.co for v in support.data.vertices],
            [tuple(t.vertices) for t in support.data.loop_triangles],all_triangles=True)
        vertices=[];faces=[];segments=64;rows=5
        for row in range(rows):
            t=row/(rows-1)
            for i in range(segments+1):
                a=i/segments*2*math.pi;d=Vector((math.sin(a),math.cos(a),0))
                z=rim-.035+(t*.044)-.005*max(0,math.cos(a))*t
                origin=Vector((0,neck_y,z))
                # Cast inward from outside: a mildly stooped neck can put
                # the old centre outside the new cross-section. At the low
                # hidden edge, the retained body supplies the throat below
                # the anatomical head's crop.
                section_origin=Vector((0,neck_y,max(z,rim-.018)))
                skinhit=necktree.ray_cast(section_origin+d*.25,-d,.50)[0]
                clothhit=shirttree.ray_cast(origin+d*.25,-d,.50)[0]
                if skinhit is None:
                    # This row can be beneath both deliberately cropped skin
                    # meshes. The nearest throat rim supplies its section;
                    # the facing still retains the shirt's authored height.
                    skinhit=necktree.find_nearest(section_origin+d*.065)[0]
                if skinhit is None:raise ValueError('No anatomical throat for sewn collar '+recipe['id'])
                radius=Vector((skinhit.x,skinhit.y-neck_y,0)).length+.005
                # Shoulder/arm surfaces are not a collar cross-section.
                # Limit the bridge to a small sewing allowance at the throat.
                if clothhit is not None:radius=max(radius,min((clothhit-origin).length+.003,radius+.014*(1-t)+.004))
                vertices.append(tuple(origin+d*radius))
        for row in range(rows-1):
            for i in range(segments):
                k=row*(segments+1)+i;faces.append((k,k+1,k+segments+2,k+segments+1))
        mesh=bpy.data.meshes.new('Sewn_neck_facing');mesh.from_pydata(vertices,[],faces);mesh.update()
        facing=bpy.data.objects.new('Top_neck_facing',mesh);bpy.context.scene.collection.objects.link(facing)
        mesh.materials.append(support.data.materials[0])
        for polygon in mesh.polygons:polygon.use_smooth=True
        surface_weights(head,facing);bind(facing,arm)
        # The old upright tube climbed into the jaw. A shirt has a small
        # turned collar lying on its own facing, below the exposed throat.
        collars=[o for o in bpy.data.objects if o.type=='MESH' and o.name=='Collar']
        if collars:
            collar_mat=collars[0].data.materials[0]
            for o in collars:bpy.data.objects.remove(o,do_unlink=True)
            for sign in (-1,1):
                flap_vertices=[];flap_faces=[];cols=6;flap_rows=4
                for row in range(flap_rows):
                    v=row/(flap_rows-1)
                    for column in range(cols):
                        u=column/(cols-1)
                        x=sign*(.009+u*(.063-.009))
                        z=rim+.004-u*.014-v*(.020+u*.020)
                        probe=Vector((x,.7,z));hit=shirttree.ray_cast(probe,Vector((0,-1,0)))[0]
                        neckhit=necktree.ray_cast(probe,Vector((0,-1,0)))[0]
                        y=max(hit.y if hit is not None else neck_y,neckhit.y if neckhit is not None else neck_y)
                        flap_vertices.append((x,y+.009+.003*math.sin(v*math.pi),z))
                for row in range(flap_rows-1):
                    for column in range(cols-1):
                        k=row*cols+column;flap_faces.append((k,k+1,k+cols+1,k+cols))
                flap_mesh=bpy.data.meshes.new('Turned_collar');flap_mesh.from_pydata(flap_vertices,[],flap_faces);flap_mesh.update()
                flap=bpy.data.objects.new('Collar_turnover_'+str(sign),flap_mesh);bpy.context.scene.collection.objects.link(flap)
                flap_mesh.materials.append(collar_mat)
                for polygon in flap_mesh.polygons:polygon.use_smooth=True
                surface_weights(head,flap);bind(flap,arm)
    eyes=next(o for o in parts if o.name.startswith('HumanEyes'))
    eye_z=sum(v.co.z for v in eyes.data.vertices)/len(eyes.data.vertices)
    eye_y=max(v.co.y for v in eyes.data.vertices)
    skull=[v.co for v in head.data.vertices if v.co.z>crown-.090]
    width=max(abs(v.x) for v in skull);center_y=(min(v.y for v in skull)+max(v.y for v in skull))/2
    depth=(max(v.y for v in skull)-min(v.y for v in skull))/2
    # Refit the already authored male grooming surface to the anatomical
    # head. Female recipes are explicitly forbidden from entering this path.
    if entry['sex']=='female' and facials:raise ValueError('Female facial hair rejected '+recipe['id'])
    head.data.calc_loop_triangles()
    headtree=BVHTree.FromPolygons([v.co for v in head.data.vertices],[tuple(t.vertices) for t in head.data.loop_triangles],all_triangles=True)
    for obj in facials:
        old_min=min(v.co.z for v in obj.data.vertices);old_max=max(v.co.z for v in obj.data.vertices)
        moustache='moustache' in obj.name
        sideburn='muttonchops' in obj.name
        side_x=[abs(v.co.x) for v in obj.data.vertices]
        for v in obj.data.vertices:
            if sideburn:
                t=(v.co.z-old_min)/max(old_max-old_min,1e-5)
                u=(abs(v.co.x)-min(side_x))/max(max(side_x)-min(side_x),1e-5)
                angle=math.copysign(1.14+.22*u,v.co.x)
                v.co.z=eye_z-.085+t*.092
                direction=Vector((math.sin(angle),math.cos(angle),0))
                hit=headtree.ray_cast(Vector((0,center_y,v.co.z)),direction,.25)[0]
                if hit is None:hit=headtree.find_nearest(v.co)[0]
                v.co=hit+direction*.0008
                continue
            v.co.x*=width/old_width
            if moustache:
                t=(v.co.z-old_min)/max(old_max-old_min,1e-5)
                v.co.z=crown-hh*.745+(t-.5)*hh*.025
            direction=Vector((v.co.x,v.co.y-neck_y,0))
            if direction.length<1e-5:direction=Vector((0,1,0))
            direction.normalize()
            hit=headtree.ray_cast(Vector((0,center_y,v.co.z)),direction,.25)[0]
            if hit is None:hit=headtree.find_nearest(v.co)[0]
            v.co=hit+direction*.0008
        # A small strand/cutout tile softens the previous opaque mask.
        mat=bpy.data.materials.new('human_facial');obj.data.materials.clear();obj.data.materials.append(mat)
        uv=obj.data.uv_layers.active or obj.data.uv_layers.new(name='HumanGrooming')
        xs=[v.co.x for v in obj.data.vertices];zs=[v.co.z for v in obj.data.vertices]
        for loop in obj.data.loops:
            v=obj.data.vertices[loop.vertex_index].co
            local_xs=[x for x in xs if (x<0)==(v.x<0)] if sideburn else xs
            uv.data[loop.index].uv=((v.x-min(local_xs))/max(max(local_xs)-min(local_xs),1e-5),(v.z-min(zs))/max(max(zs)-min(zs),1e-5))
        for poly in obj.data.polygons:poly.material_index=0
        obj.name='HumanGroom_'+obj.name;bind_rigid(obj,arm,'Head')
    hats=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Work_cap','Cap_','Beanie','Beret','Flatcap','Hat_'))]
    for obj in hats:
        for v in obj.data.vertices:
            v.co.x*=width/old_width
            v.co.y=(v.co.y-old_y)*depth/old_depth+center_y
    if recipe.get('headwear')=='cap':
        brim=next(o for o in hats if o.name.startswith('Cap_brim'))
        lift=max(0,eye_z+.027-min(v.co.z for v in brim.data.vertices))
        for obj in hats:
            for v in obj.data.vertices:v.co.z+=lift
    # Hair hidden by a cap is removed from the exported master, rather than
    # overlapping the hat in motion. Keep rear ponytail and sideburns.
    if recipe.get('headwear','none')!='none' and hats:
        hair=next(o for o in parts if o.name.startswith('HumanHair'))
        bottom=min(v.co.z for o in hats for v in o.data.vertices)
        bm=bmesh.new();bm.from_mesh(hair.data)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,
            plane_co=(0,0,bottom+.006),plane_no=(0,0,1))
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z>bottom+.006],context='FACES')
        bm.to_mesh(hair.data);bm.free();hair.data.update()
    # Existing glasses are fitted to the actual new ocular region.
    for obj in bpy.data.objects:
        if obj.type=='MESH' and obj.name.startswith('Glasses'):
            old_z=sum(v.co.z for v in obj.data.vertices)/len(obj.data.vertices)
            old_y=sum(v.co.y for v in obj.data.vertices)/len(obj.data.vertices)
            for v in obj.data.vertices:v.co.z+=eye_z-old_z;v.co.y+=eye_y+.007-old_y
    # Preserve the anatomical lid closures through the crop/rig bridge.
    if 'BlinkLeftDelta' in head.data.attributes:
        head.shape_key_add(name='Basis')
        for label in ('BlinkLeft','BlinkRight'):
            key=head.shape_key_add(name=label);delta=head.data.attributes[label+'Delta']
            for v in head.data.vertices:key.data[v.index].co=v.co+delta.data[v.index].vector*scale
            key.value=0
    eyes.shape_key_add(name='Basis')
    eye_centres={side:sum((v.co for v in eyes.data.vertices if (v.co.x<0)==side),Vector())/
        sum((v.co.x<0)==side for v in eyes.data.vertices) for side in (True,False)}
    from mathutils import Matrix
    for label,axis,degrees in [('GazeRight','Z',-12),('GazeLeft','Z',12),('GazeUp','X',12),('GazeDown','X',-12)]:
        key=eyes.shape_key_add(name=label);rotation=Matrix.Rotation(math.radians(degrees),3,axis)
        for v in eyes.data.vertices:
            centre=eye_centres[v.co.x<0];key.data[v.index].co=centre+rotation@(v.co-centre)
    return {'source':entry['path'],'sourceSha256':entry['sha256'],'headHeight':source_hh*scale,
        'join':join,'scale':scale,'neckShift':shift_y,'headVertices':len(head.data.vertices),
        'eyeHeight':eye_z,'rigBones':len(arm.data.bones)}
