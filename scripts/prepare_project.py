from pathlib import Path
import shutil, json, hashlib, zipfile

workspace = Path(__file__).resolve().parents[3]
root = Path(__file__).resolve().parents[1]
out = workspace / 'output'
assets = root / 'vystupy'
assets.mkdir(exist_ok=True)
for src in out.iterdir():
    if src.name.startswith('BD_STUROVA_projekt'): continue
    dest = assets / src.name
    if src.is_dir(): shutil.copytree(src, dest, dirs_exist_ok=True)
    else: shutil.copyfile(src, dest)
sources = root / 'podklady'
sources.mkdir(exist_ok=True)
for pattern in ('*.dwg', '*.pdf'):
    for src in (workspace/'tmp/foundations').glob(pattern):
        shutil.copyfile(src, sources/src.name)

questions = [
    'P31 a P41: Aká je presná spodná a horná výšková kóta?',
    'T01 a T02: Kde začínajú a končia stupne medzi −3,870 a −3,670 m?',
    'Rez C–C: Ktoré základy sú priamo rezané a ktoré sú v pohľade za rezom?',
    'Obvodové krčky: Aký je úplný priebeh, prierez a výškové členenie?',
    'Schodiskové jadrá: Kde prechádzajú úrovne −3,450, −3,670 a −3,900 m?',
    'N11, N12, N23, N27, N55, N59, N60, N64 a N75: Aké sú kóty a napojenia?',
    'Sú všetky styky pätiek, krčkov a pásov zhodné s pôdorysmi aj rezmi?',
    'Je poloha a výškové pripojenie ±0,000 = 263,650 m overené voči DMR?'
]
metadata = {'layer_id':'zaklady','name':'VRSTVA ZÁKLADOV','version':'0.2',
    'trust_percent':65,'trust_method':'Orientačný odborný odhad; nie štatistická presnosť ani percento overených prvkov.',
    'placement':'Lokálne CAD súradnice; osadenie do DMR neoverené.',
    'model':'vystupy/BD_STUROVA_zaklady_v02/model_data.json','questions':questions}
(root/'vrstva_zakladov.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
s=(out/'BD_STUROVA_interaktivny_teren.html').read_text()
s=s.replace('<title>BD Štúrova · interaktívny terén</title>','<title>BD Štúrova · projektové vrstvy</title>')
panel='''<div class="line"><b>VRSTVA ZÁKLADOV</b><button id="foundationButton" onclick="showFoundation(true)" aria-pressed="false" style="width:100%;text-align:left;font-weight:bold;border-left:5px solid #bc8735">▰ ZÁKLADY <span class="badge">65 %</span></button><button id="terrainButton" onclick="showFoundation(false)" aria-pressed="true">Terén a vrstevnice</button><p class="note">v0.2 · pracovná miera dôvery 65 %. Odhad, nie presnosť rozmerov. Základy majú samostatný lokálny pohľad; osadenie do DMR ešte nie je overené.</p><details><summary>Otvorené otázky (8)</summary><ol class="note">'''+''.join('<li>'+q+'</li>' for q in questions)+'''</ol></details><p class="note"><a href="vystupy/BD_STUROVA_zaklady_v02/zaklady_v02.glb" download>GLB</a> · <a href="vystupy/BD_STUROVA_zaklady_v02/zaklady_v02.obj" download>OBJ</a> · <a href="vystupy/BD_STUROVA_zaklady_v02/prvky_a_vysky.csv" download>Prvky CSV</a></p></div>'''
s=s.replace('<div class="line"><b>Zvýraznenie výšok</b>',panel+'<div class="line"><b>Zvýraznenie výšok</b>')
s=s.replace('<section id="view">','<section id="view"><iframe id="foundationFrame" title="VRSTVA ZÁKLADOV – lokálny 3D model" src="vystupy/BD_STUROVA_zaklady_v02/zaklady_v02.html" style="display:none;position:absolute;inset:0;width:100%;height:100%;border:0;z-index:2;background:#f8faf7"></iframe>')
extra='''<script>
function foundationPlot(){const f=document.getElementById('foundationFrame');return {w:f.contentWindow,g:f.contentDocument.querySelector('.plotly-graph-div')};}
function showFoundation(on){
 document.getElementById('foundationFrame').style.display=on?'block':'none';
 document.getElementById('foundationButton').setAttribute('aria-pressed',String(on));
 document.getElementById('terrainButton').setAttribute('aria-pressed',String(!on));
 document.getElementById('exag').disabled=on;
 for(const id of ['surface','contours','drawing'])document.getElementById(id).disabled=on;
 if(on){const p=foundationPlot();if(p.g&&p.w.Plotly)p.w.Plotly.Plots.resize(p.g);}else Plotly.Plots.resize(gd);
}
const terrainZoom=zoom,terrainReset=resetView,terrainTop=topView;
function foundationsActive(){return document.getElementById('foundationButton').getAttribute('aria-pressed')==='true';}
zoom=function(f){if(!foundationsActive())return terrainZoom(f);const p=foundationPlot();if(!p.g?._fullLayout)return;const c=JSON.parse(JSON.stringify(p.g._fullLayout.scene.camera));for(const k of ['x','y','z'])c.eye[k]*=f;p.w.Plotly.relayout(p.g,{'scene.camera':c});};
resetView=function(){if(!foundationsActive())return terrainReset();const p=foundationPlot();if(p.g)p.w.Plotly.relayout(p.g,{'scene.camera':{eye:{x:1.3,y:-1.5,z:.9},up:{x:0,y:0,z:1},projection:{type:'perspective'}}});};
topView=function(){if(!foundationsActive())return terrainTop();const p=foundationPlot();if(p.g)p.w.Plotly.relayout(p.g,{'scene.camera':{eye:{x:0,y:0,z:2.2},up:{x:0,y:1,z:0},projection:{type:'orthographic'}}});};
</script>'''
s=s.replace('</html>',extra+'</html>')
(root/'index.html').write_text(s)
(root/'README.md').write_text('''# BD Štúrova – projektové vrstvy

Otvorte `index.html`. Ľavý panel obsahuje ZÁKLADY · 65 % a prepnutie späť na terén, vrstevnice a situáciu. Otáčanie a priblíženie sú dostupné v oboch pohľadoch. Pre úplnú funkciu ovládania vnoreného pohľadu spustite v tomto adresári `python -m http.server 8000` a otvorte http://localhost:8000.

## Obsah
- `vystupy/`: všetky doteraz dostupné finálne výstupy, obrázky, profily, geologická interpretácia, HTML prehliadače, GIS vrstvy a archívy v01/v02.
- `vystupy/BD_STUROVA_vrstvy/`: DMR 6.0, ortofoto, situácia, kontrolné body, transformácia a QGIS projekt.
- `vystupy/BD_STUROVA_zaklady_v02/`: aktuálne základové prvky GLB/OBJ, geometria a atribúty JSON/CSV, generátor, zoznam otvorených detailov.
- `podklady/`: dostupné pôvodné DWG pôdorysov a rezov, PDF pôdorysov, všetkých šiestich rezov a pohľadov.
- `vrstva_zakladov.json`: názov vrstvy, pracovná dôvera a osem otvorených otázok.
- `manifest.json`: zoznam súborov a kontrolné súčty SHA-256.

## Stav
VRSTVA ZÁKLADOV v0.2: pracovná dôvera 65 %, orientačný odhad, nie štatistická presnosť. 110 objemových prvkov. 11 nedoriešených oblastí a P31/P41 bez jednoznačných výšok. Nie je to dokončený IFC BIM model. Geometria zostáva nezmenená.

Základy sú v lokálnych CAD súradniciach, ±0,000 = 263,650 m. Nie sú zlúčené s DMR do spoločnej scény: ich georeferencovanie ešte nie je overené. Situácia na teréne má orientačné osadenie s RMSE 1,27 m; výškový systém DMR nie je potvrdený. Geologický obrázok je interpretácia, nie výsledok IGP.

Zdrojový projekt: https://drive.google.com/drive/folders/1h1nt2uwKaRwJnOPqug7kXpLQropPfxNh
PDF dokumentácia: https://drive.google.com/drive/folders/17O5_RcX8CYjAMJJFUV-a9_uU0jLPq2kv

GitHub: balík pripravený pre nový súkromný repozitár BD_STUROVA; vytvorenie repozitára čaká na dostupný spôsob prístupu. Žiadne súbory zatiaľ neboli odoslané na GitHub.
''')
manifest=[]
for p in sorted(root.rglob('*')):
    if p.is_file() and p.name!='manifest.json':
        manifest.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
zip_path=out/'BD_STUROVA_projekt_GitHub.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file():z.write(p,Path('BD_STUROVA')/p.relative_to(root))
print(json.dumps({'files':len(manifest)+1,'zip':str(zip_path),'bytes':zip_path.stat().st_size}))
