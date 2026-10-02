"""Bounded structural variants of the existing Quaternius rig, not a new rig.

The same anatomical warp is applied to every mesh and rest bone. Face shaping
uses the existing head topology; it does not add face textures or bones.
"""
import math
import bpy
from mathutils import Vector, Matrix

def lerp(a,b,t):return a+(b-a)*max(0,min(1,t))

def facial_form(p, profile, ratio):
    """Continuous head sculpt shared by skin, eyes, hair and attachments, in source metres.

    Features blend smoothly into the neck. The old hard z>1.58 width switch
    could create a ring at the jaw. The cranium, jaw, sockets and mouth now
    have separate controls; skull height remains owned by solve_head.
    """
    x,y,z=p/ratio
    gate=max(0,min(1,(z-1.565)/.055));gate=gate*gate*(3-2*gate)
    if not gate:return p
    gauss=lambda a,c,w:math.exp(-((a-c)/w)**2)
    jaw=gauss(z,1.627,.047);cheek=gauss(z,1.687,.030)
    cranium=max(0,min(1,(z-1.718)/.066))
    side=1+(profile.get('faceWidth',1)-1)*gate
    side*=1+(profile['jaw']-1)*jaw+(profile['cheeks']-1)*cheek
    side*=1+(profile.get('craniumWidth',1)-1)*cranium
    p.x*=side
    front=max(0,min(1,(y+.005)/.06))
    # Move eye centres AND socket geometry together. Keep the external skull
    # and ears out of this local map; glasses follow the same ocular region.
    eye=gauss(z,1.704,.021)*gauss(abs(x),.051,.032)*front
    p.x+=math.copysign((profile.get('eyeSpacing',1)-1)*.052*ratio*eye,x)
    p.z+=profile.get('eyeHeight',0)*ratio*eye
    p.z+=profile.get('eyeTilt',0)*ratio*eye*x/.060
    nose=gauss(z,1.676,.038)*gauss(x,0,.027)*front
    p.y+=(profile['nose']-1)*.10*ratio*nose
    p.x*=1+(profile.get('noseWidth',1)-1)*nose
    p.y+=profile.get('bridge',0)*ratio*gauss(z,1.705,.027)*gauss(x,0,.023)*front
    mouth=gauss(z,1.634,.021)*gauss(x,0,.056)*front
    p.x*=1+(profile.get('mouthWidth',1)-1)*mouth
    p.z+=profile.get('mouthHeight',0)*ratio*mouth
    chin=gauss(z,1.604,.023)*gauss(x,0,.049)*front
    p.y+=profile.get('chin',0)*.010*ratio*chin
    p.z-=profile.get('chin',0)*.008*ratio*chin
    p.y+=profile.get('forehead',0)*ratio*gauss(z,1.750,.041)*front
    p.z+=profile['brow']*gauss(z,1.721,.015)*front
    # Small age-related loss of cheek support, jaw softness and intrinsic
    # asymmetry. These are geometry changes, independent of grey hair.
    sag=profile.get('ageSag',0)*ratio
    p.z-=sag*cheek*front*gauss(abs(x),.063,.045)
    p.y+=sag*.55*jaw*front
    asym=profile.get('faceAsymmetry',0)*ratio
    p.y+=asym*gauss(z,1.686,.075)*x/.095*front
    return p

HAND_CHAIN=('hand_','thumb_','index_','middle_','ring_','pinky_')

def hand_side(name):
    """'l'/'r' when a bone/vertex group belongs to a hand (wrist, palm or finger), else None."""
    if name.startswith(HAND_CHAIN) and name[-2:] in ('_l','_r'):return name[-1]
    return None

def solve_head(profile,body,anthropometry,native_height,ratio):
    """Head factor that gives the person an absolute head height (crown to eye line x2).

    The Quaternius sources carry small heads (8.0-8.6 heads tall, measured); a constant ratio also made tall men
    pin-headed. Real head size varies far less than stature, so the target is absolute with a mild height term."""
    tweak=profile.get('head',1.0)
    spec=(anthropometry or {}).get('headHeight',{}).get((body or {}).get('id',''))
    if not spec:return tweak
    target=profile.get('headHeight') or spec['base']*(profile['height']/spec['refHeight'])**spec['exponent']
    native=anthropometry['native'][body['id']]['headHeight']
    pelvis=.95*ratio;neck=1.54*ratio
    fixed=pelvis*profile['legs']+(neck-pelvis)          # zmap(native) = fixed + (native_height-neck)*head
    head=target*fixed/(native*profile['height']-target*(native_height-neck))
    return head*tweak

def shape_character(arm,meshes,profile,native_height,body=None,anthropometry=None):
    ratio=native_height/1.81008
    pelvis=.95*ratio;neck=1.54*ratio
    profile=dict(profile);profile['head']=solve_head(profile,body,anthropometry,native_height,ratio)
    # Source-family hand correction (male Quaternius hands are about one head long; human ~0.8) times a profile tweak.
    hand_scale=(body or {}).get('handScale',1.0)*profile.get('hand',1.0)
    # Limb mass without skeletal change: arm girth scales the arm radially about the shoulder-wrist line.
    arm_girth=profile.get('armGirth',1.0)
    leg_end=pelvis*profile['legs']
    def zmap(z):
        if z<=pelvis:return z*profile['legs']
        if z<=neck:return leg_end+(z-pelvis)
        return leg_end+neck-pelvis+(z-neck)*profile['head']
    scale=profile['height']/zmap(native_height)
    def warp(v):
        x,y,z=v;az=z/ratio
        if az<.70:sx=profile['hips']*.4+.6
        elif az<.98:sx=lerp(profile['hips']*.4+.6,profile['hips'],(az-.70)/.28)
        elif az<1.15:sx=lerp(profile['hips'],profile['torso'],(az-.98)/.17)
        elif az<1.46:sx=lerp(profile['torso'],profile['shoulders'],(az-1.15)/.31)
        else:sx=lerp(profile['shoulders'],profile['head'],(az-1.46)/.12)
        if 1.25<az<1.55 and abs(x)>.24*ratio:
            x=math.copysign(.24*ratio*sx+(abs(x)-.24*ratio)*profile['armLength'],x)
        else:x*=sx
        depth=profile['depth'] if .83<az<1.5 else profile['head'] if az>1.58 else 1+(profile['hips']-1)*.4
        y*=depth
        # Optional posture: a gentle forward curve of the upper spine. Applied to meshes AND
        # rest bones so the Humanoid avatar is authored from the same (mildly curved) rest pose.
        stoop=profile.get('stoop',0)
        if stoop and az>1.0:
            t=min(1,(az-1.0)/.62);y+=stoop*ratio*t*t
        return Vector((x*scale,y*scale,zmap(z)*scale))
    bpy.context.view_layer.update()
    # First place all geometry/rest bones in the common source world frame.
    for o in meshes:
        o.data.transform(o.matrix_world.copy());o.matrix_world=Matrix.Identity(4)
    arm.data.transform(arm.matrix_world.copy());arm.matrix_world=Matrix.Identity(4)
    wrist={s:arm.data.bones['hand_'+s].head_local.copy() for s in ('l','r')}
    shoulder={s:arm.data.bones['upperarm_'+s].head_local.copy() for s in ('l','r')}
    for o in meshes:
        sides={g.index:hand_side(g.name) for g in o.vertex_groups}
        arms={g.index:g.name[-1] for g in o.vertex_groups if g.name[:-2] in ('upperarm','lowerarm') and g.name[-2:] in ('_l','_r')}
        for vertex in o.data.vertices:
            p=vertex.co.copy();z=p.z/ratio
            if hand_scale!=1:
                for g in vertex.groups:
                    side=sides.get(g.group)
                    if side and g.weight>0:p+=(vertex.co-wrist[side])*(hand_scale-1)*g.weight
            if arm_girth!=1:
                for g in vertex.groups:
                    side=arms.get(g.group)
                    if side and g.weight>0:
                        a=shoulder[side];d=(wrist[side]-a).normalized();rel=vertex.co-a
                        p+=(rel-d*rel.dot(d))*(arm_girth-1)*g.weight
            # Body-mass detail that is not skeletal: abdomen volume and neck thickness.
            belly=profile.get('belly',0)
            if belly and .86<z<1.36:
                front=max(0,min(1,(p.y+.02*ratio)/(.10*ratio)))
                lateral=max(0,1-(abs(p.x)/(.30*ratio))**2)
                p.y+=belly*ratio*.16*math.exp(-((z-1.06)/.13)**2)*front*lateral
                p.x*=1+belly*.18*math.exp(-((z-1.06)/.16)**2)
            neck_scale=profile.get('neckScale',1)
            if neck_scale!=1 and 1.50<z<1.62:
                k=1+(neck_scale-1)*math.exp(-((z-1.55)/.045)**2)
                if abs(p.x)<.16*ratio:p.x*=k;p.y=(p.y+.017*ratio)*k-.017*ratio
            p=facial_form(p,profile,ratio)
            vertex.co=warp(p)
        o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);o.data.update()
    bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);bpy.context.view_layer.objects.active=arm
    bpy.ops.object.mode_set(mode='EDIT')
    original={b.name:(b.head.copy(),b.tail.copy(),b.roll) for b in arm.data.edit_bones}
    for bone in arm.data.edit_bones:
        head,tail,roll=original[bone.name];side=hand_side(bone.name)
        if side and hand_scale!=1:
            w=wrist[side];tail=w+(tail-w)*hand_scale
            if not bone.name.startswith('hand_'):head=w+(head-w)*hand_scale
        bone.head=warp(head);bone.tail=warp(tail);bone.roll=roll
    bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()
    skin=[o for o in meshes if o.name.startswith('VisibleSkin')]
    head_z=arm.data.bones['Head'].head_local.z
    crown=max((v.co.z for o in skin for v in o.data.vertices if v.co.z>head_z),default=profile['height'])
    stature=crown
    eyes=[v.co.z for o in meshes if o.name.split('.')[0]=='Eyes' for v in o.data.vertices]
    head_height=2*(crown-(max(eyes)+min(eyes))/2) if eyes else float('nan')
    wrist_l=arm.data.bones['hand_l'].head_local
    groups={}
    for o in skin:
        for g in o.vertex_groups:groups[(o.name,g.index)]=g.name
    hand_len=max(((o.matrix_world@v.co)-wrist_l).length for o in skin for v in o.data.vertices
        if sum(g.weight for g in v.groups if hand_side(groups[(o.name,g.group)])=='l')>.5)
    metrics={'crown':float(crown),'headHeight':float(head_height),'headsTall':float(stature/head_height),
        'handLength':float(hand_len),'handOverHead':float(hand_len/head_height),'headFactor':float(profile['head']),
        'shoulderJointRatio':float(abs(arm.data.bones['upperarm_l'].head_local.x-arm.data.bones['upperarm_r'].head_local.x)/stature),
        'hipJointRatio':float(abs(arm.data.bones['thigh_l'].head_local.x-arm.data.bones['thigh_r'].head_local.x)/stature),
        'headLength':float((crown-head_z)/stature),
        'pelvisHeight':float(arm.data.bones['pelvis'].head_local.z/stature)}
    return {**metrics,'family':profile['id'],'height':profile['height'],'shoulderSpan':float((arm.data.bones['upperarm_l'].head_local-arm.data.bones['upperarm_r'].head_local).length),
            'legLength':float((arm.data.bones['thigh_l'].head_local-arm.data.bones['foot_l'].head_local).length),
            'hipSpan':float((arm.data.bones['thigh_l'].head_local-arm.data.bones['thigh_r'].head_local).length)}

