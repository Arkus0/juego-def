using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;

namespace JuegoDef.Characters.Editor
{
    /// <summary>Small recipe-to-prefab adapter; Blender owns mesh fitting, Unity owns serialization.</summary>
    public static class CharFactory
    {
        public const string Root = "Assets/JuegoDef/Derived/CHAR";
        public const string UAL = "Assets/ThirdParty/Quaternius/UAL1/UAL1.fbx";
        public static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "../../.."));
        [Serializable] public class Recipe { public string id, role, body, profile, top, bottom, hair, accessory, skin, palette,footwear,headwear,brows,fabric,shoeFabric,pose,workPose,eyes,face,fit,qualityTier,complexion,headForm,hairStyle,garmentPattern; public float height,stanceBias,slouch; public string[] tags,facial,extras; }
        [Serializable] public class Palette { public string id, top, bottom, accent, hair, shoes, outer, cap, detail, beard, skin, eyes, apron; }
        [Serializable] public class Manifest { public int schemaVersion; public Recipe[] recipes; public Palette[] palettes; }
        [Serializable] public class BuildRow { public string id,exportSha256;public Recipe recipe; }
        [Serializable] public class BuildEvidence { public BuildRow[] variants;public CharValidation.Identity[] inputs; }
        public static Manifest Read() => JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(Repo,"Docs/asset_catalog/char_recipes.json")));
        public static bool ValidMaterial(Material material)
        {
            if(material==null||material.shader==null||!material.shader.isSupported)return false;
            if(material.shader.name=="Universal Render Pipeline/Lit")return true;
            return material.shader==AssetDatabase.LoadAssetAtPath<Shader>("Assets/JuegoDef/Characters/Shaders/CharSkin.shader")
                && material.name.EndsWith("-skin",StringComparison.Ordinal)
                && material.GetTexture("_BaseMap")!=null && !material.IsKeywordEnabled("_SPECULAR_SETUP")
                && material.GetFloat("_WorkflowMode")>.5f;
        }
        public static void Folder(string path) { Directory.CreateDirectory(path); AssetDatabase.Refresh(); }

        [MenuItem("Tools/JuegoDef/Characters/Build seed prefabs")]
        public static void Build()
        {
            if (EditorApplication.isPlaying) throw new InvalidOperationException("Stop Play Mode before building prefabs");
            var manifest=Read();
            var build=JsonUtility.FromJson<BuildEvidence>(File.ReadAllText(Path.Combine(Repo,"Docs/evidence/WP-PROD-CHAR-01/build_inventory.json")));
            if(build.inputs==null||build.variants.Length!=manifest.recipes.Length)throw new InvalidOperationException("Missing/full Blender batch required");
            foreach(var input in build.inputs)
                if(JDAnimationFactory.Hash(Path.Combine(Repo,input.path))!=input.sha256)throw new InvalidOperationException("Stale Blender build input "+input.path);
            foreach(var recipe in manifest.recipes)
            {
                var row=build.variants.Single(v=>v.id==recipe.id);
                if(JsonUtility.ToJson(row.recipe)!=JsonUtility.ToJson(recipe)||JDAnimationFactory.Hash(Root+"/Models/"+recipe.id+".fbx")!=row.exportSha256)
                    throw new InvalidOperationException("Stale Blender recipe/model "+recipe.id);
            }
            if(manifest.recipes.Select(r=>r.id).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=manifest.recipes.Length)
                throw new InvalidOperationException("Duplicate recipe identity");
            Folder(Root+"/Prefabs"); Folder(Root+"/Materials"); Folder("Assets/JuegoDef/Characters");
            JDAnimationFactory.ApplyPresets();
            var controller=Controller();
            foreach(var recipe in manifest.recipes)
            {
                if(!System.Text.RegularExpressions.Regex.IsMatch(recipe.id,"^[a-z][a-z0-9-]{2,40}$"))throw new InvalidOperationException("Unsafe recipe id");
                string path=Root+"/Models/"+recipe.id+".fbx";
                var importer=AssetImporter.GetAtPath(path) as ModelImporter;
                if(importer==null)throw new InvalidOperationException("Missing derived model "+path);
                // A .meta from an earlier build keeps its old bone description and Unity reports a rig mis-match.
                if(importer.animationType!=ModelImporterAnimationType.Generic){importer.animationType=ModelImporterAnimationType.Generic;importer.SaveAndReimport();importer=AssetImporter.GetAtPath(path) as ModelImporter;}
                importer.animationType=ModelImporterAnimationType.Human;
                importer.avatarSetup=ModelImporterAvatarSetup.CreateFromThisModel;
                importer.importAnimation=false; importer.importBlendShapes=true; importer.isReadable=true; importer.bakeAxisConversion=true;
                importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
                importer.SaveAndReimport();
                var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);
                var instance=(GameObject)PrefabUtility.InstantiatePrefab(asset);
                try
                {
                    instance.name=recipe.id;
                    var animator=instance.GetComponent<Animator>();
                    if(animator==null || animator.avatar==null || !animator.avatar.isValid || !animator.avatar.isHuman)
                        throw new InvalidOperationException("Invalid Humanoid avatar "+recipe.id);
                    animator.runtimeAnimatorController=CharPosture.Controller(recipe,controller);animator.applyRootMotion=false;
                    animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
                    var palette=manifest.palettes.Single(p=>p.id==recipe.palette);
                    foreach(var renderer in instance.GetComponentsInChildren<SkinnedMeshRenderer>())
                    {
                        renderer.sharedMaterials=renderer.sharedMaterials.Select(m=>ResolveMaterial(m.name,recipe,palette)).ToArray();
                        renderer.updateWhenOffscreen=true;
                        if(renderer.name.StartsWith("HumanBrows")||renderer.name.StartsWith("HumanLashes")||renderer.name.StartsWith("HumanEyes"))
                            renderer.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
                    }
                    var presentation=instance.GetComponent<JuegoDef.Characters.NpcPresentation>()??instance.AddComponent<JuegoDef.Characters.NpcPresentation>();
                    uint personSeed=2166136261;foreach(char c in recipe.id)personSeed=(personSeed^c)*16777619;
                    presentation.seed=unchecked((int)personSeed);
                    presentation.face=instance.GetComponentsInChildren<SkinnedMeshRenderer>().Single(s=>s.name.StartsWith("HumanHead",StringComparison.Ordinal));
                    presentation.eyes=instance.GetComponentsInChildren<SkinnedMeshRenderer>().Single(s=>s.name.StartsWith("HumanEyes",StringComparison.Ordinal));
                    PrefabUtility.SaveAsPrefabAsset(instance,Root+"/Prefabs/"+recipe.id+".prefab");
                }
                finally { UnityEngine.Object.DestroyImmediate(instance); }
            }
            AssetDatabase.SaveAssets();
            Debug.Log("CHAR_PREFABS_BUILT "+manifest.recipes.Length);
        }

        struct Fabric { public string albedo, normal; public float scale, smooth, bump; }
        // Garment UVs are world-scale (1 unit = 1 m, Tools/char_build.py fabric_uvs), so each fabric has ONE weave size
        // for the whole cast: tiles per metre of the 128 px grain tile. Smoothness is a property of the fabric, not the slot.
        static readonly Dictionary<string,float> TilesPerMetre=new Dictionary<string,float>{{"Cloth",22f},{"Knit",11f},{"Canvas",15f},{"Denim",18f},{"Leather",14f}};
        static readonly Dictionary<string,float> FabricSmoothness=new Dictionary<string,float>{{"Cloth",.08f},{"Knit",.04f},{"Canvas",.10f},{"Denim",.08f},{"Leather",.30f}};
        static Fabric F(string name,float bump=1f)
            => new Fabric{albedo="T_CHAR_"+name+".png",normal="T_CHAR_"+name+"_N.png",scale=TilesPerMetre[name],smooth=FabricSmoothness[name],bump=bump};
        static Fabric TopFabric(Recipe r)
        {
            switch(r.fabric)
            {
                case "denim":return F("Denim",.5f);
                case "leather":return F("Leather",.5f);
                case "canvas":return F("Canvas",.5f);
                case "knit":return F("Knit",.6f);
                case "cotton":return F("Cloth",.4f);
            }
            switch(r.top)
            {
                case "sweater":case "cardigan":case "hoodie":return F("Knit",.6f);
                case "light_coat":return F("Canvas",.5f);
                default:return F("Cloth",.4f);
            }
        }
        // Mirrors Docs/asset_catalog/char_compatibility.json > skinTones (tints multiply the derived pale atlas).
        static string SkinTint(string tone)
        {
            switch(tone)
            {
                case "pale":return "FFFFFF";
                case "fair":return "F3EDE8";
                case "olive":return "E5D3C2";
                case "weathered":return "EDC2B8";
                case "tan":return "D2B3A0";
                case "brown":return "A89080";
            }
            throw new InvalidOperationException("Unknown skin tone "+tone);
        }
        static string SkinTexture(Recipe r)
        {
            if(r.body!="regular_male"&&r.body!="regular_female"&&r.body!="superhero_male"&&r.body!="superhero_female")throw new InvalidOperationException("No skin atlas for body "+r.body);
            // Face variants (Tools/char_skin.py): same atlas with make-up, grooming or age lines painted over.
            return "T_CHAR_Skin_"+r.body+(string.IsNullOrEmpty(r.face)||r.face=="default"?"":"_"+r.face)+".jpg";
        }
        static string SkinNormal(Recipe r)
        {
            switch(r.body)
            {
                case "regular_male":return "T_Regular_Male_Normal.png";
                case "regular_female":return "T_Regular_Female_Normal.png";
                case "superhero_female":return "T_Superhero_Female_Normal.png";
                case "superhero_male":return "T_Superhero_Male_Normal.png";
            }
            return null;
        }
        static string Hex(string preferred,string fallback)=>string.IsNullOrEmpty(preferred)?fallback:preferred;
        static Color Parse(string hex){Color c;ColorUtility.TryParseHtmlString("#"+hex,out c);return c;}
        static Texture2D LoadTexture(string fileName,bool normal)
        {
            bool authored=fileName.StartsWith("T_CHAR_",StringComparison.Ordinal);
            string texturePath=(fileName.StartsWith("T_CHAR_Skin_",StringComparison.Ordinal)||fileName.StartsWith("T_CHAR_Eye_",StringComparison.Ordinal)||fileName.StartsWith("T_CHAR_Human_",StringComparison.Ordinal)?"Assets/JuegoDef/Derived/CHAR/Textures/":authored?"Assets/JuegoDef/Characters/Textures/":"Assets/ThirdParty/Quaternius/BaseCharacters/Base Characters/Textures/")+fileName;
            var importer=AssetImporter.GetAtPath(texturePath) as TextureImporter;
            if(importer==null)throw new InvalidOperationException("Missing texture importer "+texturePath);
            // ASSET intake supplies GUID-only metadata; Unity inferred some atlases as cubemaps.
            // Bounded import configuration; original PNG bytes remain untouched.
            var wantType=normal?TextureImporterType.NormalMap:TextureImporterType.Default;
            bool linear=fileName.StartsWith("T_CHAR_Human_AO_",StringComparison.Ordinal)||fileName.StartsWith("T_CHAR_Human_SkinControl_",StringComparison.Ordinal);
            bool dirty=importer.textureShape!=TextureImporterShape.Texture2D||importer.textureType!=wantType||(authored&&importer.wrapMode!=TextureWrapMode.Repeat)||(!normal&&importer.sRGBTexture==linear);
            if(dirty)
            {
                importer.textureShape=TextureImporterShape.Texture2D;
                importer.textureType=wantType;
                if(!normal)importer.sRGBTexture=!linear;
                if(authored){importer.wrapMode=TextureWrapMode.Repeat;importer.filterMode=FilterMode.Bilinear;}
                importer.SaveAndReimport();
            }
            var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
            if(tex==null)throw new InvalidOperationException("Missing texture "+texturePath);
            return tex;
        }

        [Serializable] class HumanHeadSource { public string id,sex,skin,hair; }
        [Serializable] class HumanHeadSources { public HumanHeadSource[] heads; }
        static HumanHeadSource HumanHead(string id)
        {
            var path=Path.Combine(Repo,"Art/Characters/HumanHeads/source_manifest.json");
            var entry=JsonUtility.FromJson<HumanHeadSources>(File.ReadAllText(path)).heads.FirstOrDefault(h=>h.id==id);
            if(entry==null)throw new InvalidOperationException("Missing admitted human head "+id);
            return entry;
        }
        static Material ResolveMaterial(string slot,Recipe r,Palette p)
        {
            var semantic=slot.Split('.')[0];
            string identity=semantic,hex="FFFFFF",albedo=null,normal=null;
            float smooth=.08f,scale=1f,bump=1f;
            bool hasApron=r.accessory=="apron"||(r.extras!=null&&Array.IndexOf(r.extras,"apron")>=0);
            Fabric f;
            switch(semantic)
            {
                case "human_skin":hex=Hex(p.skin,SkinTint(r.skin));identity=r.palette+"-human-skin";albedo="T_CHAR_Human_Skin_"+HumanHead(r.headForm).skin+".png";smooth=.30f;break;
                case "human_eye":identity=r.palette+"-human-eye";albedo="T_CHAR_Human_Eye_"+(r.eyes??"brown")+".png";smooth=.52f;break;
                case "human_hair":hex=p.hair;identity=r.palette+"-human-hair";albedo="T_CHAR_Human_Hair_"+HumanHead(r.headForm).hair+".png";smooth=.10f;break;
                case "human_brow":hex=ColorUtility.ToHtmlStringRGB(Parse(p.hair)*1.6f);identity=r.palette+"-human-brow";albedo="T_CHAR_Human_Brow_"+HumanHead(r.headForm).sex+".png";smooth=.05f;break;
                case "human_lash":hex=p.hair;identity=r.palette+"-human-lash";albedo="T_CHAR_Human_Lash_standard.png";smooth=.05f;break;
                case "human_facial":hex=ColorUtility.ToHtmlStringRGB(Parse(Hex(p.beard,p.hair))*1.5f);identity=r.palette+"-human-facial";albedo="T_CHAR_Human_Facial_standard.png";smooth=.07f;break;
                case "top":f=TopFabric(r);hex=p.top;identity=r.palette+"-top";albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;break;
                case "bottom":
                    f=r.bottom=="work"?F("Canvas",.5f):(r.bottom=="skirt"||r.bottom=="long_skirt")?F("Cloth",.4f):F("Denim",.5f);
                    hex=p.bottom;identity=r.palette+"-bottom";albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;break;
                case "accent":f=hasApron?F("Canvas",.5f):F("Cloth",.4f);hex=p.accent;identity=r.palette+"-accent";albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;break;
                case "apron":
                    hex=Hex(p.apron,p.accent);identity=r.palette+"-apron";
                    if(r.shoeFabric=="rubber")smooth=.42f;   // fish-market PVC apron: smooth plastic, no weave
                    else{f=F("Canvas",.4f);albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;}
                    break;
                case "outer":f=F("Cloth",.4f);hex=Hex(p.outer,p.accent);identity=r.palette+"-outer";albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;break;
                case "cap":f=(r.headwear=="beanie"||r.headwear=="beret")?F("Knit",.6f):F("Cloth",.4f);hex=Hex(p.cap,p.top);identity=r.palette+"-cap";albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;break;
                case "detail":f=F("Knit",.6f);hex=Hex(p.detail,ColorUtility.ToHtmlStringRGB(Parse(p.top)*.7f));identity=r.palette+"-detail";albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;break;
                case "hair":hex=p.hair;identity=r.palette+"-hair";smooth=.12f;albedo="T_CHAR_Hair.png";normal="T_CHAR_Hair_N.png";bump=.2f;break;
                case "beard":hex=Hex(p.beard,p.hair);identity=r.palette+"-beard";smooth=.14f;break;
                case "shoes":
                    hex=p.shoes;identity=r.palette+"-shoes";
                    if(r.shoeFabric!="rubber"){f=F("Leather",.45f);albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;}
                    else smooth=.45f;
                    break;
                case "trim":
                    f=F("Cloth",.4f);hex=ColorUtility.ToHtmlStringRGB(Parse(p.top)*.70f);identity=r.palette+"-trim";
                    albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;break;
                case "eyes":hex="FFFFFF";identity=r.palette+"-eyes";albedo="T_CHAR_Eye_"+(string.IsNullOrEmpty(r.eyes)?"brown":r.eyes)+".png";smooth=.28f;break;
                case "lid":
                    var lidTint=Parse(SkinTint(r.skin));hex=ColorUtility.ToHtmlStringRGB(new Color(.94f*lidTint.r,.74f*lidTint.g,.62f*lidTint.b));
                    identity=r.palette+"-lid";smooth=.08f;break;
                case "hem":f=F("Cloth",.4f);hex=ColorUtility.ToHtmlStringRGB(Parse(p.bottom)*.80f);identity=r.palette+"-hem";albedo=f.albedo;normal=f.normal;scale=f.scale;smooth=f.smooth;bump=f.bump;break;
                case "reflective":hex="D8D9CA";smooth=.32f;break;
                case "sole":hex="BEBFB5";smooth=.20f;break;
                default:
                    if(!semantic.StartsWith("skin_"))throw new InvalidOperationException("Unknown material slot "+slot);
                    hex=Hex(p.skin,SkinTint(r.skin));identity=r.palette+"-skin";albedo=SkinTexture(r);normal=SkinNormal(r);smooth=.10f;bump=.18f;
                    break;
            }
            string path=Root+"/Materials/"+identity+".mat";
            var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(mat==null){mat=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(mat,path);}
            bool skinMaterial=semantic.StartsWith("skin_",StringComparison.Ordinal);
            mat.shader=Shader.Find(skinMaterial?"JuegoDef/Characters/Skin":"Universal Render Pipeline/Lit");
            if(mat.shader==null)throw new InvalidOperationException("Missing character shader");
            if(skinMaterial)
            {
                // Seed from stable recipe identity; do not use randomized string.GetHashCode.
                uint seed=2166136261;foreach(char ch in r.id)seed=(seed^ch)*16777619;
                var complexions=new[]{"clear","freckles","weathered","age_spots","mole","scar"};
                int complexion=Array.IndexOf(complexions,r.complexion??"clear");
                if(complexion<0)throw new InvalidOperationException("Unknown complexion "+r.id);
                mat.DisableKeyword("_SPECULAR_SETUP");
                mat.SetColor("_SpecColor",new Color((seed%10000)/10000f,complexion/5f,r.qualityTier=="conversation"?.18f:.12f,r.face=="older"?.9f:r.face=="mature"?.45f:.1f));
            }
            Color color;if(!ColorUtility.TryParseHtmlString("#"+hex,out color))throw new InvalidOperationException("Bad palette color");
            mat.SetColor("_BaseColor",color);
            mat.SetFloat("_Smoothness",smooth);
            mat.SetFloat("_Metallic",0);
            mat.SetFloat("_Cull",0); // thin straps/skirt surfaces have a visible reverse face
            bool cutout=semantic=="human_eye"||semantic=="human_hair"||semantic=="human_brow"||semantic=="human_lash"||semantic=="human_facial";
            mat.SetFloat("_AlphaClip",cutout?1:0);mat.SetFloat("_Cutoff",.35f);
            if(cutout){mat.EnableKeyword("_ALPHATEST_ON");mat.renderQueue=2450;mat.SetOverrideTag("RenderType","TransparentCutout");}
            else{mat.DisableKeyword("_ALPHATEST_ON");mat.renderQueue=-1;mat.SetOverrideTag("RenderType","Opaque");}
            if(albedo!=null)
            {
                mat.SetTexture("_BaseMap",LoadTexture(albedo,false));
                mat.SetTextureScale("_BaseMap",Vector2.one*scale);
            }
            else mat.SetTexture("_BaseMap",null);
            if(normal!=null)
            {
                mat.SetTexture("_BumpMap",LoadTexture(normal,true));
                mat.SetTextureScale("_BumpMap",Vector2.one*scale);
                mat.SetFloat("_BumpScale",bump);
                mat.EnableKeyword("_NORMALMAP");
            }
            else{mat.SetTexture("_BumpMap",null);mat.DisableKeyword("_NORMALMAP");}
            if(semantic=="human_skin")
            {
                mat.SetFloat("_Cull",2);
                mat.SetTexture("_MetallicGlossMap",LoadTexture("T_CHAR_Human_SkinControl_"+HumanHead(r.headForm).skin+".png",false));
                mat.EnableKeyword("_METALLICSPECGLOSSMAP");mat.SetFloat("_SmoothnessTextureChannel",0);
                var ao="T_CHAR_Human_AO_"+r.headForm+".png";
                if(File.Exists(Root+"/Textures/"+ao))
                {
                    mat.SetTexture("_OcclusionMap",LoadTexture(ao,false));mat.SetFloat("_OcclusionStrength",.60f);mat.EnableKeyword("_OCCLUSIONMAP");
                }
            }
            EditorUtility.SetDirty(mat);return mat;
        }

        static AnimatorController Controller()
        {
            const string path="Assets/JuegoDef/Characters/CivilianFitPreview.controller";
            var controller=AssetDatabase.LoadAssetAtPath<AnimatorController>(path);
            // Civilian posture derivatives of the admitted clips (relaxed hands, hip-width stance); see CharPosture.
            CharPosture.BuildAll();
            var idle=CharPosture.Load("ual1:idle_loop");
            var walk=CharPosture.Load("ual1:walk_loop");
            var talk=CharPosture.Load("ual1:idle_talking_loop");
            if(!idle.humanMotion||!walk.humanMotion)throw new InvalidOperationException("Run accepted UAL import wrapper first");
            if(controller==null)controller=AnimatorController.CreateAnimatorControllerAtPath(path);
            var machine=controller.layers[0].stateMachine;
            foreach(var pair in new[]{new KeyValuePair<string,AnimationClip>("Idle",idle),new KeyValuePair<string,AnimationClip>("Walk",walk),new KeyValuePair<string,AnimationClip>("Talking",talk)})
            {
                var state=machine.states.Select(s=>s.state).FirstOrDefault(s=>s.name==pair.Key)??machine.AddState(pair.Key);
                state.motion=pair.Value;if(pair.Key=="Idle")machine.defaultState=state;
            }
            EditorUtility.SetDirty(controller);
            return controller;
        }

        [MenuItem("Tools/JuegoDef/Characters/Create fit preview scene")]
        public static void Scene()
        {
            if(EditorApplication.isPlaying)throw new InvalidOperationException("Stop Play Mode first");
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var ground=GameObject.CreatePrimitive(PrimitiveType.Plane);ground.name="Fit review ground";ground.transform.localScale=new Vector3(3,1,3);
            var groundMat=new Material(Shader.Find("Universal Render Pipeline/Lit"));groundMat.SetColor("_BaseColor",new Color(.43f,.43f,.40f));
            string groundPath="Assets/JuegoDef/Characters/FitGround.mat";
            var old=AssetDatabase.LoadAssetAtPath<Material>(groundPath);
            if(old==null){AssetDatabase.CreateAsset(groundMat,groundPath);old=groundMat;}else UnityEngine.Object.DestroyImmediate(groundMat);
            ground.GetComponent<Renderer>().sharedMaterial=old;
            var light=new GameObject("Daylight").AddComponent<Light>();light.type=LightType.Directional;light.intensity=2.2f;light.color=new Color(1f,.94f,.84f);light.shadows=LightShadows.Soft;light.transform.rotation=Quaternion.Euler(45,-35,0);
            RenderSettings.ambientMode=UnityEngine.Rendering.AmbientMode.Flat;RenderSettings.ambientLight=new Color(.70f,.71f,.68f);
            var camera=new GameObject("Third-person review camera").AddComponent<Camera>();camera.tag="MainCamera";
            camera.transform.position=new Vector3(2.8f,1.75f,9.5f);camera.transform.LookAt(new Vector3(0,1,0));camera.fieldOfView=50;
            camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.43f,.50f,.54f);
            var recipes=Read().recipes;
            camera.transform.position=new Vector3(0,2.8f,Mathf.Max(9.5f,recipes.Length*1.4f));
            camera.transform.LookAt(new Vector3(0,.95f,0));
            for(int i=0;i<recipes.Length;i++)
            {
                var go=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Root+"/Prefabs/"+recipes[i].id+".prefab"));
                go.transform.position=new Vector3((i-(recipes.Length-1)/2f)*1.2f,0,0);
            }
            Folder("Assets/JuegoDef/Scenes/CHAR");
            EditorSceneManager.SaveScene(scene,"Assets/JuegoDef/Scenes/CHAR/CivilianFitPreview.unity");
            AssetDatabase.SaveAssets();Debug.Log("CHAR_PREVIEW_SCENE_READY");
        }
    }
}
