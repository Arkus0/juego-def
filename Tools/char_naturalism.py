"""Authored civilian forms on the admitted skeleton, shared by every CHAR build.

The source rig/UVs are retained. Eyebrows, everyday hair and facial hair are
owned meshes, and the facial/garment construction is selected explicitly by
recipe. No exported-FBX retouches or random appearance generation.
"""
import math
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def _tree(o):
    return BVHTree.FromPolygons([v.co for v in o.data.vertices], [list(f.vertices) for f in o.data.polygons])


def _surface_copy(body, name, keep, push, material, bind, arm):
    o = body.copy(); o.data = body.data.copy(); o.name = name
    bpy.context.scene.collection.objects.link(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not keep(f.calc_center_median())], context='FACES')
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * push
    bm.to_mesh(o.data); bm.free(); o.data.materials.clear(); o.data.materials.append(material)
    for f in o.data.polygons: f.material_index = 0; f.use_smooth = True
    bind(o, arm, 'Head')
    return o


def sculpt_head(body, meshes, form, ratio):
    """Reshape the ocular aperture with the eyeballs, soften lip relief and
    author cheek/brow/nasal support. Actual eye centres are measured from
    each admitted family rather than inferred from one male template.
    """
    eyes = next(o for o in meshes if o.name.startswith('Eyes'))
    centres = {}
    for sign in (-1, 1):
        vs = [v.co for v in eyes.data.vertices if v.co.x * sign > 0]
        centres[sign] = sum(vs, Vector()) / len(vs)
    ocular = form['eyeAperture']; width = form['eyeWidth']
    expression=form['expression']
    smile=expression['smile']; happy=max(0,smile)
    mouth_z=1.624 if form['sex']=='female' else 1.630
    for o in (body, eyes):
        for v in o.data.vertices:
            p = v.co; sign = 1 if p.x >= 0 else -1; c = centres[sign]
            dx, dz = (p.x-c.x)/ratio, (p.z-c.z)/ratio
            if o == eyes:
                w = 1.0
            else:
                d = math.hypot(dx/.036, dz/.029)
                w = min(1.0, max(0.0, (1.7-d)/.7)) * min(1.0, max(0.0, (p.y/ratio-.015)/.035))
            p.x += (p.x-c.x)*(width-1)*w
            p.z += (p.z-c.z)*(ocular-1)*w
            # A smile raises the lower lid with the cheek. Move the skin and
            # the eye's lower surround together, leaving the iris centre put.
            lid=math.exp(-(dx/.028)**4-((dz+.012)/.010)**2)
            p.z += happy*.0022*ratio*lid*w
            if o != body or p.z < 1.58*ratio: continue
            x,y,z = p/ratio
            front = min(1.0, max(0.0, (y-.015)/.045))
            lip = math.exp(-((z-mouth_z)/.018)**2-((x)/.046)**4)*front
            p.y -= (1-form['lipRelief'])*.011*ratio*lip
            mouth=math.exp(-((z-mouth_z)/.023)**2-(x/.049)**6)*front
            corners=math.exp(-((abs(x)-.027)/.018)**2)*mouth
            p.z += (form['mouthCorner']+smile*.011)*ratio*corners
            p.x += x*.16*happy*ratio*mouth
            # Thin the source's pouting upper lip/philtrum rather than
            # retaining a protruding dark ridge that reads as a moustache.
            if form['sex']=='female':
                upper=math.exp(-((z-(mouth_z+.007))/.008)**2-(x/.038)**4)*front
                p.y-=.0035*ratio*upper
            cheek=math.exp(-((abs(x)-.049)/.026)**2-((z-1.663)/.028)**2)*front
            p.z+=happy*.0035*ratio*cheek
            p.y+=happy*.002*ratio*cheek
            # Mild frown is carried by inner brow compression and the mouth,
            # while relaxed/happy eyes retain an unforced upper aperture.
            brow=math.exp(-((abs(x)-.024)/.023)**2-((z-c.z/ratio-.026)/.022)**2)*front
            p.z+=expression['browInner']*ratio*brow
            p.y += form['cheekSupport']*ratio*math.exp(-((abs(x)-.059)/.026)**2-((z-1.679)/.035)**2)*front
            p.y += form['bridgeSupport']*ratio*math.exp(-(x/.018)**2-((z-1.700)/.031)**2)*front
            p.z -= form['lowerLid']*ratio*math.exp(-((abs(x)-abs(c.x/ratio))/.026)**2-((z-c.z/ratio+.013)/.014)**2)*front
    body.data.update(); eyes.data.update()
    return centres


def brows(body, arm, centres, form, ratio, mat, fitted_grid):
    """Thin tapered brow ribbons with authored slope; no source eyelash/brow shell."""
    tree = _tree(body)
    for sign in (-1, 1):
        c = centres[sign]; verts=[]; faces=[]; n=12
        for i in range(n):
            t=i/(n-1); x=sign*(abs(c.x)+(-.020+.047*t)*ratio)
            expression=form['expression']
            lift=expression['browInner']*(1-t)+expression['browOuter']*t
            lift+=expression['asymmetry']*(1 if sign>0 else -1)
            z=c.z+(.024+.0035*math.sin(math.pi*t)+form['browSlope']*(t-.5)+lift)*ratio
            thick=form['browThickness']*ratio*(.35+.65*math.sin(math.pi*t)**.5)
            for offset in (-thick/2, thick/2):
                hit=tree.ray_cast(Vector((x,1.0,z+offset)),Vector((0,-1,0)))[0]
                y=(hit.y if hit is not None else c.y+.015*ratio)+.002*ratio
                verts.append((x,y,z+offset))
        for i in range(n-1): faces.append((i*2,i*2+2,i*2+3,i*2+1))
        o=fitted_grid(body,arm,'Eyebrows_Natural_'+str(sign),verts,faces,mat)
        # Head attachment is exact and does not introduce another skeleton.
        o.vertex_groups.clear();g=o.vertex_groups.new(name='Head');g.add(list(range(len(o.data.vertices))),1,'REPLACE')


def _tube(name, points, radii, mat, arm, bind, sides=8):
    points=[Vector(p) for p in points];verts=[];faces=[]
    for i,p in enumerate(points):
        axis=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
        u=axis.cross(Vector((0,1,0)))
        if u.length < .1: u=axis.cross(Vector((1,0,0)))
        u.normalize();v=axis.cross(u).normalized()
        for j in range(sides):
            angle=2*math.pi*j/sides
            verts.append(tuple(p+(u*math.cos(angle)+v*math.sin(angle))*radii[i]))
    for i in range(len(points)-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides;faces.append((a,b,b+sides,a+sides))
    faces += [tuple(reversed(range(sides))),tuple((len(points)-1)*sides+j for j in range(sides))]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);mesh.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    bind(o,arm,'Head');return o


def hair(body, arm, ratio, style, form, mat, bind, fitted_grid, ellipsoid, covered=False):
    """Everyday scalp/part/bob/tied-hair forms, all owned and reproducible.
    Source pack hairstyles are deliberately not loaded on this route.
    """
    receding = style == 'receding'
    tree=_tree(body);verts=[];faces=[];segments=64;rows=14
    crown=max(v.co.z for v in body.data.vertices)/ratio
    if covered:crown=min(crown,1.700)
    for row in range(rows):
        t=row/rows
        for i in range(segments):
            a=2*math.pi*i/segments;front=max(0,math.cos(a))
            exponent=.65 if style in ('low_bun','pony') else 1.15 if style=='sidepart' else 1.7
            line=1.665+.083*front**exponent
            # A swept everyday hairline, with temples and a mild off-centre part.
            line+=.004*math.sin(a*2)+.002*math.sin(a*5)
            if style in ('sidepart','bob','wavy_bob'):line+=.010*math.sin(a)*front
            if receding:line+=.039*front**2+.017*math.sin(a)**2*front
            if covered:line=min(line,crown-.005)
            z=(line+(crown-line)*math.sin(t*math.pi/2))*ratio
            d=Vector((math.sin(a),math.cos(a),0))
            hit=tree.ray_cast(Vector((0,-.020*ratio,z)),d,.3*ratio)[0]
            if hit is None:
                radius=.089*math.sqrt(max(.001,1-((z/ratio-1.710)/.106)**2))*ratio
                hit=Vector((d.x*radius,-.020*ratio+d.y*radius,z))
            # Broad combed clumps, millimetres deep, break a uniform helmet.
            flow=a*16 + t*(2.0 if style=='sidepart' else .7)
            relief=(.0011*math.cos(flow)+.0005*math.cos(a*7))*math.sin(math.pi*t)**.7
            margin=(.004+(.003 if style in ('bob','wavy_bob') else .001)*math.sin(math.pi*t)+relief)*ratio
            if style=='short_waves':margin+=(.006+.004*math.sin(a*8+t*9)*math.sin(math.pi*t))*ratio
            verts.append(tuple(hit+d*margin))
    verts.append((0,-.020*ratio,(crown+.003)*ratio))
    for row in range(rows-1):
        for i in range(segments):
            k=row*segments+i;l=row*segments+(i+1)%segments
            faces.append((k,l,l+segments,k+segments))
    for i in range(segments):faces.append(((rows-1)*segments+i,(rows-1)*segments+(i+1)%segments,len(verts)-1))
    scalp=fitted_grid(body,arm,'Hair_Scalp',verts,faces,mat);bind(scalp,arm,'Head')
    _hair_uv(scalp,ratio)
    if style in ('bob','wavy_bob'):
        verts=[];faces=[];segments=40;rows=9
        for j in range(rows):
            t=j/(rows-1)
            for i in range(segments):
                a=2*math.pi*i/segments;front=max(0,math.cos(a))
                bottom=1.595+.175*front**1.6+.008*math.sin(a)*front+.008*math.sin(a)**2
                z=1.790*(1-t)+bottom*t
                crown=math.sqrt(max(.15,1-((z-1.706)/.113)**2))
                rx=.090*crown+.012*t
                ry=.092*crown+.008*t
                ripple=(.002*math.sin(a*7+t*2) if style=='wavy_bob' else .001*math.cos(a*12))
                verts.append(((rx+ripple)*math.sin(a)*ratio,(-.020+(ry+ripple)*math.cos(a))*ratio,z*ratio))
        for j in range(rows-1):
            for i in range(segments):
                a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
        o=fitted_grid(body,arm,'Hair_Bob',verts,faces,mat);bind(o,arm,'Head')
        _hair_uv(o,ratio)
    elif style in ('low_bun','pony'):
        centre=(0,-.110*ratio,1.691*ratio)
        ellipsoid('Hair_Tie',centre,(.024*ratio,.022*ratio,.026*ratio),mat,arm,'Head',segments=20,rings=10)
        if style=='low_bun':
            ellipsoid('Hair_LowBun',(0,-.138*ratio,1.690*ratio),(.035*ratio,.030*ratio,.035*ratio),mat,arm,'Head',segments=24,rings=12)
        else:
            _tube('Hair_Pony',[(0,-.13*ratio,1.69*ratio),(.007*ratio,-.15*ratio,1.65*ratio),(.012*ratio,-.155*ratio,1.60*ratio),(.008*ratio,-.14*ratio,1.56*ratio)],
                [.022*ratio,.021*ratio,.017*ratio,.010*ratio],mat,arm,bind,sides=12)
    return scalp


def _hair_uv(o,ratio):
    uv=o.data.uv_layers.new(name='HairFlow')
    for f in o.data.polygons:
        first=None
        for li in f.loop_indices:
            p=o.data.vertices[o.data.loops[li].vertex_index].co/ratio
            u=math.atan2(p.x,p.y+.020)/(2*math.pi)
            if first is None:first=u
            while u-first>.5:u-=1
            while u-first<-.5:u+=1
            uv.data[li].uv=(u,(p.z-1.58)/.24)


def facial_hair(body, arm, ratio, kinds, mat, bind, fitted_grid):
    tree=_tree(body)
    for kind in kinds:
        if kind=='moustache':
            verts=[];faces=[];cols=32;rows=4
            for row in range(rows):
                t=row/(rows-1)
                for i in range(cols+1):
                    u=2*i/cols-1;x=u*.039*ratio
                    low=1.647-.003*abs(u);height=.012*max(0,1-u*u)**.5
                    z=(low+height*t)*ratio
                    hit=tree.ray_cast(Vector((x,1,z)),Vector((0,-1,0)))[0]
                    if hit is None:raise ValueError('Moustache has no face backing')
                    verts.append((x,hit.y+.0025*ratio,z))
            for row in range(rows-1):
                for i in range(cols):
                    k=row*(cols+1)+i;faces.append((k,k+1,k+cols+2,k+cols+1))
            o=fitted_grid(body,arm,'Facial_moustache',verts,faces,mat);bind(o,arm,'Head')
            continue
        if kind=='beard':
            verts=[];faces=[];cols=40;rows=8
            for row in range(rows):
                t=row/(rows-1)
                for i in range(cols+1):
                    a=-1.40+2.80*i/cols;s=abs(math.sin(a))
                    top=1.622+.067*s**3;bottom=1.589+.052*s**2
                    z=(bottom+(top-bottom)*t)*ratio
                    d=Vector((math.sin(a),math.cos(a),0))
                    hit=tree.ray_cast(Vector((0,-.020*ratio,z)),d,.3*ratio)[0]
                    if hit is None:hit=tree.find_nearest(Vector((d.x*.05*ratio,d.y*.05*ratio,z)))[0]
                    verts.append(tuple(hit+d*(.002+.002*math.sin(math.pi*t))*ratio))
            for row in range(rows-1):
                for i in range(cols):
                    k=row*(cols+1)+i;faces.append((k,k+1,k+cols+2,k+cols+1))
            o=fitted_grid(body,arm,'Facial_beard',verts,faces,mat);bind(o,arm,'Head')
            continue
        def keep(p):
            x,y,z=p/ratio
            if kind=='moustache':
                lo=1.649-.005*abs(x)/.042
                return abs(x)<.043 and lo<z<1.665 and y>.055
            if kind=='beard':
                mouth=abs(x)<.037 and 1.622<z<1.648
                return 1.588<z<1.666 and y>.014 and not mouth
            return .061<abs(x)<.089 and 1.618<z<1.714 and -.012<y<.063
        _surface_copy(body,'Facial_'+kind,keep,.002*ratio,mat,bind,arm)


def tailor(meshes, ratio, pattern, recipe, fitted_grid, arm, trim):
    """Hanging chest panels, distinct cuts, broad folds and functional facings.
    The admitted weight-transfer path stays shared; muscle-shaped relief does
    not define the final garment surface.
    """
    cloth=[o for o in meshes if o.name.startswith(('Top_','Outer_','Inner_','Straight_','Shop_coat'))]
    for o in cloth:
        # Cloth over the bust hangs between seam lines; it does not reproduce skin.
        if not o.name.startswith('Straight_'):
            for v in o.data.vertices:
                x,y,z=v.co/ratio
                if abs(x)<.23 and 1.10<z<1.44:
                    same=[w.co.y for w in o.data.vertices if abs(w.co.x)<.030*ratio and abs(w.co.z-v.co.z)<.023*ratio and w.co.y>0]
                    if same and y>0:
                        plane=sum(same)/len(same)+.007*ratio
                        v.co.y=plane+(v.co.y-plane)*.40
                # A few centimetre-wide compression folds at waist and elbow,
                # not high-frequency normal noise across the whole person.
                fold=math.exp(-((z-1.055)/.075)**2)*math.sin(x*25+z*27)
                if abs(x)<.24 and y>0:v.co.y+=pattern['foldDepth']*ratio*fold
            o.data.update()
    outer=next((o for o in cloth if o.name.startswith('Outer_')),None)
    if outer is None:return
    tree=_tree(outer)
    def panel(name, points):
        verts=[]
        for x,z in points:
            hit=tree.ray_cast(Vector((x*ratio,1.0,z*ratio)),Vector((0,-1,0)))[0]
            if hit is None:return
            verts.append((x*ratio,hit.y+.005*ratio,z*ratio))
        fitted_grid(outer,arm,name,verts,[tuple(range(len(verts)))],trim)
    if pattern['collar'] in ('denim','lapel'):
        for sign in (-1,1):
            if pattern['collar']=='denim':
                points=[(sign*.100,1.550),(sign*.147,1.490),(sign*.117,1.452),(sign*.097,1.512)]
            else:
                points=[(sign*.101,1.550),(sign*.151,1.482),(sign*.117,1.412),(sign*.098,1.494)]
            panel('Pattern_collar_'+str(sign),points)
    # Patch/welt proportions come from the garment pattern, never from a
    # floating cube accessory. Each panel follows the actual garment surface.
    if pattern['pockets']=='chest':
        for sign in (-1,1):
            panel('Pattern_pocket_'+str(sign),[(sign*.092,1.354),(sign*.170,1.354),(sign*.170,1.265),(sign*.092,1.265)])


def line_open_layer(outer, inner, ratio, material):
    """Cut a lined opening from one finished surface and its skin weights.

    Independently smoothed inner/outer meshes crossed at the opening while
    bending. A thin inset copy stays parallel and leaves a 13 mm sewn overlap.
    """
    if [g.name for g in inner.vertex_groups]!=[g.name for g in outer.vertex_groups]:
        raise ValueError('Lined garments must share the source group map')
    inner.data=outer.data.copy()
    inner.data.materials.clear();inner.data.materials.append(material)
    bm=bmesh.new();bm.from_mesh(inner.data);bm.normal_update()
    for v in bm.verts:v.co-=v.normal*.012*ratio
    for x in (-.108,.108):
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
            plane_co=(x*ratio,0,0),plane_no=(1,0,0))
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
        plane_co=(0,0,.99*ratio),plane_no=(0,0,1))
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not(f.calc_center_median().y>0 and abs(f.calc_center_median().x)<.108*ratio and f.calc_center_median().z>=.99*ratio)],context='FACES')
    bm.to_mesh(inner.data);bm.free();inner.data.update()
    for f in inner.data.polygons:f.material_index=0
    bm=bmesh.new();bm.from_mesh(outer.data)
    for x in (-.095,.095):
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
            plane_co=(x*ratio,0,0),plane_no=(1,0,0))
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().y>.005*ratio and abs(f.calc_center_median().x)<.095*ratio],context='FACES')
    bm.to_mesh(outer.data);bm.free();outer.data.update()


def mask_covered_waist(lower, ratio, top_hem):
    """Keep a sewn 20 mm overlap, remove trouser waist hidden inside tops."""
    z=(top_hem+.020)*ratio
    bm=bmesh.new();bm.from_mesh(lower.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
        plane_co=(0,0,z),plane_no=(0,0,1))
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z>z],context='FACES')
    bm.to_mesh(lower.data);bm.free();lower.data.update()


def finish_necklines(body, meshes, ratio, surface_weights):
    """Sew high neckline boundaries to one measured continuous neck surface.

    Flat-plane snapping made square tubes and exposed triangular gaps. These
    loops follow the neck; the authored outer opening keeps its lower V.
    """
    tree=_tree(body)
    for o in meshes:
        if not o.name.startswith(('Top_','Outer_','Inner_','Waistcoat_','Work_vest_')):continue
        if o.name.startswith(('Waistcoat_panel_','Work_vest_panel_')):continue
        bm=bmesh.new();bm.from_mesh(o.data)
        changed=[]
        for v in bm.verts:
            if v.co.z<1.490*ratio or abs(v.co.x)>.145*ratio:continue
            if not v.is_boundary and v.co.z<1.520*ratio:continue
            a=math.atan2(v.co.x,v.co.y+.020*ratio)
            front=max(0,math.cos(a));z=(1.567-.014*front)*ratio
            d=Vector((math.sin(a),math.cos(a),0))
            hit=tree.ray_cast(Vector((0,-.020*ratio,z)),d,.4*ratio)[0]
            if hit is None:continue
            clearance=.018 if o.name.startswith('Outer_') else .009
            t=1 if v.is_boundary else min(.75,max(0,(v.co.z/ratio-1.490)/.077))
            target=hit+d*clearance*ratio
            v.co=v.co.lerp(target,t)
            changed.append(v.index)
        bm.to_mesh(o.data);bm.free();o.data.update()
        surface_weights(body,o,[o.data.vertices[i] for i in changed])


def torso_weights(o,arm):
    """Free apron ties follow the torso, not the nearest arm."""
    allowed={'pelvis','spine_01','spine_02','spine_03','clavicle_l','clavicle_r','neck_01'}
    for v in o.data.vertices:
        weights={g.group:g.weight for g in v.groups if o.vertex_groups[g.group].name in allowed}
        total=sum(weights.values())
        for g in list(v.groups):o.vertex_groups[g.group].remove([v.index])
        if total:
            for key,value in weights.items():o.vertex_groups[key].add([v.index],value/total,'REPLACE')
        else:
            name='spine_03';g=o.vertex_groups.get(name) or o.vertex_groups.new(name=name);g.add([v.index],1,'REPLACE')


def waistcoat(body, shirt, arm, ratio, mat, fitted_grid, work=False, clearance=.013):
    """Cut a connected outer panel on the shirt's exact surface and weights.

    Separate ray-projected front/back grids diverged from the shirt under arm
    motion. Plane cuts interpolate the supporting cloth's existing weights,
    preserve side seams and put the V/armholes on explicit construction lines.
    """
    o=shirt.copy();o.data=shirt.data.copy();o.name='Work_vest_panel_sewn' if work else 'Waistcoat_panel_sewn'
    bpy.context.scene.collection.objects.link(o)
    bm=bmesh.new();bm.from_mesh(o.data)
    cuts=[((0,0,.97*ratio),(0,0,1))]
    vbase=1.455 if work else 1.31
    vslope=.35 if work else .40
    for sign in (-1,1):
        cuts.append(((sign*.235*ratio,0,1.30*ratio),(sign,0,.32)))
        cuts.append(((0,0,vbase*ratio),(sign,0,-vslope)))
    for point,normal in cuts:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=point,plane_no=normal)
    def keep(f):
        x,y,z=f.calc_center_median()/ratio
        return z>=.97 and abs(x)<=.235-.32*(z-1.30) and not(y>0 and z>vbase and abs(x)<vslope*(z-vbase))
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not keep(f)],context='FACES')
    bm.normal_update()
    for v in bm.verts:v.co+=v.normal*clearance*ratio
    bm.to_mesh(o.data);bm.free();o.data.update()
    o.data.materials.clear();o.data.materials.append(mat)
    for f in o.data.polygons:f.material_index=0;f.use_smooth=True
    return o


def mask_under_vest(shirt, ratio, work=False):
    """Remove invisible inner cloth, retaining a sewn overlap at the V,
    armholes and hem. This prevents sleeves/torso layers punching through a
    vest during retargeted motion without hiding any exposed skin defect."""
    bm=bmesh.new();bm.from_mesh(shirt.data)
    vbase=1.455 if work else 1.31;vslope=.35 if work else .40
    cuts=[((0,0,1.005*ratio),(0,0,1))]
    for sign in (-1,1):
        cuts.append(((sign*.220*ratio,0,1.30*ratio),(sign,0,.32)))
        cuts.append(((sign*.014*ratio,0,vbase*ratio),(sign,0,-vslope)))
    for point,normal in cuts:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=point,plane_no=normal)
    def keep(f):
        x,y,z=f.calc_center_median()/ratio
        return z<1.005 or abs(x)>.220-.32*(z-1.30) or (y>0 and z>vbase-.04 and abs(x)<vslope*(z-vbase)+.014)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not keep(f)],context='FACES')
    bm.to_mesh(shirt.data);bm.free();shirt.data.update()


def shoulder_ribbon(surface, ratio, centre, width, mat, name, bottom=1.12):
    """A sewn ribbon following the supporting garment, including its shoulder.

    Copy/cut the actual cloth rather than projecting unrelated path vertices
    across front/back/arm surfaces. BMesh interpolates seam weights, so both
    layers deform together. The lower end is covered by the backpack body.
    """
    o=surface.copy();o.data=surface.data.copy();o.name=name
    bpy.context.scene.collection.objects.link(o)
    bm=bmesh.new();bm.from_mesh(o.data)
    lo=(centre-width/2)*ratio;hi=(centre+width/2)*ratio;bottom=bottom*ratio
    for point,normal in [((lo,0,0),(1,0,0)),((hi,0,0),(1,0,0)),((0,0,bottom),(0,0,1))]:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=point,plane_no=normal)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not(lo<=f.calc_center_median().x<=hi and f.calc_center_median().z>=bottom)],context='FACES')
    bm.normal_update()
    for v in bm.verts:v.co+=v.normal*.011*ratio
    bm.to_mesh(o.data);bm.free();o.data.update()
    o.data.materials.clear();o.data.materials.append(mat)
    for f in o.data.polygons:f.material_index=0;f.use_smooth=True
    return o
