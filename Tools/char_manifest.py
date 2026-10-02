"""Small recipe admission layer shared by Blender and command-line checks."""
import json
import re
import math
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def admitted_head(recipe,manifest=None):
    """Validate one reusable head bundle and its admitted raw CC0 inputs."""
    doc=manifest if manifest is not None else json.loads((ROOT/'Art/Characters/HumanHeads/source_manifest.json').read_text())
    if doc.get('assetLicense')!='CC0-1.0' or doc.get('mpfbCommit')!='afb9f530a7c2741dedb8df0ebae2e0b183caec21':
        raise ValueError('Unadmitted anatomical tool/asset provenance')
    entry=next((h for h in doc['heads'] if h['id']==recipe['headForm']),None)
    if entry is None:raise ValueError('Unadmitted anatomical head form '+recipe['headForm'])
    sex='female' if recipe['body'].endswith('female') else 'male'
    if entry['sex']!=sex:raise ValueError('Anatomical head/body sex mismatch')
    if entry.get('hairStyle')!=recipe.get('hairStyle'):raise ValueError('Hair style requires a matching admitted head/hair bundle')
    if sex=='female' and recipe.get('facial'):raise ValueError('Female facial hair rejected')
    source=(ROOT/entry['path']).resolve()
    if not source.is_relative_to(ROOT/'Art/Characters/HumanHeads') or source.suffix!='.blend':raise ValueError('Unsafe anatomical head source')
    if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Changed anatomical head bundle')
    for raw in entry['sourceFiles']:
        path=ROOT/'Art/Characters/HumanSources/system'/raw['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=raw['sha256']:raise ValueError('Changed CC0 anatomical source '+raw['path'])
    for raw in entry.get('blinkSources',[]):
        path=ROOT/'Art/Characters/HumanSources/mpfb_targets'/Path(raw['path']).relative_to('src/mpfb/data/targets')
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=raw['sha256']:raise ValueError('Changed CC0 eyelid target')
    return entry

def human_source_ids(recipe):
    entry=admitted_head(recipe)
    ids=['makehuman:hm08.obj']+['makehuman:system/'+r['path'] for r in entry['sourceFiles']]
    ids+=['makehuman:mpfb_targets/'+Path(r['path']).relative_to('src/mpfb/data/targets').as_posix() for r in entry.get('blinkSources',[])]
    eye=recipe.get('eyes') or 'brown'
    material=ROOT/'Art/Characters/HumanSources/system/eyes/materials'/(eye+'.mhmat')
    texture=next(line.split(maxsplit=1)[1] for line in material.read_text().splitlines() if line.startswith('diffuseTexture '))
    ids+=['makehuman:system/eyes/materials/'+eye+'.mhmat','makehuman:system/eyes/materials/'+texture]
    return sorted(set(ids))

def read_recipes(path=None):
    data=json.loads(Path(path or ROOT/'Docs/asset_catalog/char_recipes.json').read_text())
    matrix=json.loads((ROOT/'Docs/asset_catalog/char_compatibility.json').read_text())
    validate(data,matrix)
    return data,matrix


def colour_discipline(r,pal,max_sat=.66,max_val=.96,min_val=.08):
    """Visual Bible: lightly graded albedo, no pure black/white, controlled saturation (hi-vis vest accent excepted)."""
    for role in ['top','bottom','accent','outer','cap','detail','apron','shoes','hair','beard']:
        if role not in pal:continue
        if role=='accent' and 'work_vest' in [r['accessory']]+list(r.get('extras',[])):continue
        h=pal[role];red,green,blue=[int(h[i:i+2],16)/255 for i in (0,2,4)]
        v=max(red,green,blue);sat=0 if v==0 else (v-min(red,green,blue))/v
        if sat>max_sat:raise ValueError('Palette %s.%s is too saturated (%.2f > %.2f)'%(pal['id'],role,sat,max_sat))
        if role not in ('hair','beard') and not min_val<=v<=max_val:raise ValueError('Palette %s.%s is pure black/white (value %.2f)'%(pal['id'],role,v))

def skin_like(h):
    """Warm, lightly saturated, light colours read as bare skin next to a face under warm sun (ENV CASCO check 2026-09-30)."""
    import colorsys
    r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    hue,sat,val=colorsys.rgb_to_hsv(r,g,b)
    return 15/360<=hue<=48/360 and .10<=sat<=.45 and val>=.55

def validate(data,matrix):
    forms=json.loads((ROOT/'Docs/asset_catalog/char_naturalism_forms.json').read_text())
    if forms.get('schemaVersion')!=1:raise ValueError('Unknown naturalism form schema')
    face_bounds={'eyeAperture':(.85,1.05),'eyeWidth':(.88,1.05),'lipRelief':(.30,.85),
        'mouthCorner':(-.002,.004),'cheekSupport':(-.005,.006),'bridgeSupport':(-.003,.005),
        'lowerLid':(0,.004),'browSlope':(-.006,.004),'browThickness':(.002,.005)}
    for name,form in forms['heads'].items():
        if form.get('sex') not in ('male','female'):raise ValueError('Invalid head sex '+name)
        expression=form.get('expression',{})
        if expression.get('mood') not in ('welcoming','happy','relaxed','grumpy','wry','focused'):
            raise ValueError('Missing authored expression '+name)
        for axis,lo,hi in [('smile',-.55,1.1),('browInner',-.006,.004),('browOuter',-.004,.006),('asymmetry',-.002,.002)]:
            value=expression.get(axis)
            if not isinstance(value,(int,float)) or not math.isfinite(value) or not lo<=value<=hi:
                raise ValueError('Invalid expression axis '+name+'.'+axis)
        for key,(lo,hi) in face_bounds.items():
            value=form.get(key)
            if not isinstance(value,(int,float)) or not math.isfinite(value) or not lo<=value<=hi:
                raise ValueError('Invalid naturalism head axis '+name+'.'+key)
    bodies={b['id']:b for b in matrix['bodies']}
    profiles={p['id']:p for p in json.loads((ROOT/'Docs/asset_catalog/char_body_profiles.json').read_text())['profiles']}
    if not data['recipes']:raise ValueError('Empty recipe batch')
    for p in profiles.values():
        for k in ['height','shoulders','torso','hips','depth','legs','armLength','head','jaw','nose','cheeks','brow']:
            if not isinstance(p[k],(int,float)) or not math.isfinite(p[k]):raise ValueError('Non-finite profile '+p['id'])
            if k!='brow' and p[k]<=0:raise ValueError('Invalid profile dimension '+p['id'])
    # Anatomical identity axes remain bounded; reject typos and non-finite input
    # before expensive mesh assembly. The output anthropometry gates still apply.
    bounds={'faceWidth':(.86,1.14),'jaw':(.86,1.16),'cheeks':(.84,1.14),
        'nose':(.84,1.18),'noseWidth':(.82,1.18),'mouthWidth':(.82,1.16),
        'craniumWidth':(.90,1.12),'eyeSpacing':(.90,1.10),'chin':(-.6,1.0),
        'forehead':(-.006,.006),'ageSag':(0,.009),'faceAsymmetry':(-.003,.003),
        'eyeHeight':(-.004,.004),'eyeTilt':(-.003,.003),'hand':(.88,1.02)}
    for profile in profiles.values():
        for k,(lo,hi) in bounds.items():
            if k in profile and (not isinstance(profile[k],(int,float)) or not math.isfinite(profile[k]) or not lo<=profile[k]<=hi):
                raise ValueError('Invalid anatomical identity axis '+profile['id']+'.'+k)
    palettes={p['id']:p for p in data['palettes']}
    if len(palettes)!=len(data['palettes']):raise ValueError('Duplicate palette identity')
    vocab=matrix['vocabulary']
    seen=set()
    for p in palettes.values():
        if not re.fullmatch('[a-z][a-z0-9-]{2,40}',p['id']):raise ValueError('Invalid palette identity')
        for k in ['top','bottom','accent','hair','shoes']:
            if not re.fullmatch('[0-9A-Fa-f]{6}',p[k]):raise ValueError('Invalid palette '+p['id'])
        for k in ['outer','cap','detail','beard','skin','eyes','apron']:
            if k in p and not re.fullmatch('[0-9A-Fa-f]{6}',p[k]):raise ValueError('Invalid optional palette colour '+k+' in '+p['id'])
        unknown=set(p)-{'id','top','bottom','accent','hair','shoes','outer','cap','detail','beard','skin','eyes','apron'}
        if unknown:raise ValueError('Unknown palette role(s) '+','.join(sorted(unknown))+' in '+p['id'])
    for r in data['recipes']:
        if not re.fullmatch('[a-z][a-z0-9-]{2,40}',r['id']) or r['id'] in seen:
            raise ValueError('Invalid/duplicate generated identity: '+r['id'])
        seen.add(r['id'])
        if r['body'] not in bodies:raise ValueError('Unsupported body family: '+r['body'])
        b=bodies[r['body']]
        if b.get('civilianUse')=='NOT_FOR_CIVILIANS':raise ValueError('Body family %s is not admitted for civilians (%s)'%(r['body'],r['id']))
        if r['top'] not in b['garments']:raise ValueError('Unsupported top: '+r['top'])
        if r['hair']!='none' and r['hair'] not in b['hair']:raise ValueError('Hair/body mismatch: '+r['hair']+'/'+r['body'])
        if r.get('profile') not in profiles:raise ValueError('Unsupported body profile')
        if profiles[r['profile']]['body']!=r['body']:raise ValueError('Body/profile mismatch')
        if r['height']!=profiles[r['profile']]['height']:raise ValueError('Height/profile disagreement')
        if r['bottom'] not in vocab['bottoms'] or r['bottom'] not in b.get('bottoms',vocab['bottoms']):raise ValueError('Unsupported bottom')
        if r['accessory'] not in vocab['accessories']:raise ValueError('Unsupported accessory')
        extras=r.get('extras',[])
        if len(set(extras))!=len(extras) or any(e not in vocab['extras'] for e in extras):raise ValueError('Unsupported extra')
        if r.get('footwear') not in vocab['footwear']:raise ValueError('Unsupported footwear')
        if r.get('headwear') not in vocab['headwear']:raise ValueError('Unsupported headwear')
        facial=r.get('facial',[])
        if len(set(facial))!=len(facial) or any(f not in vocab['facial'] or f not in b.get('facial',[]) for f in facial):raise ValueError('Unsupported facial hair for '+r['body'])
        if r.get('brows','default') not in vocab['brows'] or (r.get('brows')=='thick' and 'thick' not in b.get('brows',[])):raise ValueError('Unsupported brows')
        if r['bottom']=='work' and not b.get('workDonor',False):raise ValueError('Donor work trousers need a matching Regular body')
        if r['accessory']=='work_vest' and r['top']!='sweater':raise ValueError('Work vest requires covered sweater fit')
        if 'waistcoat' in [r['accessory']]+extras and r['top']!='shirt':raise ValueError('Waistcoat requires a shirt underneath')
        if r['bottom']=='overalls' and r['top'] not in ['tshirt','sweater','shirt']:raise ValueError('Overalls need a plain layer underneath')
        if r.get('eyes','brown') not in vocab['eyes']:raise ValueError('Unsupported eye colour')
        sex='female' if r['body'].endswith('female') else 'male'
        if r.get('face','default') not in vocab.get('faces',{}).get(sex,['default']):raise ValueError('Unsupported face variant %s for %s'%(r.get('face'),r['id']))
        if r['skin'] not in matrix['skinTones']['tones']:raise ValueError('Unsupported skin tone '+str(r['skin']))
        if r.get('headForm') not in forms['heads']:raise ValueError('Unknown authored head form')
        if forms['heads'][r['headForm']]['sex']!=sex:raise ValueError('Authored head form has incompatible source family')
        if r.get('hairStyle') not in forms['hairStyles']:raise ValueError('Unknown authored hair style')
        if r.get('garmentPattern') not in forms['garmentPatterns']:raise ValueError('Unknown authored garment pattern')
        if r['palette'] not in palettes:raise ValueError('Unknown palette')
        if r.get('fit','regular') not in ('fitted','regular','loose'):raise ValueError('Unknown garment fit')
        if r.get('qualityTier','secondary') not in ('conversation','secondary','ambient'):raise ValueError('Unknown visual quality tier')
        if r.get('complexion','clear') not in ('clear','freckles','weathered','age_spots','mole','scar'):raise ValueError('Unknown complexion')
        for key,limit in [('stanceBias',.05),('slouch',.15)]:
            value=r.get(key,0)
            if not isinstance(value,(int,float)) or not math.isfinite(value) or abs(value)>limit:raise ValueError('Invalid posture '+key)

        rules=matrix.get('outfitRules')
        if rules:
            if r['footwear'] not in rules['footwearByBottom'][r['bottom']]:raise ValueError('Footwear %s does not go with %s (%s)'%(r['footwear'],r['bottom'],r['id']))
            if r['footwear']=='trainers' and r['top'] not in rules['trainersRequireTop']:raise ValueError('Trainers need a casual top ('+r['id']+')')
            pal=palettes[r['palette']]
            def luma(h):return (.2126*int(h[0:2],16)+.7152*int(h[2:4],16)+.0722*int(h[4:6],16))/255
            if r['footwear'] in ['loafers','work_shoes','ankle_boots','work_boots'] and r.get('shoeFabric')!='rubber' and luma(pal['shoes'])>rules['formalBottomShoeMaxLuma']:
                raise ValueError('Leather shoes must be dark enough to read as footwear ('+r['id']+')')
        if not matrix['limits']['heightMin']<=r['height']<=matrix['limits']['heightMax']:raise ValueError('Height outside admitted range')
        colour_discipline(r,palettes[r['palette']])
        pal=palettes[r['palette']]
        neck_layer=pal['accent'] if r['top'] in ('cardigan','light_coat') else pal['top'] if r['top'] in ('shirt','tshirt') else None
        if neck_layer and skin_like(neck_layer):raise ValueError('Layer at the neck of %s (%s) reads as bare skin; use a cooler or deeper colour'%(r['id'],neck_layer))
        if r['top'] in ('cardigan','light_coat'):
            rr,gg,bb=[int(pal['accent'][i:i+2],16) for i in (0,2,4)]
            if max(rr,gg,bb)/255>.80 and bb<=rr:raise ValueError('Light warm inner layer under an open outer layer of %s (%s) reads as a bare torso in warm sun; use a cool tint or a mid value'%(r['id'],pal['accent']))
    return True

def check_proportions(metrics,anthropometry,body):
    """Reject builds outside the human envelope (native rest-pose ratios of the source body +- bounded deviation)."""
    native=anthropometry['native'][body];lim=anthropometry['limits'];problems=[]
    for key,ref in (('shoulderJointRatio',native['shoulderJoint']),('hipJointRatio',native['hipJoint'])):
        ratio=metrics[key]/ref;lo,hi=lim[key]
        if not lo<=ratio<=hi:problems.append('%s %.3f is %.2fx the source body (allowed %.2f-%.2f)'%(key,metrics[key],ratio,lo,hi))
    for key in ('headLength','pelvisHeight','headsTall','handOverHead'):
        if key not in lim or key not in metrics:continue
        lo,hi=lim[key]
        if not lo<=metrics[key]<=hi:problems.append('%s %.3f outside %.3f-%.3f'%(key,metrics[key],lo,hi))
    if problems:raise ValueError('Non-human proportions for %s: %s'%(metrics['family'],'; '.join(problems)))
    return True


if __name__=='__main__':
    data,_=read_recipes()
    print('CHAR_RECIPES_VALID',len(data['recipes']))
