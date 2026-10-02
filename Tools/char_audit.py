"""CHAR evidence checks and bounded lineage registration. Standard library only.

python Tools/char_audit.py negative [--write]
python Tools/char_audit.py lineage
python Tools/char_audit.py repeat --other <second-build-directory> [--write]
python Tools/char_audit.py verify
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from char_manifest import ROOT, read_recipes, validate, check_proportions, admitted_head, human_source_ids

E=ROOT/'Docs/evidence/WP-PROD-CHAR-01'
PROJECT=ROOT/'Unity/JuegoDef'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def negative():
    data,matrix=read_recipes();rows=[]
    mutations=[('unsupported body','body','teen_male'),('hair mismatch','hair','hair_balding'),
        ('body profile mismatch','profile','tall_heavy'),('unknown profile','profile','hero'),
        ('unsupported top','top','armour'),('invalid output path','id','../escape'),
        ('unknown palette','palette','missing'),('non-finite height','height',float('nan')),
        ('wrong height','height',99),('unsupported bottom','bottom','shorts'),
        ('unsupported accessory','accessory','weapon'),('unsupported footwear','footwear','heels'),
        ('unsupported headwear','headwear','helmet')]
    mutations += [('unknown authored head','headForm','unknown'),('wrong authored head sex','headForm','dock-worker'),
        ('unknown everyday hair','hairStyle','warrior-spikes'),('unknown garment pattern','garmentPattern','armour')]
    cases=[]
    for name,key,value in mutations:
        d=copy.deepcopy(data);d['recipes'][0][key]=value;cases.append((name,d))
    d=copy.deepcopy(data);d['recipes'].append(copy.deepcopy(d['recipes'][0]));cases.append(('duplicate output',d))
    d=copy.deepcopy(data);d['recipes'][1]['top']='cardigan';cases.append(('vest over unsupported layer',d))
    d=copy.deepcopy(data);d['palettes'][0]['top']='ZZFFFF';cases.append(('bad material color',d))
    d=copy.deepcopy(data);d['palettes'][0]['id']='../escape';cases.append(('unsafe palette path',d))
    d=copy.deepcopy(data);d['recipes']=[];cases.append(('empty batch',d))
    def one(rid,**kw):
        d=copy.deepcopy(data)
        r=next(x for x in d['recipes'] if x['id']==rid);r.update(kw);return d
    def pal(pid,**kw):
        d=copy.deepcopy(data);next(x for x in d['palettes'] if x['id']==pid).update(kw);return d
    cases+=[('facial hair on a female body',one('market-worker',facial=['beard'])),
        ('thick brows on a female body',one('market-worker',brows='thick')),
        ('unknown facial hair',one('eccentric',facial=['mullet'])),
        ('unknown skin tone',one('market-worker',skin='green')),
        ('trainers with a formal coat',one('office-worker',footwear='trainers')),
        ('work boots with a skirt',one('everyday-pedestrian',footwear='work_boots')),
        ('donor work trousers on a superhero body',one('mechanic',bottom='work')),
        ('waistcoat without a shirt',one('waiter-veteran',top='sweater')),
        ('overalls over a hoodie',one('mechanic',top='hoodie')),
        ('over-saturated garment colour',pal('market',top='FF0000')),
        ('pure black garment',pal('office',bottom='000000')),
        ('pale leather shoes',pal('market',shoes='C8C8C0')),
        ('unsupported palette role',pal('market',glow='FFFFFF')),
        # 2026-09-30 art QA rules
        ('gym superhero body for a civilian',one('bruiser',body='superhero_male',profile='bruiser')),
        ('neck layer that reads as bare skin',pal('elderwoman',accent='E4DCC8')),
        ('light warm tee under an open jacket',pal('student',accent='E6E4DD')),
        ('undefined garment fit',one('market-worker',fit='inflate')),
        ('unknown visual quality tier',one('elder-woman',qualityTier='ultra')),
        ('unknown complexion',one('bruiser',complexion='metal')),
        ('non-finite asymmetry',one('eccentric',stanceBias=float('nan'))),
        ('impossible resting lean',one('eccentric',slouch=1.0)),
        ('unknown face variant',one('elder-woman',face='anime')),
        ('male grooming variant on a woman',one('elder-woman',face='clean'))]
    for name,d in cases:
        try:validate(d,matrix)
        except (ValueError,KeyError) as exc:rows.append({'case':name,'result':'REJECT','reason':str(exc)})
        else:raise AssertionError('Unexpected admission: '+name)
    good={'family':'probe','shoulderJointRatio':.212,'hipJointRatio':.100,'headLength':.116,'pelvisHeight':.524,'headsTall':7.5,'handOverHead':.80}
    for name,patch in [('hips 37% wider than the source body',{'hipJointRatio':.138*1.4}),('shoulders 25% wider',{'shoulderJointRatio':.212*1.25}),
                       ('head too small for the body',{'headLength':.095}),('legs too long',{'pelvisHeight':.58}),('legs too short',{'pelvisHeight':.46}),
                       ('pin head: 8.6 heads tall (raw Quaternius male)',{'headsTall':8.6}),('oversized hands: one head long',{'handOverHead':1.0})]:
        try:check_proportions({**good,**patch},matrix['anthropometry'],'regular_male')
        except ValueError as exc:rows.append({'case':name,'result':'REJECT','reason':str(exc)})
        else:raise AssertionError('Unexpected proportion admission: '+name)
    check_proportions(good,matrix['anthropometry'],'regular_male')
    heads=read(ROOT/'Art/Characters/HumanHeads/source_manifest.json')
    for r in data['recipes']:admitted_head(r,heads)
    for name,mutation in [
        ('missing anatomical bundle',lambda d:d['heads'].pop(0)),
        ('unadmitted head license',lambda d:d.update(assetLicense='CC-BY-4.0')),
        ('unadmitted authoring version',lambda d:d.update(mpfbCommit='0'*40)),
        ('anatomical head sex mismatch',lambda d:d['heads'][0].update(sex='male')),
        ('unmatched source hair bundle',lambda d:d['heads'][0].update(hairStyle='crop')),
        ('changed anatomical bundle bytes',lambda d:d['heads'][0].update(sha256='0'*64)),
        ('changed raw anatomical input',lambda d:d['heads'][0]['sourceFiles'][0].update(sha256='0'*64))]:
        d=copy.deepcopy(heads);mutation(d)
        try:admitted_head(data['recipes'][0],d)
        except (ValueError,KeyError) as exc:rows.append({'case':name,'result':'REJECT','reason':str(exc)})
        else:raise AssertionError('Unexpected anatomical admission: '+name)
    return {'positiveRecipes':len(data['recipes']),'cases':rows}

def lineage():
    data,matrix=read_recipes();bodies={b['id']:b for b in matrix['bodies']}
    registry=ROOT/'Docs/asset_catalog/lineage.json';doc=read(registry)
    doc['assets']=[a for a in doc['assets'] if not a['path'].startswith(('Assets/JuegoDef/Derived/CHAR/','Assets/JuegoDef/Characters/Textures/T_CHAR_Skin_'))]
    doc['assets']=[a for a in doc['assets'] if not a['path'].startswith('Assets/JuegoDef/Characters/Textures/T_CHAR_Hair')]
    recipes={r['id']:r for r in data['recipes']}
    admission=read(ROOT/'Art/Characters/HumanSources/admission.json')
    human_outputs={x['output']:x for x in admission['derived']+admission.get('projectAuthored',[])}
    for p in sorted((PROJECT/'Assets/JuegoDef/Derived/CHAR').rglob('*')):
        if not p.is_file() or p.suffix=='.meta':continue
        r=recipes.get(p.stem)
        if p.stem.startswith('T_CHAR_Human_'):
            receipt=human_outputs.get(p.relative_to(ROOT).as_posix())
            assert receipt,'Missing anatomical texture receipt '+p.name
            assert digest(p)==receipt['sha256'],'Stale anatomical texture receipt '+p.name
            sources=[receipt.get('sourceContext') or 'makehuman:system/'+receipt['source']]
            doc['assets'].append({'id':'char:'+p.relative_to(PROJECT/'Assets/JuegoDef/Derived/CHAR').as_posix(),'path':p.relative_to(PROJECT).as_posix(),
                'sourceIds':sources,'recipe':'admitted anatomical head texture',
                'materialAuthorship':receipt.get('authorship','Colour/saturation derivation of the retained CC0 MakeHuman albedo; source UVs/alpha retained.'),
                'transformation':'Tools/char_human_textures.py / char_human_sources.py; hash-bound admission receipt',
                'workpack':'WP-PROD-CHAR-01'})
            continue
        if p.stem.startswith('T_CHAR_Eye_'):
            doc['assets'].append({'id':'char:'+p.relative_to(PROJECT/'Assets/JuegoDef/Derived/CHAR').as_posix(),'path':p.relative_to(PROJECT).as_posix(),
                'sourceIds':sorted({b['source'] for b in bodies.values()}),'recipe':'shared iris colour variant',
                'materialAuthorship':'CC0 eye-atlas derivative: restrained iris colours, warm ivory sclera and softened exterior socket paint; source UVs and highlight placement retained.',
                'transformation':'Tools/char_skin.py derive_eye','workpack':'WP-PROD-CHAR-01'})
            continue
        if p.stem.startswith('char_') and p.suffix in ('.anim','.overrideController'):
            recipe_id=p.stem[len('char_'):].rsplit('_',1)[0] if p.suffix=='.anim' else p.stem[len('char_'):]
            recipe=recipes[recipe_id]
            motion=p.stem.rsplit('_',1)[-1] if p.suffix=='.anim' else None
            ids=([recipe.get('pose','ual1:idle_loop')] if motion=='Idle' else ['ual1:walk_loop'] if motion=='Walk' else ['ual1:idle_talking_loop'] if motion=='Talking' else [recipe.get('pose','ual1:idle_loop'),'ual1:walk_loop','ual1:idle_talking_loop'])
            doc['assets'].append({'id':'char:'+p.relative_to(PROJECT/'Assets/JuegoDef/Derived/CHAR').as_posix(),'path':p.relative_to(PROJECT).as_posix(),
                'sourceIds':sorted(set(ids)),'recipe':recipe_id+' presentation posture',
                'materialAuthorship':None,'transformation':'CharPosture: civilian clip plus bounded spine/neck/shoulder static offsets; root and leg curves preserved; override of shared presentation controller','workpack':'WP-PROD-CHAR-01'})
            continue
        if p.suffix=='.anim' and p.stem.startswith('civ_'):
            clip=p.stem[len('civ_'):].replace('_',':',1)
            doc['assets'].append({'id':'char:'+p.relative_to(PROJECT/'Assets/JuegoDef/Derived/CHAR').as_posix(),'path':p.relative_to(PROJECT).as_posix(),
                'sourceIds':[clip],'recipe':'shared civilian posture clip',
                'materialAuthorship':None,
                'transformation':'Editor/Char/CharPosture.cs: copy of the admitted Humanoid clip with relaxed hands, hip-width stance, softened chest and optional forearm pronation (held components only)','workpack':'WP-PROD-CHAR-01'})
            continue
        if p.stem.startswith('T_CHAR_Skin_'):
            body=p.stem[len('T_CHAR_Skin_'):]
            face=next((f for f in ('_natural','_mature','_older','_clean') if body.endswith(f)),'')
            body=body[:len(body)-len(face)];assert body in bodies,'Unknown skin atlas '+p.name
            if face:
                doc['assets'].append({'id':'char:'+p.relative_to(PROJECT/'Assets/JuegoDef/Derived/CHAR').as_posix(),'path':p.relative_to(PROJECT).as_posix(),
                    'sourceIds':[bodies[body]['source']],'recipe':'shared face variant ('+face[1:]+')',
                    'materialAuthorship':'Deterministic paint-over of the derived CC0 skin atlas (make-up/stubble chroma shift, soft age creases).',
                    'transformation':'Tools/char_skin.py face_variant','workpack':'WP-PROD-CHAR-01'})
                continue
            doc['assets'].append({'id':'char:'+p.relative_to(PROJECT/'Assets/JuegoDef/Derived/CHAR').as_posix(),'path':p.relative_to(PROJECT).as_posix(),
                'sourceIds':[bodies[body]['source']],'recipe':'shared fair-skin atlas',
                'materialAuthorship':'Colour-remapped derivative of the admitted CC0 base-character skin atlas; painted shading preserved.',
                'transformation':'Tools/char_skin.py (median-tone gain to a pale peach base at 1024 px; deeper tones are per-person material tints)','workpack':'WP-PROD-CHAR-01'})
            continue
        if r:
            sources=[bodies[r['body']]['source'],bodies[r['body']]['donor']]
            if r.get('headForm'):sources+=human_source_ids(r)
            if not r.get('hairStyle'):
                if r['hair']!='none':sources.append('base:'+r['hair'])
                sources+=['base:hair_'+f for f in r.get('facial',[])]
                if r.get('brows')=='thick':sources.append('base:eyebrows_thick')
        else:
            users=[x for x in data['recipes'] if p.stem.startswith(x['palette']+'-')]
            if p.stem in ['reflective','sole']:users=[x for x in data['recipes'] if 'work_vest' in [x['accessory']]+x.get('extras',[]) or (p.stem=='sole' and x['footwear']=='trainers')]
            assert users,'Orphan material '+p.name
            def src(x):
                if '-human-' in p.stem:return human_source_ids(x)
                if x.get('hairStyle') and p.stem.endswith(('-hair','-beard','-lid')):return [bodies[x['body']]['source']]
                if p.stem.endswith('-hair'):return ['base:'+x['hair']] if x['hair']!='none' else [bodies[x['body']]['source']]
                if p.stem.endswith('-beard'):return ['base:hair_'+f for f in x.get('facial',[])] or ['base:'+x['hair']]
                if p.stem.endswith('-shoes') or p.stem=='sole':return [bodies[x['body']]['donor']]
                return [bodies[x['body']]['source']]
            sources=sorted({i for x in users for i in src(x)})
        doc['assets'].append({'id':'char:'+p.relative_to(PROJECT/'Assets/JuegoDef/Derived/CHAR').as_posix(),
            'path':p.relative_to(PROJECT).as_posix(),'sourceIds':sources,
            'recipe':r['id'] if r else 'shared semantic material; project palette',
            'materialAuthorship':None if r else 'Project-authored URP parameters; sourceIds identify the source mesh/texture assignment context, not copied source material bytes.',
            'transformation':'Tools/char_build.py / char_human.py: admitted CC0 anatomical head/lids/eyes/hair on the retained body/65-bone rig; constructed sewn wardrobe; CharFactory.Build; NpcPresentation additive blink/gaze; no exported asset hand edits',
            'workpack':'WP-PROD-CHAR-01'})
    save(registry,doc);return {'registered':len(doc['assets'])}

def repeat(other):
    a=read(E/'build_inventory.json')['variants'];b=read(other/'build_inventory.json')['variants']
    assert {r['id'] for r in a}=={r['id'] for r in b},'Batch membership differs'
    rows=[]
    for x in a:
        y=next(r for r in b if r['id']==x['id'])
        assert x['geometrySha256']==y['geometrySha256'],x['id']+' semantic rebuild differs'
        assert x['recipe']==y['recipe'] and x['unweightedVertices']==y['unweightedVertices']==0
        rows.append({'id':x['id'],'semanticSha256':x['geometrySha256'],'match':True})
    return {'method':'Two independent Blender factory-reset batch builds; hash includes mesh positions/topology/UV layers/smooth flags/material slots/weights, complete blend-shape coordinates and rest bone matrices. FBX timestamps and polygon enumeration/start-corner order excluded; winding preserved.','variants':rows}

def verify():
    data,_=read_recipes();report=read(E/'unity_runtime_validation.json')
    assert report['variants']==len(data['recipes']) and report['playMode'] and not report['problems']
    assert len(report['samples'])==len(data['recipes'])*12
    expected={(r['id'],motion,phase) for r in data['recipes'] for motion in ['Idle','Walk','Talking'] for phase in [0,.25,.5,.75]}
    assert {(s['id'],s['motion'],s['phase']) for s in report['samples']}==expected,'Missing or repeated motion/phase coverage'
    assert all(s['finite'] for s in report['samples']),'Non-finite pose'
    assert len({i['path'] for i in report['inputs']})==len(report['inputs']),'Duplicate runtime input'
    rebuild=read(E/'unity_rebuild_validation.json')
    assert rebuild['variants']==len(data['recipes']) and not rebuild['problems']
    assert rebuild['inputs']==report['inputs'],'Stale prefab rebuild evidence'
    for item in report['inputs']:
        assert (ROOT/item['path']).is_file(),'Missing '+item['path']
        assert digest(ROOT/item['path'])==item['sha256'],'Stale runtime input '+item['path']
    built=read(E/'build_inventory.json')['variants']
    assert {r['id'] for r in built}=={r['id'] for r in data['recipes']},'Incomplete Blender batch'
    for r in built:
        assert r['recipe']==next(item for item in data['recipes'] if item['id']==r['id']),'Stale built recipe'
        assert r['bones']==65 and r['unweightedVertices']==0 and r['donorRestDelta']<.0001
        assert digest(PROJECT/'Assets/JuegoDef/Derived/CHAR/Models'/ (r['id']+'.fbx'))==r['exportSha256'],'Changed generated FBX'
    for item in read(E/'build_inventory.json')['inputs']:
        assert digest(ROOT/item['path'])==item['sha256'],'Stale Blender build input '+item['path']
    repeated=read(E/'repeatability.json')['variants']
    assert len(repeated)==len(built) and {r['id'] for r in repeated}=={r['id'] for r in built},'Incomplete repeat build'
    for row in repeated:
        original=next(r for r in read(E/'build_inventory.json')['variants'] if r['id']==row['id'])
        assert row['match'] and row['semanticSha256']==original['geometrySha256'],'Stale rebuild proof'
    assert negative()==read(E/'negative_cases.json'),'Stale recipe rejection evidence'
    images=list(E.glob('fit_*.png'))+list(E.glob('group_*.png'))
    assert len(images)==60,'Missing or unexpected pose/distance captures'
    visual=read(E/'visual_review.json')
    assert digest(E/'unity_runtime_validation.json')==visual['runtimeReportSha256'],'Stale visual review'
    assert set(p.name for p in images)==set(item['path'] for item in visual['captures']),'Visual capture membership changed'
    for item in visual['captures']:assert digest(E/item['path'])==item['sha256'],'Changed visual capture '+item['path']
    if all(r.get('headForm') for r in data['recipes']):
        from char_evidence import verify as verify_naturalism
        verify_naturalism()
    return {'variants':len(data['recipes']),'samples':len(report['samples']),'runtimeInputs':len(report['inputs']),'captures':len(images),'problems':[]}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['negative','lineage','repeat','verify']);p.add_argument('--other',type=Path);p.add_argument('--write',action='store_true');args=p.parse_args()
    if args.command=='negative':result=negative();target=E/'negative_cases.json'
    elif args.command=='repeat':result=repeat(args.other);target=E/'repeatability.json'
    elif args.command=='lineage':result=lineage();target=None
    else:result=verify();target=None
    if args.write and target:save(target,result)
    print(json.dumps(result,indent=2))
