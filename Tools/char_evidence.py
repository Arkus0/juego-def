"""Collect and verify the bounded naturalism visual evidence, without editing Unity assets.

python Tools/char_evidence.py collect --audit <preserved operator audit>
python Tools/char_evidence.py verify
"""
import argparse
import gzip
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'Docs/evidence/WP-PROD-CHAR-01'
N=E/'naturalism_2026-10-01'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def row(p,base=ROOT):return {'path':p.relative_to(base).as_posix(),'sha256':digest(p)}

def collect(audit):
    from PIL import Image,ImageDraw
    ids=[r['id'] for r in read(ROOT/'Docs/asset_catalog/char_recipes.json')['recipes']]
    snapshot=audit/'ENV01Review'
    batches=[('before',snapshot/'Unity/JuegoDef/Captures/char','comparison_before'),
             ('after',ROOT/'Unity/JuegoDef/Captures/char','comparison_after')]
    for prefix,source,folder in batches:
        names=[f'{prefix}_face_{rid}_{yaw}.png' for rid in ids for yaw in (0,45,90)]
        names += [f'{prefix}_bare_{rid}.png' for rid in ids]
        names += [f'{prefix}_group_{batch}{suffix}.png' for batch in range(3) for suffix in ('','_silhouette')]
        files=[source/name for name in sorted(names)]
        assert len(files)==66 and all(p.is_file() for p in files),'Missing exact fifteen-person portraits/groups: '+prefix
        dest=N/folder;dest.mkdir(parents=True,exist_ok=True)
        for p in files:shutil.copy2(p,dest/p.name)
    env=N/'ENV01';env.mkdir(parents=True,exist_ok=True)
    captures=snapshot/'Captures/ENV01Characters'
    env_report=read(captures/'ENV_CAPTURES.json')
    assert env_report['playMode'] and len(env_report['captures'])==18
    assert {r['ids'][0] for r in env_report['captures'] if len(r['ids'])==1}==set(ids)
    for item in env_report['captures']:shutil.copy2(captures/item['file'],env/item['file'])
    shutil.copy2(captures/'ENV_CAPTURES.json',env/'ENV_CAPTURES.json')
    shutil.copy2(captures/'ENV_ATTENTION.json',env/'ENV_ATTENTION.json')
    shutil.copy2(snapshot/'ENV_SOURCE_MANIFEST.json',env/'ENV_SOURCE_MANIFEST.json')
    fixture=snapshot/'Unity/JuegoDef/Assets/JuegoDef/Scenes/CHAR/ENV01CharacterReview.unity'
    # Keep the exact Editor-authored fixture bytes without committing a >100 MB
    # text blob. A deterministic gzip is inspectable by ordinary decompression.
    archived_fixture=env/'ENV01CharacterReview.unity.txt.gz'
    archived_fixture.write_bytes(gzip.compress(fixture.read_bytes(),mtime=0))
    old_fixture=env/'ENV01CharacterReview.unity.txt'
    if old_fixture.is_file():old_fixture.unlink()
    # The snapshot's effective scene/renderer bytes are independently retained
    # outside Git, including licensed source assets. Preserve a durable locator
    # and compare every consumed project CHAR asset against this candidate.
    overlay=[]
    for folder in ('Characters','Derived/CHAR','Editor/Char','Editor/Animation'):
        for p in sorted((ROOT/'Unity/JuegoDef/Assets/JuegoDef'/folder).rglob('*')):
            if p.is_file():
                counterpart=snapshot/p.relative_to(ROOT)
                assert counterpart.is_file() and digest(p)==digest(counterpart),'Stale ENV overlay '+str(p)
                overlay.append(row(p))
    for folder in ('Art/Characters/HumanHeads','Art/Characters/HumanSources'):
        for p in sorted((ROOT/folder).rglob('*')):
            if p.is_file():
                counterpart=snapshot/p.relative_to(ROOT)
                assert counterpart.is_file() and digest(p)==digest(counterpart),'Stale ENV anatomical source '+str(p)
                overlay.append(row(p))
    source=read(env/'ENV_SOURCE_MANIFEST.json')
    critical=[r for r in source['files'] if r['path'].startswith(('Unity/JuegoDef/Assets/JuegoDef/Rendering/',
                'Unity/JuegoDef/Assets/JuegoDef/Scenes/ENV/','Unity/JuegoDef/ProjectSettings/GraphicsSettings.asset',
                'Unity/JuegoDef/ProjectSettings/QualitySettings.asset'))]
    for r in critical:assert digest(snapshot/r['path'])==r['sha256'],'Changed ENV calibration authority '+r['path']
    save(env/'CALIBRATION_IDENTITY.json',{'snapshot':str(snapshot),'source':'effective ENV worktree bytes at copy time; unmerged calibration',
         'sceneFixture':{**row(archived_fixture),'compression':'gzip','decompressedSha256':digest(fixture),
                         'decompressedBytes':fixture.stat().st_size}, 'unchangedSceneAndRenderingInputs':critical,
         'characterOverlay':overlay,'note':'The complete hash-bound snapshot is preserved at the local path. Captures do not claim NPC navigation or final dialogue integration.'})
    baseline=read(audit/'baseline_manifest.json')
    save(N/'BASELINE_IDENTITY.json',{'snapshot':str(audit/'baseline'),'preservedManifest':baseline,
         'note':'Before portraits are the preserved pre-naturalism CHAR WIP, rendered through the same CharReview capture configuration; this was not an accepted art baseline.'})
    canvas=Image.new('RGB',(1500,1170),(235,233,225));draw=ImageDraw.Draw(canvas)
    for i,n in enumerate(ids):
        im=Image.open(N/'comparison_after'/f'after_face_{n}_0.png').convert('RGB').crop((150,235,450,595))
        x=(i%5)*300;y=(i//5)*390;canvas.paste(im,(x,y));draw.text((x+8,y+364),n,fill=(35,35,35))
    canvas.save(N/'quince_rostros.jpg',quality=95)
    pilots=['market-worker','dock-worker','older-resident','elder-woman','student','waiter-veteran']
    pairs=Image.new('RGB',(960,1200),(235,233,225));draw=ImageDraw.Draw(pairs)
    for i,n in enumerate(pilots):
        x=(i%2)*480;y=(i//2)*400
        draw.text((x+12,y+8),n,fill=(35,35,35))
        for j,(prefix,folder,label) in enumerate([('before','comparison_before','Antes: WIP conservado'),('after','comparison_after','Ahora')]):
            im=Image.open(N/folder/f'{prefix}_face_{n}_0.png').convert('RGB').crop((150,235,450,650)).resize((230,318))
            pairs.paste(im,(x+j*240+5,y+42));draw.text((x+j*240+8,y+368),label,fill=(35,35,35))
    pairs.save(N/'comparativa_seis.jpg',quality=95)
    # Fit overviews retain all poses at their original scale in the PNGs; these
    # assemblies are convenient indexes, never additional fitted samples.
    for motion in ('Idle','Walk','Talking'):
        for view in ('front','side','rear'):
            files=sorted(E.glob(f'fit_{motion}_*_{view}.png'));assert len(files)==4
            thumbs=[]
            for p in files:
                im=Image.open(p).convert('RGB');im.thumbnail((2400,400));thumbs.append(im)
            sheet=Image.new('RGB',(2400,sum(im.height+24 for im in thumbs)),(235,233,225));draw=ImageDraw.Draw(sheet);y=0
            for p,im in zip(files,thumbs):draw.text((8,y+3),p.name,fill=(35,35,35));sheet.paste(im,(0,y+24));y+=im.height+24
            sheet.save(N/f'fit_{motion}_{view}_overview.jpg',quality=95)
    live=read(N/'living/LIVING_LIVE.json');live_frames=live['frames']
    assert not live['error'] and len(live_frames)>=60
    frames=[Image.open(N/'living/frames'/f['file']).convert('RGB') for f in live_frames]
    durations=[max(30,round((b['time']-a['time'])*1000)) for a,b in zip(live_frames,live_frames[1:])]+[85]
    frames[0].save(N/'living/waiter_idle.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0)
    files=[p for p in N.rglob('*') if p.is_file() and p.suffix.lower() in ('.png','.jpg','.gif','.json','.txt','.gz') and p.name!='MANIFEST.json']
    tools=[ROOT/'Tools'/n for n in ('CharNaturalismRun.cs','CharNaturalismSafety.cs','CharEnvRun.cs','CharLivingRun.cs','char_evidence.py',
        'char_human_sources.py','char_human_textures.py','char_human.py','char_build.py','char_manifest.py')]
    masters=sorted((ROOT/'Art/Characters/Naturalism').glob('*.blend'));assert {p.stem for p in masters}==set(ids)
    heads=sorted((ROOT/'Art/Characters/HumanHeads').glob('*.blend'));assert {p.stem for p in heads}==set(ids)
    admission=ROOT/'Art/Characters/HumanSources/admission.json'
    manifest={'schemaVersion':1,'variants':ids,'kind':'Worker readiness evidence; independent review and Owner art acceptance pending',
              'runtimeReport':row(E/'unity_runtime_validation.json'),'buildInventory':row(E/'build_inventory.json'),
              'capturingTools':[row(p) for p in tools],'masters':[row(p) for p in masters],
              'anatomicalHeadMasters':[row(p) for p in heads],
              'anatomicalHeadManifest':row(ROOT/'Art/Characters/HumanHeads/source_manifest.json'),
              'cc0Admission':row(admission),
              'files':[row(p) for p in sorted(files)]}
    save(N/'MANIFEST.json',manifest)
    return verify()

def verify():
    m=read(N/'MANIFEST.json');ids=[r['id'] for r in read(ROOT/'Docs/asset_catalog/char_recipes.json')['recipes']]
    assert m['variants']==ids,'Naturalism batch identity changed'
    for item in [m['runtimeReport'],m['buildInventory'],m['anatomicalHeadManifest'],m['cc0Admission']]+m['capturingTools']+m['masters']+m['anatomicalHeadMasters']+m['files']:
        assert digest(ROOT/item['path'])==item['sha256'],'Stale naturalism evidence '+item['path']
    admission=read(ROOT/m['cc0Admission']['path'])
    assert admission['license']=='CC0-1.0','Changed anatomical asset license'
    for item in admission['admitted']+admission['derived']+admission.get('projectAuthored',[]):
        path=item.get('path',item.get('output'))
        assert digest(ROOT/path)==item['sha256'],'Stale admitted anatomical source/output '+path
    env=read(N/'ENV01/CALIBRATION_IDENTITY.json')
    fixture=env['sceneFixture']
    if fixture.get('compression')=='gzip':
        raw=gzip.decompress((ROOT/fixture['path']).read_bytes())
        assert len(raw)==fixture['decompressedBytes'] and hashlib.sha256(raw).hexdigest()==fixture['decompressedSha256'],'Changed calibration fixture bytes'
    safety=read(N/'SAFETY.json')
    assert safety['samples']==len(ids)*3*24 and safety['protectedCurves']==1575 and not safety['problems'],'Incomplete dense safety/curve evidence'
    for item in env['characterOverlay']:assert digest(ROOT/item['path'])==item['sha256'],'Stale ENV character overlay '+item['path']
    attention=read(N/'ENV01/ENV_ATTENTION.json')
    assert attention['playMode'] and attention['variants']==len(ids),'Missing canonical GC2 attention evidence'
    living=read(N/'living/LIVING_AUDIT.json');live=read(N/'living/LIVING_LIVE.json')
    assert living['playMode'] and living['variants']==len(ids) and not living['problems'],'Missing living batch audit'
    assert live['playMode'] and not live['directSampleCalls'] and not live['error'] and len(live['frames'])>=60,'Incomplete live presentation'
    for report in (living,live):
        for item in report['inputs']:assert digest(ROOT/item['path'])==item['sha256'],'Stale living input '+item['path']
    assert len(list((N/'comparison_before').glob('*.png')))==len(list((N/'comparison_after').glob('*.png')))==66
    assert len(list((N/'ENV01').glob('*.png')))==18
    return {'variants':len(ids),'before':66,'after':66,'env':18,'masters':len(m['masters']),'problems':[]}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['collect','verify']);p.add_argument('--audit',type=Path);args=p.parse_args()
    print(json.dumps(collect(args.audit) if args.command=='collect' else verify(),indent=2))
