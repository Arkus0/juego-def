"""Derive bounded Unity albedos from the admitted CC0 core assets.

python Tools/char_human_textures.py --system-assets <pack> --mpfb-source <checkout>
Raw admitted files and their notices are retained for reconstructable reuse.
No regional reference photographs become textures.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--system-assets',required=True);p.add_argument('--mpfb-source',required=True)
    args=p.parse_args();source=Path(args.system_assets);mpfb=Path(args.mpfb_source)
    manifest=json.loads((ROOT/'Art/Characters/HumanHeads/source_manifest.json').read_text())
    raw=ROOT/'Art/Characters/HumanSources';raw.mkdir(parents=True,exist_ok=True)
    prior=json.loads((raw/'admission.json').read_text()) if (raw/'admission.json').exists() else {}
    output=ROOT/'Unity/JuegoDef/Assets/JuegoDef/Derived/CHAR/Textures';output.mkdir(parents=True,exist_ok=True)
    for name in ('LICENSE.ASSETS.md','LICENSE.md'):
        shutil.copyfile(mpfb/name,raw/name)
    shutil.copyfile(mpfb/'src/mpfb/data/3dobjs/base.obj',raw/'hm08.obj')
    jobs={};admitted=set();authored=[]
    def material(kind,name,path,tint=False):
        text=path.read_text()
        line=next(s for s in text.splitlines() if s.startswith('diffuseTexture '))
        image=(path.parent/line.split(maxsplit=1)[1]).resolve()
        jobs['T_CHAR_Human_'+kind+'_'+name+'.png']=(image,kind,tint)
        admitted.add(path);admitted.add(image)
    for head in manifest['heads']:
        skin=head['skin'];hair=head['hair'];brow='eyebrow002' if head['sex']=='female' else 'eyebrow001'
        material('Skin',skin,source/'skins'/skin/(skin+'.mhmat'))
        material('Hair',hair,source/'hair'/hair/(hair+'.mhmat'),True)
        material('Brow',head['sex'],source/'eyebrows'/brow/(brow+'.mhmat'),True)
        material('Lash','standard',source/'eyelashes/eyelashes01/eyelashes01.mhmat',True)
        admitted.update(source/f['path'] for f in head['sourceFiles'])
        for target in head.get('blinkSources',[]):
            original=mpfb/target['path'];dest=raw/'mpfb_targets'/Path(target['path']).relative_to('src/mpfb/data/targets')
            if hashlib.sha256(original.read_bytes()).hexdigest()!=target['sha256']:raise ValueError('Changed CC0 eyelid target')
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest)
        if head.get('occlusion'):
            original=ROOT/head['occlusion']['path']
            if hashlib.sha256(original.read_bytes()).hexdigest()!=head['occlusion']['sha256']:raise ValueError('Changed anatomical AO')
            dest=output/('T_CHAR_Human_AO_'+head['id']+'.png');shutil.copyfile(original,dest)
            authored.append({'output':dest.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                'sourceContext':'makehuman:hm08.obj','authorship':'16-sample local geometry AO baked by char_human_sources.py; actual admitted head/eye surfaces; no directional light painted into albedo.'})
    for eye in ('brown','blue','green','grey'):
        material('Eye',eye,source/'eyes/materials'/(eye+'.mhmat'))
    # Superseded pilot hairstyles remain lawful authoring inputs. Re-derive
    # their retained textures too, so every current output has a current,
    # verifiable raw-source receipt after changes to the common treatment.
    for retained in sorted((raw/'system/hair').glob('*/*.mhmat')):
        name=retained.stem
        if (output/('T_CHAR_Human_Hair_'+name+'.png')).is_file():
            material('Hair',name,source/retained.relative_to(raw/'system'),True)
    receipts=[]
    y,x=np.mgrid[0:128,0:128]/127
    strand=.70+.22*np.sin(x*465+y*39)+.08*np.sin(x*927-y*56)
    alpha=np.clip(np.minimum(np.minimum(x,1-x)*12,np.minimum(y,1-y)*10),0,1)
    alpha*=.75+.25*np.sin(x*465+y*39)**2
    groom=np.empty((128,128,4),dtype=np.uint8)
    groom[:,:,:3]=np.clip(strand[:,:,None]*220,0,255).astype(np.uint8)
    groom[:,:,3]=(alpha*255).astype(np.uint8)
    Image.fromarray(groom,'RGBA').save(output/'T_CHAR_Human_Facial_standard.png')
    authored.append({'output':(output/'T_CHAR_Human_Facial_standard.png').relative_to(ROOT).as_posix(),
        'sha256':hashlib.sha256((output/'T_CHAR_Human_Facial_standard.png').read_bytes()).hexdigest(),
        'sourceContext':'makehuman:hm08.obj','authorship':'Project-authored deterministic strand/cutout tile, used only on admitted male grooming.'})
    for name,(path,kind,tint) in sorted(jobs.items()):
        image=Image.open(path).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
        a=np.asarray(image,dtype=np.float64).copy();rgb=a[:,:,:3]
        if tint:
            # Preserve the actual hair strands/cutout. Neutralize source hair
            # colour so the admitted civilian palettes own grooming colour.
            l=rgb.mean(axis=2);mask=(a[:,:,3]>180)&(l>8)
            middle=np.median(l[mask]) if mask.any() else 100
            g=np.clip(l/max(middle,30)*180,25,248)
            a[:,:,:3]=g[:,:,None]
        elif kind=='Skin':
            # One restrained pale base permits the same body/head tone tint.
            # Preserve lip, eyelid and age variation; no normal or pore map.
            mask=(rgb[:,:,0]>rgb[:,:,1]*1.02)&(rgb[:,:,1]>rgb[:,:,2]*.97)&(rgb.mean(axis=2)>60)&(a[:,:,3]>240)
            median=np.median(rgb[mask],axis=0)
            target=np.array([224,190,173.0]);gain=np.clip(target/median,.75,1.6)
            a[:,:,:3]=np.clip(rgb*gain,0,255)
        elif kind=='Eye':
            # The stock brown iris is red under ENV's warm sunlight. Keep
            # its radial structure, but use a quiet chestnut colour.
            iris=(rgb[:,:,0]>rgb[:,:,1]*1.22)&(rgb[:,:,1]>rgb[:,:,2]*1.15)&(rgb[:,:,1]<145)
            a[:,:,0]=np.where(iris,rgb[:,:,0]*.90,rgb[:,:,0])
            a[:,:,1]=np.where(iris,rgb[:,:,1]*1.12+14,rgb[:,:,1])
            a[:,:,2]=np.where(iris,rgb[:,:,2]*1.3+10,rgb[:,:,2])
            # Two atlas discs, measured from the admitted eye texture. Keep
            # sclera and transparent cornea, darken the iris/limbal border.
            yy,xx=np.mgrid[0:1024,0:1024]
            radius=np.minimum(np.hypot(xx-302,yy-722),np.hypot(xx-725,yy-302))/115
            edge=np.clip((radius-.72)/.27,0,1)
            iris_mask=radius<1.02
            gain=(.66 if name.endswith(('grey.png','blue.png')) else .73 if name.endswith('green.png') else .90)*(1-edge*.30)
            a[:,:,:3]*=np.where(iris_mask,gain,.94)[:,:,None]
        Image.fromarray(a.astype('uint8'),'RGBA').save(output/name)
        receipts.append({'output':(output/name).relative_to(ROOT).as_posix(),
            'sha256':hashlib.sha256((output/name).read_bytes()).hexdigest(),
            'source':path.relative_to(source).as_posix(),'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        if kind=='Skin':
            # Lip colour identifies a restrained wetness variation; broad
            # colour variation stays in the admitted photographic albedo.
            red,green=rgb[:,:,0],rgb[:,:,1]
            lip=np.clip((red-green*1.22)/np.maximum(green*.45,20),0,1)
            control=np.zeros((1024,1024,4),dtype=np.uint8)
            yy,xx=np.mgrid[0:1024,0:1024]
            ellipse=lambda x,y,rx,ry:np.exp(-((xx-x)/rx)**2-((yy-y)/ry)**2)
            nose=ellipse(899,511,24,25)
            lids=ellipse(855,443,13,20)+ellipse(855,576,13,20)
            ears=ellipse(870,380,22,18)+ellipse(870,640,22,18)
            mouth=ellipse(934,511,20,31)
            control[:,:,3]=np.clip((.48+lip*mouth*.42+nose*.17+lids*.065+ears*.08)*255,0,255).astype(np.uint8)
            control_name=name.replace('Skin_','SkinControl_')
            Image.fromarray(control,'RGBA').save(output/control_name)
            authored.append({'output':(output/control_name).relative_to(ROOT).as_posix(),'sha256':hashlib.sha256((output/control_name).read_bytes()).hexdigest(),
                'sourceContext':'makehuman:system/'+path.relative_to(source).as_posix(),
                'authorship':'Project-authored metallic-zero/smoothness control: matte cheeks, subtle nose/lid/ear variation and smoother lips; shared hm08 UV landmarks and source lip colour.'})
    for path in sorted(admitted):
        dest=raw/'system'/path.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
    # Retain truthful receipts for superseded pilot textures still present in
    # the authoring set; no old receipt may cover different current bytes.
    known={r['output'] for r in receipts}
    for old in prior.get('derived',[]):
        q=ROOT/old['output']
        if old['output'] not in known and q.is_file() and hashlib.sha256(q.read_bytes()).hexdigest()==old['sha256']:receipts.append(old)
    raw_manifest={'schemaVersion':1,'license':'CC0-1.0','mpfbCommit':manifest['mpfbCommit'],
        'systemPackSha256':manifest['systemPackSha256'],'sourceURL':'https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html',
        'derived':receipts,'projectAuthored':authored,'admitted':[{'path':q.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
            for q in sorted(raw.rglob('*')) if q.is_file() and q.name!='admission.json']}
    (raw/'admission.json').write_bytes((json.dumps(raw_manifest,indent=2)+'\n').encode())
    print('HUMAN_TEXTURES',len(receipts),'CC0_SOURCE_FILES',len(raw_manifest['admitted']))

if __name__=='__main__':main()
