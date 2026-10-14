import json,csv,shutil,zipfile
from pathlib import Path
import numpy as np,trimesh
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Patch
import plotly.graph_objects as go
out=Path('output/BD_STUROVA_zaklady_v01');out.mkdir(exist_ok=True)
base=Path('tmp/foundations');ps=json.load(open(base/'polygons.json'));ns=json.load(open(base/'necks.json'));es=json.load(open(base/'aligned.json'));origin=np.array([4980696.,-1499500.]);models=[];parents=[]
cols={-5.0:'#8da99a',-5.4:'#5e82a2',-5.8:'#a77a61'}
for item in ps:
 if item['id'] in [24,31,41]:continue
 p=Polygon(item['xy'],item['holes']);levels=[float(v.replace(',','.'))for v in item['labels']];bottom=min(levels);top=round(bottom+.8,3)
 assert bottom in cols
 ident=f"F{item['id']:02d}";parents.append((p,bottom,top,ident,item))
 models.append(dict(id=ident,kind='patka' if p.area<15 else 'pas_sustava',polygon=p,zmin=bottom,zmax=top,status='kota_v_podoryse',color=cols[bottom],parent=''))
toptexts=[]
for e in es:
 if e['type']=='TEXT' and e.get('text') in ['-3,450','-3,670','-3,870','-3,900']:
  q=(np.array([e['startPoint']['x'],e['startPoint']['y']])-origin)/1000;toptexts.append((Point(q),float(e['text'].replace(',','.'))))
foot=unary_union([v[0]for v in parents]);selected=[]
for n in ns:
 p=Polygon(n['xy'],n['holes'])
 if p.area<50 and p.intersection(foot).area/p.area>.95:selected.append(p)
# Merge shared drawing boundaries; keep elevation changes at footing boundaries.
merged=unary_union(selected);counter=0
for p,bottom,top,pid,item in parents:
 cut=merged.intersection(p)
 parts=list(cut.geoms) if hasattr(cut,'geoms') else [cut]
 for q in parts:
  if q.geom_type!='Polygon' or q.area<.05:continue
  candidates=[(q.distance(pt),height)for pt,height in toptexts if p.buffer(.5).contains(pt)]
  if not candidates:continue
  candidates.sort();dist,zhi=candidates[0]
  nearby={v for d,v in candidates if d<dist+.15}
  status='predbezna_kota_overit' if dist>1 or len(nearby)>1 or q.area>2 else 'kota_priradena_z_podorysu'
  counter+=1;models.append(dict(id=f'K{counter:02}',kind='krcok_stlpa' if q.area<1 else 'zakladovy_tram',polygon=q,zmin=top,zmax=zhi,status=status,color='#d9bc78' if status.startswith('predbezna') else '#d2d9de',parent=pid))
scene=trimesh.Scene();meta=[];traces=[];faces3d=[]
for m in models:
 mesh=trimesh.creation.extrude_polygon(m['polygon'],m['zmax']-m['zmin'],engine='earcut');mesh.apply_translation([0,0,m['zmin']]);color=matplotlib.colors.to_rgba(m['color']);mesh.visual.face_colors=np.array(color)*255
 assert mesh.is_watertight and mesh.volume>0
 scene.add_geometry(mesh,node_name=m['id'],geom_name=m['id']);vertices=mesh.vertices;faces=mesh.faces
 meta.append({k:v for k,v in m.items()if k not in ['polygon','color']}|dict(xy=list(m['polygon'].exterior.coords),holes=[list(r.coords)for r in m['polygon'].interiors],area_m2=round(m['polygon'].area,5),volume_m3=round(mesh.volume,5),zmin_absolute=round(263.65+m['zmin'],3),zmax_absolute=round(263.65+m['zmax'],3)))
 traces.append(go.Mesh3d(x=vertices[:,0],y=vertices[:,1],z=vertices[:,2],i=faces[:,0],j=faces[:,1],k=faces[:,2],color=m['color'],flatshading=True,name=m['id'],hovertemplate=f"{m['id']} · {m['kind']}<br>{m['zmin']:.3f} → {m['zmax']:.3f} m<br>{m['status']}<extra></extra>",showlegend=False))
 faces3d.append((vertices[faces],m['color']))
# OBJ is Z up, metres, relative to project zero.
scene.export(str(out/'zaklady_v01.obj'))
# glTF uses Y up; bake transform while preserving metre units.
gltf=scene.copy();gltf.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0]));gltf.export(str(out/'zaklady_v01.glb'))
json.dump(dict(project_zero=263.65,units='m',cad_origin_mm=origin.tolist(),CD_shift_x_mm=-115361.5,crs='local CAD; not georeferenced',elements=meta,unresolved_plan_polygon_ids=[31,41]),open(out/'model_data.json','w'),ensure_ascii=False,indent=2)
with open(out/'prvky_a_vysky.csv','w')as f:
 keys=['id','kind','parent','zmin','zmax','zmin_absolute','zmax_absolute','area_m2','volume_m3','status'];w=csv.DictWriter(f,keys,extrasaction='ignore');w.writeheader();w.writerows(meta)
fig=plt.figure(figsize=(16,10),facecolor='#f8faf7');ax=fig.add_axes([.02,.13,.66,.74],projection='3d');plan=fig.add_axes([.73,.24,.24,.60]);ax.set_facecolor('#f8faf7');plan.set_facecolor('#f8faf7')
for faces,c in faces3d:ax.add_collection3d(Poly3DCollection(faces,facecolor=c,edgecolor='#46525a',linewidth=.16))
for p,b,t,pid,item in parents:
 xy=np.array(p.exterior.coords);plan.fill(xy[:,0],xy[:,1],color=cols[b],alpha=.9);plan.plot(xy[:,0],xy[:,1],color='#4f6057',lw=.45)
 for r in p.interiors:xy=np.array(r.coords);plan.fill(xy[:,0],xy[:,1],color='#f8faf7')
for i in [31,41]:
 xy=np.array(ps[i]['xy']);plan.plot(xy[:,0],xy[:,1],color='#cc4e46',lw=1.3);pt=Polygon(xy).representative_point();plan.text(pt.x,pt.y,'?',color='#cc4e46',ha='center')
ax.set(xlim=(-2,63),ylim=(-2,62),zlim=(-6,-3),xlabel='X [m]',ylabel='Y [m]',zlabel='Relatívna výška [m]');ax.set_box_aspect((62,62,15));ax.view_init(26,-57);ax.tick_params(labelsize=8)
plan.set_aspect('equal');plan.set_title('Pôdorys · farba podľa spodnej kóty',fontsize=11);plan.tick_params(labelsize=8);plan.set_xlabel('X [m]');plan.set_ylabel('Y [m]')
fig.text(.055,.94,'BD ŠTUROVA / ZÁKLADY · MODEL v0.1',fontsize=24,color='#263f31',weight='bold');fig.text(.055,.9,'Geometria z DWG • pásy a pätky 800 mm • krčky a trámy s rozlíšenými výškami',fontsize=12,color='#58695b')
fig.legend(handles=[Patch(color=cols[k],label=f'{k:.3f} m')for k in cols]+[Patch(color='#d2d9de',label='Krčky / trámy'),Patch(color='#d9bc78',label='Horná kóta na kontrolu')],loc='lower center',bbox_to_anchor=(.50,.11),ncol=5,frameon=False)
fig.text(.055,.068,'±0,000 = 263,650 m. Pracovný model v lokálnych súradniciach; zvislé rozmery v obrázku sú zvýraznené.',fontsize=11,color='#58695b')
fig.text(.055,.037,'Červené ? = dve plochy bez jednoznačnej kóty, zatiaľ bez objemu. Schodiskové otvory zostávajú otvorené.',fontsize=10,color='#58695b');fig.savefig(out/'zaklady_v01_nahlad.png',dpi=160)
figp=go.Figure(traces)
for i in [31,41]:
 xy=np.array(ps[i]['xy']);figp.add_trace(go.Scatter3d(x=xy[:,0],y=xy[:,1],z=[-3.2]*len(xy),mode='lines',line=dict(color='#cc4e46',width=5),name=f'Neurčená výška P{i}',hovertemplate='Len 2D obrys; Z = −3,2 je zobrazovacia rovina, nie projektová kóta.<extra></extra>'))
figp.update_layout(title='BD Šturova · základové konštrukcie v0.1',paper_bgcolor='#f8faf7',margin=dict(l=0,r=0,b=0,t=50),scene=dict(aspectmode='data',xaxis_title='X [m]',yaxis_title='Y [m]',zaxis_title='Relatívna výška [m]',camera=dict(eye=dict(x=1.3,y=-1.5,z=.9))),updatemenus=[dict(type='buttons',direction='left',x=0,y=1.05,buttons=[dict(label='Skutočný pomer',method='relayout',args=[{'scene.aspectmode':'data'}]),dict(label='Zvýrazniť výšky',method='relayout',args=[{'scene.aspectmode':'manual','scene.aspectratio':dict(x=1,y=1,z=.22)}])])])
html=figp.to_html(full_html=True,include_plotlyjs=True,config=dict(scrollZoom=True,responsive=True,displaylogo=False));html=html.replace('<body>','<body><div style="font:14px Arial;padding:12px;color:#344d3b">Pracovný model v0.1 · metre · ±0,000 = 263,650 m. Otáčanie myšou, zoom kolieskom. Zlaté prvky: horná kóta na kontrolu. Červené obrysy: bez určenej výšky. Lokálny model, zatiaľ bez osadenia do DMR.</div>');(out/'zaklady_v01.html').write_text(html)
counts={k:sum(m['kind']==k for m in models)for k in set(m['kind']for m in models)};print('COUNTS',counts,'review',sum(m['status'].startswith('predbezna')for m in models));print('meshes',len(models),'all watertight')
(out/'README.txt').write_text('''BD ŠTUROVA – ZÁKLADY v0.1, 14.10.2026
PRACOVNÝ MODEL – nie realizačný ani statický návrh.
Zdroj: ZH -bytovka-pôdorysy.dwg, ZH -bytovka-rezy, pohlady.dwg; PDF 1, 2 a 15.
Geometria: polygonizované pôvodné čiary MÚRY a TENKÁ, jednotky prevedené mm → m.
A–B a C–D spojené posunom C–D −115361,5 mm v X, Y bez posunu; spoločné geometrie zlúčené.
Lokálny začiatok: X=4980696 mm, Y=−1499500 mm pôvodného DWG A–B.
Z je relatívne k ±0,000 = 263,650 m. Nie je aplikované geodetické osadenie do DMR.
OBJ je Z-up, GLB je Y-up, oba v metroch. JSON uchováva pôvodnú geometriu a metadáta.
Pásy a pätky: spodné kóty −5,000 / −5,400 / −5,800; horné −4,200 / −4,600 / −5,000, výška 800 mm.
Krčky a trámy: pôvodné obrysy TENKÁ pretiahnuté od horného povrchu podopierajúceho základu k priradenej kóte −3,450 / −3,670 / −3,870 / −3,900.
Priradenie horných kót je pracovné; zlaté prvky majú nejednoznačnú alebo vzdialenú kótu. CSV ich identifikuje. Všetky krčky ešte vyžadujú individuálnu kontrolu pred ďalším stupňom.
Podkladný betón, podlahové dosky, výstuž a nadväzujúce nadzemné stĺpy nie sú súčasťou v0.1.
Dve plochy P31 a P41 nemajú nájdenú jednoznačnú výškovú kótu: iba červený 2D obrys, bez objemu. Výška ich čiary v HTML je zobrazovacia.
P24 je otvor v sústave základov, nie samostatná pätka.
Kontrola rezov: A–A ľavá časť −5,000/−4,200, pravá −5,400/−4,600, nadväznosť krčkov na −3,670 a lokálne −3,450. B–B a F–F obsahujú −5,800/−5,000; C–C −5,000/−4,200; D–D a E–E obsahujú −5,400/−4,600. Kóty overené aj v textových entitách DWG rezov, nie kompletná priestorová kontrola každého prvku.
Oprava predchádzajúceho schematického rezu: pravá časť rezu A–A nie je založená na −5,000, ale na −5,400 m.
Validácia: uzavreté objemové siete, kladný objem, spodné bloky výšky 800 mm, krčky začínajú na hornej hrane podopierajúceho prvku. Nejde o kontrolu únosnosti ani súladu celej projektovej dokumentácie.
''')
shutil.copy('/tmp/model_foundations.py',out/'build_model.py')
for n in ['polygons.json','necks.json','aligned.json','section_text.json']:shutil.copy(base/n,out/n)
with zipfile.ZipFile('output/BD_STUROVA_zaklady_v01.zip','w',zipfile.ZIP_DEFLATED)as zf:
 for f in out.iterdir():zf.write(f,f.name)
