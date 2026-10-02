"""CHAR-01 bounded Blender assembly using Chilyer's body-topology helper.

blender --background --python-exit-code 1 --python Tools/char_build.py
Optional arguments after --: --recipes <json> --only <id> --output <folder>
The source vault is read-only. FBX output contains one rig, no animation clips.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix, Vector
from mathutils.geometry import barycentric_transform
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools'))
sys.path.insert(0,str(ROOT/'Tools/vendor/chilyer'))
from char_manifest import read_recipes, check_proportions, human_source_ids
from body_topo import build_bodytopo_garment
from char_shapes import shape_character
import char_naturalism as naturalism
import char_human

VAULT=Path('C:/Juego2-Assets')
CAT={x['id']:x for x in json.loads((ROOT/'Docs/evidence/WP-PROD-ASSET-00/catalog.json').read_text())['items']}
COMPAT=json.loads((ROOT/'Docs/asset_catalog/char_compatibility.json').read_text())
FORMS=json.loads((ROOT/'Docs/asset_catalog/char_naturalism_forms.json').read_text())

def material(name,hexcolor='FFFFFF'):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    rgb=tuple(int(hexcolor[i:i+2],16)/255 for i in (0,2,4))
    m.diffuse_color=(*rgb,1);m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*rgb,1);bsdf.inputs['Roughness'].default_value=.8
    return m

def setmat(o,m):
    o.data.materials.clear();o.data.materials.append(m)
    for p in o.data.polygons:p.material_index=0

def load(id):
    e=CAT[id];p=VAULT/e['sourcePath']
    if hashlib.sha256(p.read_bytes()).hexdigest()!=e['sourceSha256']:
        raise ValueError('Source identity changed: '+id)
    before=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(p))
    bpy.context.view_layer.update()
    objects=[o for o in bpy.data.objects if o not in before]
    for o in objects:
        if o.type=='MESH':
            o.data.transform(o.matrix_world.copy());o.matrix_world=Matrix.Identity(4)
    bpy.context.view_layer.update()
    return next((o for o in objects if o.type=='ARMATURE'),None),[o for o in objects if o.type=='MESH']

def cull(o,keep):
    bm=bmesh.new();bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not keep(f.calc_center_median())],context='FACES')
    bm.to_mesh(o.data);bm.free();o.data.update()

def bind(o,arm):
    mw=o.matrix_world.copy();o.parent=arm;o.matrix_world=mw
    mods=[m for m in o.modifiers if m.type=='ARMATURE']
    if not mods:mods=[o.modifiers.new('Armature','ARMATURE')]
    for m in mods:m.object=arm

def bind_rigid(o,arm,bone):
    o.vertex_groups.clear();g=o.vertex_groups.new(name=bone)
    g.add(list(range(len(o.data.vertices))),1,'REPLACE');bind(o,arm)

def garment(body,name,keep,push,m,planes=None):
    # Interpolate the skin's weights at real sewing planes before trimming.
    # Face-centroid culling/snap left missing shoulder triangles and stretched
    # neckline tabs, even when finite/bounds validation remained green.
    source=body
    if planes:
        source=body.copy();source.data=body.data.copy();source.name='GarmentCutSource'
        bpy.context.scene.collection.objects.link(source)
        bm=bmesh.new();bm.from_mesh(source.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
        for point,normal in planes:
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
                plane_co=point,plane_no=normal)
        bm.to_mesh(source.data);bm.free()
    r=build_bodytopo_garment(source,name,lambda x,y,z:keep(Vector((x,y,z))),
        push_distance=push,boundary_push=0 if planes else .004,smooth_passes=0 if planes else 4,solidify_thickness=.003,
        min_island_size=20)
    if source!=body:bpy.data.objects.remove(source,do_unlink=True)
    o=r['object'];setmat(o,m)
    if planes:o['sewn_cut']=True
    # The regular source encodes muscle/ridge detail. Relax the cloth surface;
    # preserving those ridges would make every garment read as painted skin.
    bm=bmesh.new();bm.from_mesh(o.data)
    smooth=[v for v in bm.verts if not planes or not v.is_boundary]
    for iteration in range(4 if planes else 7):
        bmesh.ops.smooth_vert(bm,verts=smooth,factor=.28 if planes else .45,use_axis_x=True,use_axis_y=True,use_axis_z=True)
    bm.to_mesh(o.data);bm.free();o.data.update()
    # Thin cloth is rendered double-sided in Unity. Do not bake an inner shell:
    # flattening/sizing panels can collapse it onto the outer surface (z-fighting).
    for mod in list(o.modifiers):
        if mod.type=='SOLIDIFY':o.modifiers.remove(mod)
    return o,{k:v for k,v in r.items() if k!='object'}

def top_planes(hem,neck,cuff):
    return [((0,0,hem),(0,0,1)),((0,0,neck),(0,0,1)),
            ((cuff,0,0),(1,0,0)),((-cuff,0,0),(1,0,0))]

def front(p,ratio):
    """0 at the back/sides of the neck, 1 at the throat (front is +y)."""
    return max(0.0,min(1.0,p.y/(.07*ratio)))

def trim_body(body,cuff,neck,waist,scoop=0,ratio=1,leg_hem=None):
    # Continuous throat/cuff overlap at explicit cuts. Large retained
    # clavicle triangles used to break through an open jacket's neckline.
    bm=bmesh.new();bm.from_mesh(body.data)
    for point,normal in [((0,0,1.537*ratio),(0,0,1)),((cuff-.008*ratio,0,0),(1,0,0)),((-cuff+.008*ratio,0,0),(1,0,0))]:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=point,plane_no=normal)
    if leg_hem is not None:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
            plane_co=(0,0,leg_hem*ratio),plane_no=(0,0,1))
    bm.to_mesh(body.data);bm.free()
    cull(body,lambda p:p.z>1.537*ratio or (abs(p.x)>cuff-.008*ratio and p.z>1.20*ratio)
         or (leg_hem is not None and .25*ratio<p.z<leg_hem*ratio))

def orient_outward(o):
    """Double-sided cloth is lit with its stored normal (URP Lit does not flip back faces), so a strap or bill
    whose winding faces the body renders near black in sun. Flip a whole piece when most of it faces inward/down."""
    if not o.data.polygons:return
    mw=o.matrix_world;nm=mw.to_3x3();score=0.0
    for p in o.data.polygons:
        n=(nm@p.normal);c=mw@p.center
        if abs(n.z)>.75:score+=n.z*p.area            # bills and flat tops should face up
        else:score+=n.dot(Vector((c.x,c.y+.02,0)).normalized())*p.area
    if score<0:
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
        bm.to_mesh(o.data);bm.free();o.data.update()

def tuck_neck(o,neck,ratio,band=.05,amount=.022):
    """Pull a neckline edge onto the neck: the 2-3 cm gap between cloth and skin showed as a black ring at talking distance."""
    bm=bmesh.new();bm.from_mesh(o.data)
    for v in bm.verts:
        if v.is_boundary and v.co.z>neck-band*ratio and abs(v.co.x)<.16*ratio:
            r=Vector((v.co.x,v.co.y+.017*ratio,0))
            if r.length>1e-5:
                k=max(0,r.length-amount*ratio)/r.length
                v.co.x*=k;v.co.y=(v.co.y+.017*ratio)*k-.017*ratio
    bm.to_mesh(o.data);bm.free();o.data.update()

def scoop_neck(o,neck,scoop,ratio,depth=.08):
    """Lower a flat neck cut into a garment neckline: deepest at the throat, level at the back of the neck.

    Every top used to end in a horizontal ring just under the chin, so layered shirts read as cardboard tubes."""
    if scoop<=0:return
    L=depth*ratio
    for v in o.data.vertices:
        if v.co.z>neck-L:
            t=(v.co.z-(neck-L))/L
            v.co.z-=scoop*front(v.co,ratio)*t
    o.data.update()

def tidy_boundary(o,z,inset=0.0):
    """Put a cut edge exactly on its cutting plane (face-centroid culling leaves saw teeth) and tuck it towards the axis."""
    bm=bmesh.new();bm.from_mesh(o.data)
    for v in bm.verts:
        if v.is_boundary and abs(v.co.z-z)<.03:
            v.co.z=z
            if inset:
                r=Vector((v.co.x,v.co.y,0));v.co.x-=r.x*inset;v.co.y-=r.y*inset
    bm.to_mesh(o.data);bm.free();o.data.update()

def surface_weights(source, target, vertices=None):
    """Interpolate weights on the actual supporting triangle, not four nearby
    vertices from different sides of a neck, sleeve or layered garment."""
    source.data.calc_loop_triangles()
    triangles=[tuple(t.vertices) for t in source.data.loop_triangles
        if (source.data.vertices[t.vertices[1]].co-source.data.vertices[t.vertices[0]].co).cross(
            source.data.vertices[t.vertices[2]].co-source.data.vertices[t.vertices[0]].co).length_squared>1e-14]
    if not triangles:raise ValueError('No non-degenerate supporting surface for '+target.name)
    tree=BVHTree.FromPolygons([v.co for v in source.data.vertices],triangles,all_triangles=True)
    for g in source.vertex_groups:
        if target.vertex_groups.get(g.name) is None:target.vertex_groups.new(name=g.name)
    basis=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
    for v in (vertices if vertices is not None else target.data.vertices):
        hit,_,index,_=tree.find_nearest(v.co)
        if hit is None:raise ValueError('No supporting triangle for '+target.name)
        indices=triangles[index];pts=[source.data.vertices[i].co for i in indices]
        bary=barycentric_transform(hit,*pts,*basis)
        weights={}
        for i,influence in zip(indices,bary):
            for g in source.data.vertices[i].groups:
                key=source.vertex_groups[g.group].name;weights[key]=weights.get(key,0)+g.weight*max(0,influence)
        total=sum(weights.values())
        if total<=1e-8:raise ValueError('Supporting surface is unweighted')
        for g in list(v.groups):target.vertex_groups[g.group].remove([v.index])
        for key,value in weights.items():target.vertex_groups[key].add([v.index],value/total,'REPLACE')

def fitted_grid(body,arm,name,vertices,faces,m):
    """Small accessory surface, interpolating its real supporting surface."""
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o)
    surface_weights(body,o)
    setmat(o,m);bind(o,arm)
    for polygon in o.data.polygons:polygon.use_smooth=True
    return o

def glasses(arm,eye_z):
    pieces=[]
    for x in [-.033,.033]:
        bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=6,location=(x,.092,eye_z),
            rotation=(math.pi/2,0,0),major_radius=.023,minor_radius=.0025)
        o=bpy.context.object;o.scale=(1.22,.80,1)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        pieces.append(o)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.094,eye_z+.003))
    bridge=bpy.context.object;bridge.scale=(.016,.005,.004)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);pieces.append(bridge)
    bpy.ops.object.select_all(action='DESELECT')
    for o in pieces:o.select_set(True)
    bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join()
    o=pieces[0];o.name='Glasses';setmat(o,material('shoes'));bind_rigid(o,arm,'Head')

def soft_box(name,center,size,m,arm,bone):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    o=bpy.context.object;o.name=name;o.scale=size
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bevel=o.modifiers.new('Soft manufactured edges','BEVEL');bevel.width=.025;bevel.segments=2
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    setmat(o,m);bind_rigid(o,arm,bone)
    return o

def strap(name,points,width,m,body,arm,surface=None):
    if surface is not None:
        tree=BVHTree.FromPolygons([v.co for v in surface.data.vertices],[list(f.vertices) for f in surface.data.polygons])
        subdivided=[]
        samples=[Vector(a).lerp(Vector(b),i/5) for a,b in zip(points,points[1:]) for i in range(5)]+[Vector(points[-1])]
        for p in samples:
                # Project to the chosen face of the garment, avoiding the
                # nearest-triangle flips around shoulders and narrow openings.
                if name.startswith(('Backpack_strap','Bag_strap','Bag_rear_strap')):
                    hit,normal,_,_=tree.find_nearest(p)
                else:
                    hit,normal,_,_=tree.ray_cast(Vector((p.x,math.copysign(1,p.y or 1),p.z)),Vector((0,-math.copysign(1,p.y or 1),0)))
                if hit is None:hit,normal,_,_=tree.find_nearest(p)
                if hit is None:raise ValueError('Strap has no supporting garment surface')
                if normal.dot(Vector((hit.x,hit.y,0)))<0:normal=-normal
                p=hit+normal*(.027 if name.startswith(('Backpack_strap','Bag_strap','Bag_rear_strap')) else .009)
                subdivided.append(tuple(p))
        points=subdivided
    verts=[]
    for i,point in enumerate(points):
        p=Vector(point);across=Vector((width/2,0,0))
        if surface is not None:
            _,normal,_,_=tree.find_nearest(p)
            tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
            cross=normal.cross(tangent)
            if cross.length>.0001:
                across=cross.normalized()*width/2
                # Keep a ribbon's two edges continuous as it crosses a seam.
                if i and across.dot(last_across)<0:across=-across
        last_across=across.copy()
        verts.extend([tuple(p-across),tuple(p+across)])
    faces=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(points)-1)]
    o=fitted_grid(surface if surface is not None else body,arm,name,verts,faces,m)
    if name.startswith('Apron_shoulder_tie'):
        naturalism.torso_weights(o,arm)
    return o

def edge_finish(o,ratio,hem,cuff,trim,zipper=False):
    """Manufactured cloth edges in the shared pattern, not per-NPC retouching."""
    bm=bmesh.new();bm.from_mesh(o.data)
    planes=[((0,0,(hem+.035)*ratio),(0,0,1))]
    if cuff:planes.extend([((s*(cuff-.033)*ratio,0,0),(1,0,0)) for s in [-1,1]])
    if zipper:planes.extend([((s*.006*ratio,0,0),(1,0,0)) for s in [-1,1]])
    for point,normal in planes:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=point,plane_no=normal)
    bm.to_mesh(o.data);bm.free();o.data.materials.append(trim);slot=len(o.data.materials)-1
    for f in o.data.polygons:
        p=sum((o.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
        if p.z<(hem+.035)*ratio or (cuff and abs(p.x)>(cuff-.033)*ratio) or (zipper and p.y>0 and abs(p.x)<.006*ratio):f.material_index=slot

def pattern_edges(o,hem,neck,cuff,tol=None):
    """Constrain the cut loops, not an arbitrary band of nearby vertices.

    Face-centroid culling followed by smoothing leaves uneven boundary heights.
    In a long coat those small differences become saw-tooth hems. Preserve the
    inherited rig/weights and give each existing boundary its actual sewing line.
    """
    bm=bmesh.new();bm.from_mesh(o.data)
    for v in bm.verts:
        if not v.is_boundary:continue
        choices=[(abs(v.co.z-hem),'hem'),(abs(abs(v.co.x)-cuff),'cuff')]
        if abs(v.co.x)<.18:choices.append((abs(v.co.z-neck),'neck'))
        best=min(choices)
        if tol is not None and best[0]>tol:continue
        boundary=best[1]
        if boundary=='hem':v.co.z=hem
        elif boundary=='neck':v.co.z=neck
        else:v.co.x=math.copysign(cuff,v.co.x)
    bm.to_mesh(o.data);bm.free();o.data.update()

def layer_top(r,body,arm,top,ratio,neck,cuff,topmat,accent,trim):
    if r['top'] in ['cardigan','light_coat']:
        setmat(top,accent);top.name='Inner_shirt'
        # Both layers inherit the same body weights. Hidden inner cloth is removed.
        # Fitted outer layer: 4.4 cm over the skin clears the 3 cm inner top. At 6.5 cm every jacket, cardigan and
        # coat read as the same boxy kimono with bell sleeves.
        outer,_=garment(body,'Outer_'+r['top'],lambda p:.97*ratio<p.z<neck and abs(p.x)<cuff,{'fitted':.042,'regular':.044,'loose':.059}[r.get('fit','regular')],topmat,
            planes=top_planes(.97*ratio,neck,cuff))
        sh=[arm.matrix_world@arm.data.bones['upperarm_'+sd].head_local for sd in ('l','r')]
        wr=[arm.matrix_world@arm.data.bones['hand_'+sd].head_local for sd in ('l','r')]
        for v in outer.data.vertices:
            if abs(v.co.x)<.24*ratio:continue
            i=0 if (v.co.x>0)==(sh[0].x>0) else 1
            d=(wr[i]-sh[i]).normalized();rel=v.co-sh[i];along=rel.dot(d)
            t=max(0,min(1,along/((wr[i]-sh[i]).length)))
            v.co=sh[i]+d*along+(rel-d*along)*(1-.14*t)    # sleeve tapers towards the cuff
        for v in outer.data.vertices:
            p=v.co
            if abs(p.x)>cuff-.008:p.x=math.copysign(cuff,p.x)
        # Keep the front intact until the shared neckline/tailoring pass.
        # The visible inner panel is then cut from that exact finished shell,
        # with matching weights, rather than an independently smoothed top.
        if r['top']=='light_coat':
            for v in outer.data.vertices:
                if v.co.z<1.09*ratio:
                    t=max(0,min(1,(v.co.z-.96*ratio)/(.13*ratio)))
                    v.co.z=(.77+.32*t)*ratio
                    v.co.x*=1.07-.07*t      # a straight coat skirt; the former 1.18/1.30 flare read as a bathrobe
                    v.co.y*=1.12-.12*t
        # A narrow welt gives the outer layer a readable functional pocket.
        for sign in [-1,1]:
            strap('Pocket_welt',[(sign*.14*ratio,.17*ratio,1.095*ratio),
                (sign*.225*ratio,.15*ratio,1.095*ratio)],
                .019*ratio,trim,outer,arm,surface=outer)
        return outer
    if r['top']=='hoodie':
        for v in top.data.vertices:
            if v.co.z<1.46*ratio and abs(v.co.x)<.25*ratio:
                v.co.x*=1.10;v.co.y*=1.14
        bpy.ops.mesh.primitive_torus_add(major_segments=28,minor_segments=8,
            major_radius=.115*ratio,minor_radius=.042*ratio,location=(0,-.038*ratio,1.54*ratio))
        hood=bpy.context.object;hood.name='Hood_down';hood.scale=(1.05,1.10,.75)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        # Relax the back of the hood down between the shoulders. A horizontal
        # full torus reads as a scarf; a hood has a thin front neck and a pouch.
        for v in hood.data.vertices:
            back=max(0,min(1,(-v.co.y/ratio+.01)/.19))
            v.co.z-=.10*ratio*back
            if v.co.y>0:v.co.z=1.535*ratio+(v.co.z-1.54*ratio)*.40
        setmat(hood,topmat);bind_rigid(hood,arm,'spine_03')
        # Visible inner neck layer remains part of the same reusable hoodie recipe.
        garment(body,'Hoodie_neck_layer',lambda p:1.53*ratio<p.z<1.57*ratio and abs(p.x)<.10*ratio,.010,accent)
        for sign in [-1,1]:
            strap('Hood_drawcord',[(sign*.045*ratio,.13*ratio,1.535*ratio),
                (sign*.05*ratio,.15*ratio,1.43*ratio)],
                .008*ratio,accent,top,arm,surface=top)
    return top

def skirt(body,arm,ratio,m,hem_material,hem=.62):
    verts=[];faces=[];rows=10;segments=48
    for j in range(rows+1):
        t=j/rows;z=(hem+(1.02-hem)*t)*ratio
        flare=1+(.62-hem)*.55
        rx=(.275*flare-.075*t*flare)*ratio;ry=(.215*flare-.050*t*flare)*ratio
        for i in range(segments):
            a=2*math.pi*i/segments
            pleat=1+.025*(1-t)*math.cos(8*a)
            verts.append((rx*pleat*math.cos(a),ry*pleat*math.sin(a)-.022*ratio,z))
    for j in range(rows):
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
    o=fitted_grid(body,arm,'Knee_skirt',verts,faces,m)
    # A skirt hangs from the pelvis. Nearest-leg weights split the hem; a rigid pelvis skirt let the stepping
    # knee punch through the hem (visible notch in walk). Continuous drape weights (no tear across the centre)
    # let the lower skirt follow both thighs a little.
    drape_weights(o,ratio,strength=.52 if hem>.5 else .34)
    o.data.materials.append(hem_material)
    for f in o.data.polygons:
        z=sum(o.data.vertices[i].co.z for i in f.vertices)/len(f.vertices)
        if z<(hem+.055)*ratio or z>.99*ratio:f.material_index=1
    return o

def practical_accessories(r,body,arm,ratio,accent,shoe,topmat,surface):
    acc=[r['accessory']]+list(r.get('extras',[]))
    if 'backpack' in acc:
        bag=soft_box('Backpack',(0,-.235*ratio,1.27*ratio),(.29*ratio,.15*ratio,.39*ratio),shoe,arm,'spine_02')
        for v in bag.data.vertices:
            t=max(0,min(1,(v.co.z/ratio-1.25)/.20));v.co.x*=1-.18*t
        soft_box('Backpack_front_pocket',(0,-.323*ratio,1.16*ratio),(.22*ratio,.045*ratio,.13*ratio),accent,arm,'spine_02')
        for sign in [-1,1]:
            naturalism.shoulder_ribbon(surface,ratio,sign*.145,.035,shoe,'Backpack_strap_'+str(sign))
    if 'shoulder_bag' in acc:
        soft_box('Shoulder_bag',(.285*ratio,-.012*ratio,1.015*ratio),(.15*ratio,.20*ratio,.23*ratio),shoe,arm,'pelvis')
        strap('Bag_strap',[(.14*ratio,-.02*ratio,1.5*ratio),(.18*ratio,.16*ratio,1.37*ratio),
            (.245*ratio,.17*ratio,1.16*ratio),(.285*ratio,.09*ratio,1.06*ratio)],.026*ratio,shoe,surface,arm,surface=surface)
        strap('Bag_rear_strap',[(.14*ratio,-.02*ratio,1.5*ratio),(.18*ratio,-.18*ratio,1.37*ratio),
            (.245*ratio,-.18*ratio,1.16*ratio),(.285*ratio,-.11*ratio,1.06*ratio)],.026*ratio,shoe,surface,arm,surface=surface)
    if 'watch' in acc:
        # A watch sits on the forearm just above the wrist joint and follows the forearm, not the hand
        # (hand-bound, it floated off the wrist whenever the hand bent). Band and case fit the measured wrist.
        wrist=arm.matrix_world@arm.data.bones['hand_r'].head_local
        axis=(wrist-arm.matrix_world@arm.data.bones['lowerarm_r'].head_local).normalized()
        center=wrist-axis*.035*ratio
        ring=[(v.co-center)-axis*(v.co-center).dot(axis) for v in body.data.vertices if abs((v.co-center).dot(axis))<.012*ratio and (v.co-center).length<.08*ratio]
        radius=(sum(r.length for r in ring)/len(ring) if ring else .028*ratio)+.005*ratio
        bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=radius,depth=.020*ratio,location=center)
        o=bpy.context.object;o.name='Wristwatch_band'
        o.rotation_mode='QUATERNION';o.rotation_quaternion=Vector((0,0,1)).rotation_difference(axis)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.normal.dot(axis))>.9],context='FACES')   # open band, no caps
        bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:p.use_smooth=True
        setmat(o,shoe);bind_rigid(o,arm,'lowerarm_r')
        up=Vector((0,0,1));up=(up-axis*up.dot(axis)).normalized()
        face=soft_box('Wristwatch_case',tuple(center+up*(radius+.003*ratio)),(.030*ratio,.030*ratio,.008*ratio),shoe,arm,'lowerarm_r')

def body_section(objs,z,ratio,zwin=.012,xlim=.30):
    """Front/back surface and half width of the clothed rest-pose silhouette at height z (arms excluded)."""
    for k in (1,2,4,8):
        xs=[];ys=[]
        for o in objs:
            for v in o.data.vertices:
                c=v.co
                if abs(c.z-z)<zwin*k*ratio and abs(c.x)<xlim*ratio:xs.append(abs(c.x));ys.append(c.y)
        if len(xs)>=12:return max(xs),max(ys),min(ys)
    raise ValueError('No body section at z=%.3f'%z)

def drape_weights(o,ratio,strength=.55,fall=.55,blend=.16):
    """Hang a front panel from the pelvis but let its lower part follow both thighs.

    Weight to each thigh blends continuously across the centre line (no tear), grows towards the hem and is capped,
    so the panel swings with the walk instead of standing away from the legs like a placard."""
    o.vertex_groups.clear()
    groups={n:o.vertex_groups.new(name=n) for n in ('pelvis','thigh_l','thigh_r')}
    for v in o.data.vertices:
        t=max(0,min(1,(1.0-v.co.z/ratio)/fall))*strength
        wl=max(0,min(1,.5-v.co.x/(blend*ratio)))          # the left bone sits at negative x
        groups['thigh_l'].add([v.index],t*wl,'REPLACE');groups['thigh_r'].add([v.index],t*(1-wl),'REPLACE')
        groups['pelvis'].add([v.index],1-t,'REPLACE')

def wrap_sheet(surfaces,body,arm,ratio,name,rows,arc_fn,margin_fn,m,hem_lift=.05,segments=26):
    """A garment sheet that follows the measured clothed cross-section at every row.

    Row z (body-height units) -> elliptical section (half width, front/back depth) plus cloth margin,
    smoothed across rows; arc_fn(z,rx) gives the half angle covered. Replaces a flat depth function
    that stuck out from the hips (and, when measured on bare skin, sank inside baggy trousers)."""
    raw=[body_section(surfaces,z0*ratio,ratio) for z0 in rows]
    def smooth(values):
        for _ in range(3):
            values=[values[max(0,i-1)]*.25+values[i]*.5+values[min(len(values)-1,i+1)]*.25 for i in range(len(values))]
        return values
    hw=smooth([x[0] for x in raw]);ymax=smooth([x[1] for x in raw]);ymin=smooth([x[2] for x in raw])
    verts=[];faces=[];nz=len(rows)
    for ri,z0 in enumerate(rows):
        z=z0*ratio;mg=margin_fn(z0)*ratio
        rx=hw[ri]+mg;ry=(ymax[ri]-ymin[ri])/2+mg;cy=(ymax[ri]+ymin[ri])/2;a=arc_fn(z0,rx)
        for c in range(segments+1):
            u=-1+2*c/segments;th=u*a
            # Superellipse (p=2.8): flatter front and straighter flanks than an ellipse, like hips + thighs.
            sn,cs=math.sin(th),math.cos(th);e=2/2.8
            verts.append((rx*math.copysign(abs(sn)**e,sn),cy+ry*math.copysign(abs(cs)**e,cs),z+(hem_lift*ratio*abs(u)**4 if ri==0 else 0)))
    for r in range(nz-1):
        for c in range(segments):
            i=r*(segments+1)+c;faces.append((i,i+segments+1,i+segments+2,i+1))
    o=fitted_grid(body,arm,name,verts,faces,m)
    # A front apron follows the advancing thigh below the hip. The old
    # slow .55 falloff left large trouser silhouettes through the panel.
    # The narrow continuous centre blend avoids a split; skirts retain
    # their independent, lighter drape envelope.
    drape_weights(o,ratio,strength=.99,fall=.25,blend=.10)
    return o

def darker(hexcolor,f):
    return ''.join(f'{int(int(hexcolor[i:i+2],16)*f):02X}' for i in (0,2,4))

def surface_tree(o):
    return BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])

def ellipsoid(name,center,radii,m,arm,bone,tilt=(0,0,0),segments=28,rings=14):
    """Smooth rigid head/body accessory volume (berets, crowns, knots)."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=center,rotation=tilt)
    o=bpy.context.object;o.name=name;o.scale=radii
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    setmat(o,m);bind_rigid(o,arm,bone)
    return o

def cylinder(name,center,radius,depth,m,arm,bone,verts=32,bevel=.004,taper=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=center)
    o=bpy.context.object;o.name=name
    if taper!=1.0:
        for v in o.data.vertices:
            if v.co.z>0:v.co.x*=taper;v.co.y*=taper
    if bevel:
        mod=o.modifiers.new('Bevel','BEVEL');mod.width=bevel;mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in o.data.polygons:p.use_smooth=True
    setmat(o,m);bind_rigid(o,arm,bone)
    return o

def skull_dome(body,arm,ratio,name,cut,margin,m,rim=None,flat=1.0):
    """Half-ellipsoid crown fitted to the skull measured above the ears; optional turned-up rim band.

    Returns the front surface y at the cut height (for brims)."""
    top=[v.co for v in body.data.vertices if v.co.z>1.745*ratio]
    if len(top)<20:raise ValueError('No skull above the ears for '+name)
    ys=[p.y for p in top];cy=(max(ys)+min(ys))/2
    hx=max(abs(p.x) for p in top)*1.05+margin*ratio;hy=(max(ys)-min(ys))/2*1.04+margin*ratio
    crown=max(p.z for p in top);zc=cut*ratio;hz=(crown-zc+margin*ratio)*flat
    # Fit each crown ring to the actual skull. A single ellipsoid measured
    # only above the ears was too narrow at the temples, letting scalp/hair
    # break through caps when the head turned.
    tree=surface_tree(body);verts=[];faces=[];segments=48;rows=14
    for row in range(rows):
        t=row/rows;z=zc+(crown-zc)*math.sin(t*math.pi/2)
        for i in range(segments):
            a=2*math.pi*i/segments;d=Vector((math.sin(a),math.cos(a),0))
            hit=tree.ray_cast(Vector((0,cy,z)),d,.4*ratio)[0]
            if hit is None:hit=Vector((hx*math.cos(t*math.pi/2)*d.x,cy+hy*math.cos(t*math.pi/2)*d.y,z))
            hit+=d*margin*ratio;hit.z+=(margin*ratio)*math.sin(t*math.pi/2)
            verts.append(tuple(hit))
    verts.append((0,cy,crown+margin*ratio))
    for row in range(rows-1):
        for i in range(segments):
            j=row*segments+i;k=row*segments+(i+1)%segments;faces.append((j,k,k+segments,j+segments))
    for i in range(segments):faces.append(((rows-1)*segments+i,(rows-1)*segments+(i+1)%segments,len(verts)-1))
    o=fitted_grid(body,arm,name,verts,faces,m)
    for p in o.data.polygons:p.use_smooth=True
    setmat(o,m);bind_rigid(o,arm,'Head')
    if rim:
        height,out=rim
        bpy.ops.mesh.primitive_cylinder_add(vertices=36,radius=1,depth=height*ratio,location=(0,cy,zc+height*ratio/2))
        band=bpy.context.object;band.name=name+'_rim';band.scale=(hx+out*ratio,hy+out*ratio,1)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        bm=bmesh.new();bm.from_mesh(band.data)
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.normal.z)>.9],context='FACES')
        bm.to_mesh(band.data);bm.free()
        for p in band.data.polygons:p.use_smooth=True
        setmat(band,m);bind_rigid(band,arm,'Head')
    return verts[0][1]

def headwear(r,body,arm,ratio,topmat,accent,trim,cap_mat):
    kind=r.get('headwear','none')
    if kind=='none':return
    if kind=='cap':
        # Smooth six-panel crown on the measured skull (a crown cut from head topology picked up the ear tips as spikes).
        # Longer, down-curved bill (a short flat bill on a smooth dome read as a hard hat). The crown must stay
        # above the skull: flattening it let the scalp poke through (seen in the CASCO, 2026-09-30).
        front=skull_dome(body,arm,ratio,'Work_cap',1.716,.010,cap_mat)
        verts=[]
        for i in range(13):
            x=(-.10+.20*i/12)*ratio
            for t in [0,.5,1]:verts.append((x,front-.012*ratio+t*.088*ratio*(1-(x/(.118*ratio))**2),(1.728-.010*t-.014*t*t)*ratio))
        brim=fitted_grid(body,arm,'Cap_brim',verts,[f for i in range(12) for f in ((3*i,3*i+1,3*i+4,3*i+3),(3*i+1,3*i+2,3*i+5,3*i+4))],cap_mat)
        bind_rigid(brim,arm,'Head')
    elif kind=='beret':
        # Txapela: a close band on the skull and a wide, flattened wool crown pulled to one side.
        band,_=garment(body,'Beret_band',lambda p:p.z>1.742*ratio,.013,cap_mat);bind_rigid(band,arm,'Head')
        ellipsoid('Beret_crown',(.022*ratio,-.006*ratio,1.792*ratio),(.150*ratio,.156*ratio,.050*ratio),cap_mat,arm,'Head',tilt=(math.radians(-4),math.radians(9),0))
        cylinder('Beret_stalk',(.024*ratio,-.004*ratio,1.842*ratio),.008*ratio,.020*ratio,cap_mat,arm,'Head',verts=10,bevel=.002)
    elif kind=='beanie':
        # Fisherman's watch cap: smooth knit dome plus a turned-up cuff of the same yarn.
        skull_dome(body,arm,ratio,'Beanie_crown',1.708,.016,cap_mat,rim=(.040,.008))
    elif kind=='flatcap':
        band,_=garment(body,'Flatcap_band',lambda p:p.z>1.745*ratio,.015,cap_mat);bind_rigid(band,arm,'Head')
        ellipsoid('Flatcap_crown',(0,.018*ratio,1.786*ratio),(.132*ratio,.146*ratio,.036*ratio),cap_mat,arm,'Head',tilt=(math.radians(6),0,0))
        verts=[]
        for i in range(13):
            x=(-.10+.20*i/12)*ratio
            for t in [0,1]:verts.append((x,(.082+t*(.06*(1-(x/(.115*ratio))**2)))*ratio,(1.775-.012*t)*ratio))
        brim=fitted_grid(body,arm,'Flatcap_brim',verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(12)],cap_mat)
        bind_rigid(brim,arm,'Head')
    elif kind=='fedora':
        cylinder('Hat_brim',(0,.004*ratio,1.752*ratio),.185*ratio,.007*ratio,cap_mat,arm,'Head',verts=40,bevel=.003)
        cylinder('Hat_crown',(0,-.004*ratio,1.808*ratio),.090*ratio,.115*ratio,cap_mat,arm,'Head',verts=32,bevel=.014,taper=.90)
        cylinder('Hat_band',(0,-.004*ratio,1.772*ratio),.096*ratio,.022*ratio,trim,arm,'Head',verts=32,bevel=.003)
    else:raise ValueError('Unsupported headwear '+kind)

def neck_band(body,arm,ratio,name,m,low,high,margin,split=False):
    """A continuous measured neck loop instead of centroid-cut anatomical triangles.

    The old collars inherited diagonal neck/shoulder topology and retained
    spikes. A sewn loop has explicit, smooth upper/lower boundaries and
    interpolated weights from the same body, including head/neck blending.
    """
    rx,yf,yb=body_section([body],1.585*ratio,ratio,zwin=.005,xlim=.10)
    rx=min(rx,.070*ratio)+margin*ratio
    ry=min((yf-yb)/2,.065*ratio)+margin*ratio;cy=(yf+yb)/2
    verts=[];faces=[];segments=48;rows=4;skin_tree=surface_tree(body)
    for row in range(rows):
        t=row/(rows-1)
        for i in range(segments+1):
            a=(.13 if split else 0)+(2*math.pi-(.26 if split else 0))*i/segments
            front=max(0,math.cos(a));z=(low+(high-low)*t-.018*front*t)*ratio
            # Slightly folded top edge; the scarf has a restrained asymmetric
            # wrap. All offsets are millimetres, not floating accessory scale.
            lip=1+.035*math.sin(math.pi*t)
            direction=Vector((math.sin(a),math.cos(a),0))
            verts.append((rx*math.sin(a)*lip,cy+ry*math.cos(a)*lip,z))
    for row in range(rows-1):
        for i in range(segments):
            k=row*(segments+1)+i;faces.append((k,k+1,k+segments+2,k+segments+1))
    band=fitted_grid(body,arm,name,verts,faces,m)
    naturalism.torso_weights(band,arm)
    for p in band.data.polygons:p.use_smooth=True
    return band

def scarf(body,arm,ratio,m,top,trim):
    return neck_band(body,arm,ratio,'Scarf_wrap',m,1.505,1.582,.025)

def collar(body,arm,ratio,m,top):
    return neck_band(body,arm,ratio,'Collar',m,1.558,1.594,.007,split=True)

def settle_hair(skin,meshes,arm):
    """Seat only nearby scalp roots. Ponytail/bob ends and outer clumps retain their silhouette."""
    tree=surface_tree(skin);eye=arm.data.bones['Head'].head_local.z
    for o in meshes:
        if not o.name.startswith('Hair'):continue
        for v in o.data.vertices:
            # Scalp-facing edge, excluding low fringe over the eye/face.
            if v.co.z<eye+.045 and v.co.y>0:continue
            hit,normal,_,distance=tree.find_nearest(v.co)
            if hit is not None and .003<distance<.022 and normal.dot(v.co-hit)>0:
                v.co=hit+(v.co-hit).normalized()*(.002+distance*.30)
        o.data.update()

def tie(top,arm,ratio,m):
    strap('Tie',[(0,.098*ratio,1.505*ratio),(0,.138*ratio,1.40*ratio),(0,.168*ratio,1.22*ratio)],.036*ratio,m,top,arm,surface=top)
    strap('Tie_knot',[(0,.092*ratio,1.522*ratio),(0,.108*ratio,1.492*ratio)],.050*ratio,m,top,arm,surface=top)

def bowtie(top,arm,ratio,m):
    tree=surface_tree(top)
    for sign in [-1,1]:
        verts=[]
        for x,z in [(sign*.008,1.515),(sign*.048,1.503),(sign*.048,1.538),(sign*.008,1.529)]:
            hit=tree.ray_cast(Vector((x*ratio,1,z*ratio)),Vector((0,-1,0)))[0]
            if hit is None:raise ValueError('Bow tie lacks shirt backing')
            verts.append((x*ratio,hit.y+.011*ratio,z*ratio))
        fitted_grid(top,arm,'Bowtie_wing',verts,[(0,1,2,3)],m)
    hit=tree.ray_cast(Vector((0,1,1.522*ratio)),Vector((0,-1,0)))[0]
    if hit is None:raise ValueError('Bow tie knot lacks shirt backing')
    ellipsoid('Bowtie_knot',(0,hit.y+.016*ratio,1.522*ratio),(.011*ratio,.005*ratio,.012*ratio),m,arm,'spine_03',segments=12,rings=6)

def refit_donor(arm,donor_arm,parts):
    """Move rest-pose donor geometry onto a body whose rest skeleton differs slightly (weighted bone-head delta)."""
    delta={}
    for bone in donor_arm.data.bones:
        if bone.name in arm.data.bones:
            delta[bone.name]=(arm.matrix_world@arm.data.bones[bone.name].head_local)-(donor_arm.matrix_world@bone.head_local)
    for o in parts:
        names={g.index:g.name for g in o.vertex_groups}
        for v in o.data.vertices:
            move=Vector();total=0
            for g in v.groups:
                d=delta.get(names.get(g.group))
                if d is not None:move+=d*g.weight;total+=g.weight
            if total>1e-8:v.co+=move/total
        o.data.update()

CLOTH_SLOTS=('top','bottom','accent','outer','trim','apron','cap','detail','hem','reflective','shoes','sole')

def fabric_uvs(meshes,arm):
    """World-scale fabric UVs (1 UV unit = 1 m) on every cloth/leather face, replacing inherited skin-atlas UVs.

    Garments cut from the body inherit its atlas islands, so the same fabric tile was stretched differently on
    every panel and every person (smudged chests, mismatched weave scale). Cylindrical projection per limb keeps
    knit columns vertical on the torso and along the arms and legs, with one texel density for the whole cast."""
    B=lambda n:arm.matrix_world@arm.data.bones[n].head_local
    axes={}
    for s in ('l','r'):
        axes['arm_'+s]=(B('upperarm_'+s),B('hand_'+s),.055)
        axes['leg_'+s]=(B('thigh_'+s),B('foot_'+s),.075)
    top=B('neck_01');axes['torso']=(Vector((0,B('spine_02').y,B('pelvis').z-.35)),Vector((0,B('spine_02').y,top.z)),.16)
    def region(name):
        for s in ('l','r'):
            if name.endswith('_'+s) and name.startswith(('upperarm','lowerarm','hand','thumb','index','middle','ring','pinky')):return 'arm_'+s
            if name.endswith('_'+s) and name.startswith(('thigh','calf','foot','ball')):return 'leg_'+s
        return 'torso'
    for o in meshes:
        slots=[i for i,m in enumerate(o.data.materials) if m and m.name.split('.')[0] in CLOTH_SLOTS]
        if not slots or not o.data.polygons:continue
        if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
        uv=o.data.uv_layers.active.data;names={g.index:g.name for g in o.vertex_groups};mw=o.matrix_world
        for poly in o.data.polygons:
            if poly.material_index not in slots:continue
            weight={}
            for vi in poly.vertices:
                for g in o.data.vertices[vi].groups:
                    k=region(names.get(g.group,''));weight[k]=weight.get(k,0)+g.weight
            key=max(weight,key=weight.get) if weight else 'torso'
            a,b,radius=axes[key];axis=(b-a).normalized()
            ref=Vector((0,1,0)) if abs(axis.y)<.9 else Vector((0,0,1))     # angle 0 at the front (+y), wrap seam at the back
            e1=(ref-axis*ref.dot(axis)).normalized();e2=axis.cross(e1)
            first=None
            for li in poly.loop_indices:
                p=(mw@o.data.vertices[o.data.loops[li].vertex_index].co)-a
                ang=math.atan2(p.dot(e2),p.dot(e1))
                if first is None:first=ang
                while ang-first>math.pi:ang-=2*math.pi
                while ang-first<-math.pi:ang+=2*math.pi
                uv[li].uv=(ang*radius,p.dot(axis))

def build(r,b,palette,output):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    arm,base=load(b['source']);body=max(base,key=lambda o:len(o.data.vertices))
    arm.name='CivilianRig';body.name='VisibleSkin'
    tones=COMPAT['skinTones'];tint=tones['tones'][r['skin']]
    skin=material('skin_'+r['body']+'_'+r['skin'],''.join(f'{min(255,round(b*int(tint[i:i+2],16)/255)):02X}' for b,i in zip(tones['baseRgb'],(0,2,4))))
    thick_brows=r.get('brows','default')=='thick'
    for o in list(base):
        if o==body:setmat(o,skin)
        elif o.name.startswith('Eyebrows'):
            if thick_brows or r.get('headForm'):
                bpy.data.objects.remove(o,do_unlink=True);continue
            setmat(o,material('hair',palette['hair']))
        else:
            for i,m in enumerate(o.data.materials):
                o.data.materials[i]=material('eyes','E4DED0') if 'Eyes' in m.name else material('lid','EFC4AA')
    topmat=material('top',palette['top']);bottommat=material('bottom',palette['bottom'])
    accent=material('accent',palette['accent']);shoe=material('shoes',palette['shoes'])
    # Optional distinct outer layer / cap colours; without them the established palette roles apply.
    outermat=material('outer',palette['outer']) if 'outer' in palette else accent
    capmat=material('cap',palette.get('cap',palette['top']))   # own slot: a sweater-knit cap read as a beanie
    trim=material('trim',''.join(f'{int(int(palette["top"][i:i+2],16)*.70):02X}' for i in (0,2,4)))
    h=b['nativeHeight'];ratio=h/1.81008;neck=1.565*ratio;waist=(.94 if r['top']=='shop_coat' else .99)*ratio
    if r.get('headForm'):
        form=FORMS['heads'][r['headForm']]
        centres=naturalism.sculpt_head(body,[o for o in bpy.data.objects if o.type=='MESH'],form,ratio)
        naturalism.brows(body,arm,centres,form,ratio,material('hair',palette['hair']),fitted_grid)
    short_sleeve=r['top'] in ['tshirt','jersey']
    cuff=(.43 if short_sleeve else .635)*ratio
    topkeep=lambda p:waist<p.z<neck and abs(p.x)<cuff
    ease={'fitted':.018,'regular':.024,'loose':.034}[r.get('fit','regular')]
    top,stats=garment(body,'Top_'+r['top'],topkeep,ease if not short_sleeve else ease-.003,topmat,
        planes=top_planes(waist,neck,cuff))
    # Reduce anatomical ridges in the cloth torso without changing limb binding.
    for v in top.data.vertices:
        p=v.co
        if abs(p.x)>cuff-.008:p.x=math.copysign(cuff,p.x)
    scoop={'shirt':.020,'shop_coat':.030,'jersey':.030,'tshirt':.032,'sweater':.018,'cardigan':.034,'light_coat':.034,'hoodie':0}.get(r['top'],.02)*ratio
    scoop_neck(top,neck,scoop,ratio)
    # Cut material-panel boundaries through the mesh, rather than assigning
    # jagged face-centroid stripes over the source body's irregular topology.
    bm=bmesh.new();bm.from_mesh(top.data)
    # Jersey stripes are real material bands cut through the shared torso, not a texture painted in body UV space.
    for x in ([-.21,-.15,-.09,-.03,.03,.09,.15,.21] if r['top']=='jersey' else [-.20,-.13,-.05,-.012,.012,.05,.13,.20]):
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
            plane_co=(x*ratio,0,0),plane_no=(1,0,0))
    for z in [1.10,1.22]:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
            plane_co=(0,0,z*ratio),plane_no=(0,0,1))
    bm.to_mesh(top.data);bm.free();top.data.update()
    if r['top'] in ['shirt','shop_coat']:
        # A single surface carries the placket: no nearly coincident cloth layers.
        top.data.materials.append(accent)
        for f in top.data.polygons:
            center=sum((top.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
            if center.y>.04 and abs(center.x)<.012*ratio:f.material_index=1
            if r['top']=='shop_coat' and center.y>.03 and .05*ratio<abs(center.x)<.13*ratio and 1.10*ratio<center.z<1.22*ratio:f.material_index=1
    outer=layer_top(r,body,arm,top,ratio,neck,cuff,topmat,accent,trim)
    if r.get('garmentPattern'):naturalism.finish_necklines(body,[o for o in bpy.data.objects if o.type=='MESH'],ratio,surface_weights)
    if r.get('garmentPattern'):
        naturalism.tailor([o for o in bpy.data.objects if o.type=='MESH'],ratio,FORMS['garmentPatterns'][r['garmentPattern']],r,fitted_grid,arm,trim)
    if r['top'] in ['cardigan','light_coat']:
        naturalism.line_open_layer(outer,top,ratio,accent)
    if r['top']=='jersey':
        top.data.materials.append(accent)   # slot 1: alternate stripe
        for f in top.data.polygons:
            c=sum((top.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
            if abs(c.x)<.215*ratio:f.material_index=int((abs(c.x)/ratio+.03)/.06)%2
        edge_finish(top,ratio,waist/ratio,cuff/ratio,trim)   # slot 2: dark ribbed hem, collar and cuffs
        slot=len(top.data.materials)-1
        for f in top.data.polygons:
            c=sum((top.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
            if abs(c.x)>=.215*ratio:f.material_index=slot   # solid sleeves keep the stripes readable on the torso
    if r['top'] in ['sweater','hoodie','tshirt']:edge_finish(top,ratio,waist/ratio,cuff/ratio,trim)
    donor,parts=load(b['donor'])
    shared=set(x.name for x in arm.data.bones)&set(x.name for x in donor.data.bones)
    delta=max(((arm.matrix_world@arm.data.bones[n].head_local)-(donor.matrix_world@donor.data.bones[n].head_local)).length for n in shared)
    if len(shared)!=65:raise ValueError('Incompatible donor rest rig')
    if delta>.0001:
        # Same 65-bone family with a measurably different rest skeleton (Superhero male): move the donor
        # footwear/leg geometry through its own bone weights onto this body. Bounded so a wrong family still fails.
        if not b.get('refitDonor') or delta>.035:raise ValueError('Incompatible donor rest rig')
        refit_donor(arm,donor,parts)
    for o in parts:
        if 'Feet' in o.name:
            cutoff={'work_shoes':.20,'work_boots':.31,'loafers':.16,'trainers':.175,'ankle_boots':.28}[r['footwear']]*ratio
            bm=bmesh.new();bm.from_mesh(o.data)
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
                plane_co=(0,0,cutoff),plane_no=(0,0,1))
            bm.to_mesh(o.data);bm.free()
            cull(o,lambda p:p.z<cutoff)
            # Each footwear family has a different toe/sole volume, not only a cuff cut.
            for v in o.data.vertices:
                if v.co.z<.115*ratio:
                    foot_center=math.copysign(.09*ratio,v.co.x)
                    width={'work_shoes':1.02,'work_boots':1.10,'loafers':.95,'trainers':1.09,'ankle_boots':1.0}[r['footwear']]
                    v.co.x=foot_center+(v.co.x-foot_center)*width
                    if v.co.y>.025*ratio:
                        length={'work_shoes':.90,'work_boots':.93,'loafers':.87,'trainers':.89,'ankle_boots':.94}[r['footwear']]
                        v.co.y=.025*ratio+(v.co.y-.025*ratio)*length
            o.name='Donor_'+r['footwear'];setmat(o,shoe);bind(o,arm)
            if r['footwear']=='trainers':
                o.data.materials.append(material('sole','BEBFB5'))
                for f in o.data.polygons:
                    if sum(o.data.vertices[i].co.z for i in f.vertices)/len(f.vertices)<.033*ratio:f.material_index=1
        elif 'Legs' in o.name and r['bottom']=='work':
            lower=min(v.co.z for v in o.data.vertices)
            pivot=.65*ratio
            for v in o.data.vertices:
                if v.co.z<pivot:
                    v.co.z=.11*ratio+(v.co.z-lower)*(pivot-.11*ratio)/(pivot-lower)
            o.name='Donor_work_trousers';setmat(o,bottommat);bind(o,arm)
        else:bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.objects.remove(donor,do_unlink=True)
    if r['bottom'] in ['straight','overalls']:
        pants,pantsstats=garment(body,'Straight_trousers',lambda p:.14*ratio<p.z<1.045*ratio,.019,bottommat,
            planes=[((0,0,.14*ratio),(0,0,1)),((0,0,1.045*ratio),(0,0,1))])
        for v in pants.data.vertices:
            if v.co.z<.55*ratio:
                center=.095*ratio*(1 if v.co.x>0 else -1)
                v.co.x=center+(v.co.x-center)*1.18
        stats['pants']=pantsstats
    elif r['bottom']=='skirt':skirt(body,arm,ratio,bottommat,material('hem',darker(palette['bottom'],.80)))
    elif r['bottom']=='long_skirt':skirt(body,arm,ratio,bottommat,material('hem',darker(palette['bottom'],.80)),hem=.42)
    if r['bottom']=='overalls':
        # Bib-and-brace: same trouser cloth, a chest bib and continuous straps
        # cut on the supporting sweater with the same shoulder skin weights.
        tree=surface_tree(top);bv=[];bf=[];cols=9;rows=[1.02,1.06,1.10,1.14,1.18,1.22,1.26,1.30,1.34,1.37]
        for z0 in rows:
            half=(.190-.055*max(0,(z0-1.20)/.17))*ratio
            for c in range(cols):
                x=(-1+2*c/(cols-1))*half
                hit=tree.ray_cast(Vector((x,1.0,z0*ratio)),Vector((0,-1,0)))[0]
                y=(hit.y if hit is not None else .13*ratio)+.011*ratio
                bv.append((x,y,z0*ratio))
        for j in range(len(rows)-1):
            for c in range(cols-1):
                i=j*cols+c;bf.append((i,i+cols,i+cols+1,i+1))
        bib=fitted_grid(top,arm,'Overall_bib',bv,bf,bottommat)
        for sign in [-1,1]:
            naturalism.shoulder_ribbon(top,ratio,sign*.108,.052,bottommat,'Overall_strap_'+str(sign),bottom=1.045)
        pv=[];pf=[]
        for z0 in [1.13,1.235]:
            for c in range(7):
                x=(-.075+.15*c/6)*ratio
                hit=tree.ray_cast(Vector((x,1.0,z0*ratio)),Vector((0,-1,0)))[0]
                pv.append((x,(hit.y if hit is not None else .13*ratio)+.019*ratio,z0*ratio))
        for c in range(6):pf.append((c,c+7,c+8,c+1))
        pocket=fitted_grid(bib,arm,'Overall_pocket',pv,pf,trim)
        # Buttoned side straps read as hardware, not another tint of trouser cloth.
        for sign in [-1,1]:
            ellipsoid('Overall_button',(sign*.118*ratio,.158*ratio,1.345*ratio),(.013*ratio,.008*ratio,.013*ratio),accent,arm,'spine_03',segments=10,rings=6)
    acc=[r['accessory']]+list(r.get('extras',[]))
    apron_kind=next((a for a in acc if a in ('apron','bistro_apron')),None)
    detail=material('detail',palette['detail']) if 'detail' in palette else trim
    if apron_kind:
        bistro=apron_kind=='bistro_apron'
        amat=material('apron',palette['apron']) if 'apron' in palette else accent
        if bistro:
            rows=[round(.40+.04*i,3) for i in range(16)]   # shin to waist, wraps hips/thighs, open behind
            arc=lambda z0,rx:math.asin(min(.90,(.235-.045*max(0,min(1,(z0-.45)/.55)))*ratio/rx))
            margin=lambda z0:.055+.016*max(0,min(1,(.9-z0)/.5))
        else:
            rows=[.64,.68,.72,.76,.80,.84,.88,.92,.96,1.00,1.04,1.08,1.12,1.16,1.20,1.24,1.28,1.32,1.36]
            def arc(z0,rx):
                w=(.205+.04*max(0,min(1,(1.08-z0)/.44)) if z0<=1.08 else .205-.10*min(1,(z0-1.08)/.12))*ratio
                return math.asin(min(.86,w/rx))   # never wider than the clothed hips it hangs from
            margin=lambda z0:.046+.020*max(0,min(1,(.98-z0)/.18))+.010*max(0,min(1,(z0-1.04)/.2))
        clothed=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Top_','Straight_','Donor_work','VisibleSkin'))]
        apron=wrap_sheet(clothed,body,arm,ratio,'Shop_apron',rows,arc,margin,amat)
        tree=surface_tree(apron)
        pocketverts=[];pocketfaces=[]
        pz=[.605,.623,.745] if bistro else [.925,.943,1.06]
        for z in pz:
            for col in range(13):
                x=(-.12+.24*col/12)*ratio
                hit=tree.ray_cast(Vector((x,1.0,z*ratio)),Vector((0,-1,0)))[0]
                pocketverts.append((x,(hit.y if hit is not None else .17*ratio)+.006*ratio,z*ratio))
        for row in range(2):
            for col in range(12):
                i=row*13+col;pocketfaces.append((i,i+13,i+14,i+1))
        pocket=fitted_grid(body,arm,'Apron_pocket',pocketverts,pocketfaces,amat)
        pocket.data.materials.append(trim)
        for f in pocket.data.polygons:
            z=sum(pocket.data.vertices[i].co.z for i in f.vertices)/len(f.vertices)
            if z<(pz[1]+.007)*ratio:f.material_index=1
        drape_weights(pocket,ratio,strength=.99,fall=.25,blend=.10)
        beltverts=[];beltfaces=[]
        belt_src=pants if (bistro and r['bottom'] in ['straight','overalls']) else top
        belt_tree=surface_tree(belt_src)
        for z in ([.965,.995] if bistro else [1.085,1.115]):
            for i in range(40):
                a=2*math.pi*i/40;direction=Vector((math.cos(a),math.sin(a),0))
                hit=belt_tree.ray_cast(Vector((direction.x,direction.y,z*ratio)),-direction)[0]
                if hit is None:raise ValueError('Apron waist tie has no supporting garment surface')
                beltverts.append(tuple(hit+direction*.009))
        for i in range(40):beltfaces.append((i,(i+1)%40,(i+1)%40+40,i+40))
        belt=fitted_grid(belt_src,arm,'Apron_waist_tie',beltverts,beltfaces,amat)
        # Keep the sweater intact beneath the apron; it remains visible from
        # oblique views and avoids a hole when the torso rotates in Talking.
        for sign in ([] if bistro else [-1,1]):
            naturalism.shoulder_ribbon(top,ratio,sign*.105,.028,amat,'Apron_shoulder_tie_'+str(sign),bottom=1.09)
    # Finish the supporting shirt before cutting a second layer on it. Moving
    # its neck boundary afterwards separated the sewn shoulder edges.
    if 'work_vest' in acc or 'waistcoat' in acc:
        wc='waistcoat' in acc
        vest=naturalism.waistcoat(body,top,arm,ratio,outermat,fitted_grid,work=not wc,
            clearance=.013 if wc else .022+(.010 if r.get('fit')=='loose' else 0))
        if not wc:
            # Exact seam cuts on the supporting shirt preserve the entire
            # panel and its weights; centroid-cropped armholes left spikes.
            vest.data.materials.append(material('reflective','D8D9CA'))
            bm=bmesh.new();bm.from_mesh(vest.data)
            for z in [1.11,1.16,1.34,1.39]:
                bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
                    plane_co=(0,0,z*ratio),plane_no=(0,0,1))
            bm.to_mesh(vest.data);bm.free();vest.data.update()
            for f in vest.data.polygons:
                z=sum(vest.data.vertices[i].co.z for i in f.vertices)/len(f.vertices)
                if 1.11*ratio<z<1.16*ratio or 1.34*ratio<z<1.39*ratio:f.material_index=1
            edge_finish(vest,ratio,.97,0,trim,zipper=True)
    if 'glasses' in acc:glasses(arm,1.699*ratio)
    if 'collar' in acc:collar(body,arm,ratio,accent if r['top'] in ['cardigan','light_coat'] else topmat,top)
    if 'scarf' in acc:scarf(body,arm,ratio,detail,top,trim)
    if 'tie' in acc:tie(top,arm,ratio,detail)
    if 'bowtie' in acc:bowtie(top,arm,ratio,detail)
    practical_accessories(r,body,arm,ratio,accent,(material('detail',palette['detail']) if 'detail' in palette else shoe),topmat,outer)
    if 'work_vest' in acc or 'waistcoat' in acc:naturalism.mask_under_vest(top,ratio,work='work_vest' in acc)
    for lower in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Straight_trousers','Donor_work_trousers'))]:
        naturalism.mask_covered_waist(lower,ratio,waist/ratio)
    # Retain the complete weighted throat as fitting input. VisibleSkin is
    # deliberately masked below clothing; its disconnected head/hands cannot
    # supply the neck/clavicle weights for a replacement anatomical throat.
    neck_support=body.copy();neck_support.data=body.data.copy();neck_support.name='Neck_weight_support'
    bpy.context.scene.collection.objects.link(neck_support)
    if r['bottom'] in ['skirt','long_skirt']:
        hem_skin=.630 if r['bottom']=='skirt' else .430
        trim_body(body,cuff,neck,waist,scoop,ratio,leg_hem=hem_skin)
    else:trim_body(body,cuff,neck,waist,scoop,ratio)
    covering=r.get('headwear','none') in ['cap','beret','flatcap','fedora','beanie']
    def head_parts(source,name,slot,hexcolor,hide_crown=False):
        _,parts=load(source)
        for o in parts:
            # Standalone Origin-at-zero hair FBX faces the opposite axis to the rigged body FBX.
            # Both were measured on real sources; retaining its raw orientation puts ponytails over faces.
            o.data.transform(Matrix.Rotation(math.pi,4,'Z'))
            if hide_crown:
                limit=(1.705 if r['headwear']=='beanie' else 1.700 if r['headwear']=='cap' else 1.742)*ratio
                rear=-.08*ratio if r['headwear']=='cap' else 9e9   # a cap leaves the rear hair (ponytail base) attached
                cull(o,lambda p:p.z<limit or (p.y<rear and p.z<1.738*ratio))
            o.name=name;setmat(o,material(slot,hexcolor));bind_rigid(o,arm,'Head')
    if r.get('hairStyle'):
        naturalism.hair(body,arm,ratio,r['hairStyle'],FORMS['heads'][r['headForm']],material('hair',palette['hair']),bind_rigid,fitted_grid,ellipsoid,covering)
        naturalism.facial_hair(body,arm,ratio,r.get('facial',[]),material('beard',palette.get('beard',palette['hair'])),bind_rigid,fitted_grid)
    else:
        if r['hair']!='none':head_parts('base:'+r['hair'],'Hair','hair',palette['hair'],covering)
        for facial in r.get('facial',[]):head_parts('base:hair_'+facial,'Facial_'+facial,'beard',palette.get('beard',palette['hair']))
        if thick_brows:head_parts('base:eyebrows_thick','Brows_thick','hair',palette['hair'])
    headwear(r,body,arm,ratio,topmat,accent,trim,capmat)
    profiles={p['id']:p for p in json.loads((ROOT/'Docs/asset_catalog/char_body_profiles.json').read_text())['profiles']}
    metrics=shape_character(arm,[o for o in bpy.data.objects if o.type=='MESH'],profiles[r['profile']],h,b,COMPAT['anthropometry'])
    if not r.get('hairStyle'):settle_hair(body,[o for o in bpy.data.objects if o.type=='MESH'],arm)
    check_proportions(metrics,COMPAT['anthropometry'],r['body'])
    stats['bodyMetrics']=metrics
    human=char_human.replace_head(r,body,arm,metrics,bind,bind_rigid,surface_weights,neck_support)
    bpy.data.objects.remove(neck_support,do_unlink=True)
    if human:stats['humanHead']=human
    # Facings are subdivided and seated on their finished supporting coat.
    # A four-corner panel bridged curved cloth and cut into it in conversation.
    outer=next((o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Outer_')),None)
    if outer:
        tree=surface_tree(outer)
        for panel in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Pattern_')]:
            bm=bmesh.new();bm.from_mesh(panel.data)
            bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=3,use_grid_fill=True)
            for vertex in bm.verts:
                p=vertex.co
                hit=tree.ray_cast(Vector((p.x,1,p.z)),Vector((0,-1,0)))[0]
                if hit is not None:p.y=hit.y+.006
            bm.to_mesh(panel.data);bm.free();panel.data.update()
            surface_weights(outer,panel)
    for vest in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Waistcoat_panel_sewn','Work_vest_panel_sewn'))]:
        seam_support=vest.copy();seam_support.data=vest.data.copy()
        bpy.context.scene.collection.objects.link(seam_support)
        # Subdivide only open sewing lines and round their interpolated
        # corners within the inner shirt's 14 mm overlap. The original torso
        # triangulation must not dictate a saw-toothed armhole or neckline.
        bm=bmesh.new();bm.from_mesh(vest.data)
        edges=[e for e in bm.edges if e.is_boundary and e.calc_length()>.018]
        if edges:bmesh.ops.subdivide_edges(bm,edges=edges,cuts=2,use_grid_fill=False)
        seam=[v for v in bm.verts if v.is_boundary and v.co.z>metrics['height']*metrics['pelvisHeight']+.075]
        original={v:v.co.copy() for v in seam}
        for iteration in range(3):
            # A sewing line follows its boundary neighbours. Averaging with
            # arbitrary interior triangles made valence-dependent saw teeth.
            updates={}
            for v in seam:
                neighbours=[e.other_vert(v) for e in v.link_edges if e.is_boundary]
                if len(neighbours)==2:
                    updates[v]=v.co.lerp((neighbours[0].co+neighbours[1].co)*.5,.42)
            for v,point in updates.items():v.co=point
        for v in seam:
            seam_delta=v.co-original[v]
            if seam_delta.length>.006:v.co=original[v]+seam_delta.normalized()*.006
        bm.to_mesh(vest.data);bm.free();vest.data.update()
        # Explicitly interpolate from the finished, weighted garment. New
        # boundary vertices are not assumed to inherit BMesh deform data.
        surface_weights(seam_support,vest)
        bpy.data.objects.remove(seam_support,do_unlink=True)
        # A narrow sewn binding follows the actual open edges. It supplies a
        # controlled round-over instead of accidental knife-edge cut shading.
        bm=bmesh.new();bm.from_mesh(vest.data);bm.normal_update()
        vertices=[];faces=[];boundary=[v for v in bm.verts if v.is_boundary]
        indices={}
        for vertex in boundary:
            # One continuous strip shares corners around each sewing loop.
            # Separate edge quads had conflicting normals and overlapped as
            # little triangular tabs after skinning.
            normal=vertex.normal.normalized()
            inward=sum((f.calc_center_median()-vertex.co for f in vertex.link_faces),Vector())
            inward-=normal*inward.dot(normal)
            if inward.length<1e-6:continue
            inward.normalize()
            indices[vertex]=len(vertices)
            for row in range(3):
                t=row/2
                vertices.append(tuple(vertex.co+inward*(.006*t)+normal*(.0015+.0015*math.sin(t*math.pi))))
        for edge in bm.edges:
            if not edge.is_boundary:continue
            edge_a,edge_b=edge.verts
            if edge_a not in indices or edge_b not in indices:continue
            start_a,start_b=indices[edge_a],indices[edge_b]
            for row in range(2):
                faces.append((start_a+row,start_b+row,start_b+row+1,start_a+row+1))
        bm.free()
        if vertices:
            binding=fitted_grid(vest,arm,'Waistcoat_sewn_binding' if vest.name.startswith('Waistcoat') else 'Work_vest_sewn_binding',vertices,faces,vest.data.materials[0])
            bm=bmesh.new();bm.from_mesh(binding.data)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(binding.data);bm.free()
            for polygon in binding.data.polygons:polygon.use_smooth=True
    fabric_uvs([o for o in bpy.data.objects if o.type=='MESH'],arm)
    for o in bpy.data.objects:
        if o.type=='MESH' and not o.name.startswith(('VisibleSkin','Eyes','Donor_','Glasses')):orient_outward(o)
    for o in bpy.data.objects:
        if o.animation_data:o.animation_data_clear()
    arm.data.pose_position='REST'
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    for o in meshes:
        # Imported split normals describe the undeformed source. Recompute
        # after anatomical shaping (including skin and hair), or warped heads
        # retain the old face shading and a false dark neck seam.
        if o.data.has_custom_normals:o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops))
        if o.name.startswith(('Top_','Straight_','Shop_','Outer_','Inner_','Work_vest','Waistcoat')):
            for p in o.data.polygons:p.use_smooth=True
            o.data.update()
    for o in meshes:
        valid={g.index for g in o.vertex_groups if g.name in arm.data.bones}
        for v in o.data.vertices:
            total=sum(g.weight for g in v.groups if g.group in valid)
            if total>1e-8:
                for g in list(v.groups):
                    if g.group in valid:o.vertex_groups[g.group].add([v.index],g.weight/total,'REPLACE')
    unweighted=sum(1 for o in meshes for v in o.data.vertices if sum(g.weight for g in v.groups)<.99)
    if unweighted:
        print('WEIGHTS',[(o.name,len(o.vertex_groups),min(sum(g.weight for g in v.groups) for v in o.data.vertices)) for o in meshes])
    if unweighted:raise ValueError('Unweighted mesh vertices: '+str(unweighted))
    if len([o for o in bpy.data.objects if o.type=='ARMATURE'])!=1:raise ValueError('Duplicate rig')
    output.mkdir(parents=True,exist_ok=True);target=output/(r['id']+'.fbx')
    if output.resolve()==(ROOT/'Unity/JuegoDef/Assets/JuegoDef/Derived/CHAR/Models').resolve():
        master=ROOT/'Art/Characters/Naturalism'/ (r['id']+'.blend')
        master.parent.mkdir(parents=True,exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(master),check_existing=False,compress=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(target),use_selection=True,object_types={'ARMATURE','MESH'},
        add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_triangles=True,
        axis_forward='-Z',axis_up='Y',path_mode='STRIP',use_mesh_modifiers=True)
    sources=sorted(set([b['source'],b['donor']]+human_source_ids(r)))
    stats.update(id=r['id'],sourceIds=sources,
        bones=len(arm.data.bones),meshes=[{'name':o.name,'vertices':len(o.data.vertices),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),
            'blendShapes':[k.name for k in o.data.shape_keys.key_blocks if k.name!='Basis'] if o.data.shape_keys else []} for o in meshes],
        unweightedVertices=unweighted,donorRestDelta=delta,recipe=r,blender=bpy.app.version_string)
    stats['exportSha256']=hashlib.sha256(target.read_bytes()).hexdigest()
    # UV-sphere cap faces can be emitted in different order by Blender. Compare
    # polygon cycles independent of face order/start corner, preserving winding.
    def polygon_cycle(o,p):
        v=list(p.vertices)
        start=min(range(len(v)),key=lambda i:tuple(v[i:]+v[:i]))
        loops=list(p.loop_indices);loops=loops[start:]+loops[:start]
        uvs=[(layer.name,[[round(c,6) for c in layer.data[li].uv] for li in loops]) for layer in o.data.uv_layers]
        return (tuple(v[start:]+v[:start]),p.material_index,p.use_smooth,uvs)
    # Semantic identity excludes FBX timestamps and non-semantic polygon order.
    payload={'meshes':[(o.name,[[round(c,6) for c in v.co] for v in o.data.vertices],
            sorted(polygon_cycle(o,p) for p in o.data.polygons),
            [sorted((o.vertex_groups[g.group].name,round(g.weight,6)) for g in v.groups) for v in o.data.vertices],
            [m.name for m in o.data.materials],
            [(key.name,[[round(c,6) for c in v.co] for v in key.data],key.relative_key.name) for key in o.data.shape_keys.key_blocks] if o.data.shape_keys else []) for o in sorted(meshes,key=lambda o:o.name)],
        'rig':[(b.name,b.parent.name if b.parent else None,[round(c,6) for row in b.matrix_local for c in row]) for b in arm.data.bones]}
    stats['geometrySha256']=hashlib.sha256(json.dumps(payload,separators=(',',':')).encode()).hexdigest()
    return stats

def main():
    p=argparse.ArgumentParser();p.add_argument('--recipes');p.add_argument('--only');p.add_argument('--output')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    data,matrix=read_recipes(args.recipes);bodies={b['id']:b for b in matrix['bodies']};palettes={p['id']:p for p in data['palettes']}
    recipes=[r for r in data['recipes'] if not args.only or r['id']==args.only]
    if not recipes:raise ValueError('No matching recipe')
    output=Path(args.output) if args.output else ROOT/'Unity/JuegoDef/Assets/JuegoDef/Derived/CHAR/Models'
    reports=[build(r,bodies[r['body']],palettes[r['palette']],output) for r in recipes]
    report=ROOT/'Docs/evidence/WP-PROD-CHAR-01/build_inventory.json'
    if args.output:report=output/'build_inventory.json'
    inputs=[Path(args.recipes) if args.recipes else ROOT/'Docs/asset_catalog/char_recipes.json',
        ROOT/'Docs/asset_catalog/char_body_profiles.json',ROOT/'Docs/asset_catalog/char_compatibility.json',
        ROOT/'Tools/char_build.py',ROOT/'Tools/char_shapes.py',ROOT/'Tools/char_manifest.py',ROOT/'Tools/char_naturalism.py',
        ROOT/'Docs/asset_catalog/char_naturalism_forms.json',ROOT/'Tools/vendor/chilyer/body_topo.py',ROOT/'Tools/char_human.py',
        ROOT/'Tools/char_human_sources.py',ROOT/'Tools/char_human_textures.py',ROOT/'Docs/evidence/WP-PROD-ASSET-00/catalog.json']
    human_root=ROOT/'Art/Characters/HumanHeads'
    if human_root.exists():inputs.extend(sorted(p for p in human_root.rglob('*') if p.is_file()))
    inputs.append(ROOT/'Art/Characters/HumanSources/admission.json')
    identities=[{'path':str(p.resolve().relative_to(ROOT)).replace('\\','/') if p.resolve().is_relative_to(ROOT) else str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]
    report.write_bytes((json.dumps({'schemaVersion':2,'inputs':identities,'variants':reports},indent=2)+'\n').encode())
    print('CHAR_BUILD_COMPLETE',len(reports))

if __name__=='__main__':main()
