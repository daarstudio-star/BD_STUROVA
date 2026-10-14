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
out=Path('output/BD_STUROVA_zaklady_v02');out.mkdir(exist_ok=True)
base=Path('tmp/foundations');ps=json.load(open(base/'polygons.json'));ns=json.load(open(base/'necks.json'));es=json.load(open(base/'aligned.json'));origin=np.array([4980696.,-1499500.]);models=[];parents=[]
cols={-5.0:'#8da99a',-5.4:'#5e82a2',-5.8:'#a77a61'}
for item in ps:
 if item['id'] in [24,31,41]:continue
 p=Polygon(item['xy'],item['holes']);levels=[float(v.replace(',','.'))for v in item['labels']];bottom=min(levels);top=round(bottom+.8,3)
 assert bottom in cols
 ident=f"F{item['id']:02d}";parents.append((p,bottom,top,ident,item))
 models.append(dict(id=ident,kind='patka' if p.area<15 else 'pas_sustava',polygon=p,zmin=bottom,zmax=top,status='kota_v_podoryse',color=cols[bottom],parent=''))
# Explicit source assignments; no nearest-text assignment.
neck_rules={1:(-4.6,-3.87),2:(-4.6,-3.87),3:(-5.0,-3.45),4:(-4.6,-3.67),5:(-4.6,-3.45),7:(-4.6,-3.67),8:(-4.6,-3.67),9:(-5.0,-3.67),10:(-4.2,-3.67),11:(-4.2,-3.67),26:(-4.6,-3.45),46:(-4.2,-3.9),47:(-4.2,-3.45),48:(-4.6,-3.45),49:(-4.6,-3.67),50:(-4.6,-3.67),51:(-4.2,-3.45),52:(-4.2,-3.67),53:(-4.2,-3.45),54:(-4.2,-3.67),56:(-4.2,-3.67),57:(-4.2,-3.45),79:(-4.2,-3.67)}
# Ambiguous intersections/steps are intentionally retained as 2D source outlines.
neck_rules.update({25:(-5.0,-3.67),26:(-4.6,-3.67),24:(-4.6,-3.45),37:(-5.0,-3.67),38:(-5.0,-3.67),63:(-4.2,-3.45),67:(-4.2,-3.45),66:(-4.2,-3.67),78:(-4.2,-3.67),85:(-4.2,-3.67)})
ambiguous={1,2,11,12,23,27,55,59,60,64}
voids={0,6,13,30,31,32,65}
unresolved=[]
for i,n in enumerate(ns):
 if i in voids:continue
 q=Polygon(n['xy'],n['holes'])
 if i in ambiguous:
  unresolved.append(dict(id=f'N{i:02}',reason='potrebne priradit dolnu/hornu kotu a lokalne stupne bez odhadu',xy=n['xy'],holes=n['holes']));continue
 if i in neck_rules:
  zlo,zhi=neck_rules[i];pid='';status='explicitna_kota_podla_oblasti_vykresu'
 else:
  supports=[(p,lo,hi,pid,item) for p,lo,hi,pid,item in parents if p.covers(q.representative_point())]
  if len(supports)!=1:
   unresolved.append(dict(id=f'N{i:02}',reason='chybajuca jednoznacna podpora alebo kota',xy=n['xy'],holes=n['holes']));continue
  p,lo,zlo,pid,item=supports[0]
  tops=[float(a.replace(',','.')) for a in item['labels'] if a in ['-3,670','-3,450','-3,870','-3,900']]
  if q.area>1 or len(tops)!=1:
   unresolved.append(dict(id=f'N{i:02}',reason='viac hornych kot v oblasti; nutna lokalna kontrola',xy=n['xy'],holes=n['holes']));continue
  zhi=tops[0];status='jednoznacna_kota_podorysu'
 models.append(dict(id=f'N{i:02}',kind='krcok_stlpa' if q.area<1 else 'zakladovy_tram',polygon=q,zmin=zlo,zmax=zhi,status=status,color='#d2d9de',parent=pid))
# Source-outline bridge beams with a single repeated top level are emitted separately.
# Their local end-step exceptions remain outlined for review, so no false exactness.
for i in [1,2]:
 q=Polygon(ns[i]['xy'],ns[i]['holes']);zlo,zhi=neck_rules[i]
 models.append(dict(id=f'T{i:02}',kind='zakladovy_tram',polygon=q,zmin=zlo,zmax=zhi,status='pracovna_geometria_koncove_stupne_neuzavrete',color='#d9bc78',parent=''))
json.dump(unresolved,open(out/'neuzavrete_detaily.json','w'),ensure_ascii=False,indent=2)
scene=trimesh.Scene();meta=[];traces=[];faces3d=[]
for m in models:
 mesh=trimesh.creation.extrude_polygon(m['polygon'].simplify(0.000001,preserve_topology=True),m['zmax']-m['zmin'],engine='earcut');mesh.apply_translation([0,0,m['zmin']]);color=matplotlib.colors.to_rgba(m['color']);mesh.visual.face_colors=np.array(color)*255
 
 if not mesh.is_watertight or mesh.volume<=0:print('BAD',m['id'],m['polygon'].is_valid,m['polygon'].area);raise ValueError(m['id'])
 scene.add_geometry(mesh,node_name=m['id'],geom_name=m['id']);vertices=mesh.vertices;faces=mesh.faces
 meta.append({k:v for k,v in m.items()if k not in ['polygon','color']}|dict(xy=list(m['polygon'].exterior.coords),holes=[list(r.coords)for r in m['polygon'].interiors],area_m2=round(m['polygon'].area,5),volume_m3=round(mesh.volume,5),zmin_absolute=round(263.65+m['zmin'],3),zmax_absolute=round(263.65+m['zmax'],3)))
 traces.append(go.Mesh3d(x=vertices[:,0],y=vertices[:,1],z=vertices[:,2],i=faces[:,0],j=faces[:,1],k=faces[:,2],color=m['color'],flatshading=True,name=m['id'],hovertemplate=f"{m['id']} · {m['kind']}<br>{m['zmin']:.3f} → {m['zmax']:.3f} m<br>{m['status']}<extra></extra>",showlegend=False))
 faces3d.append((vertices[faces],m['color']))
# OBJ is Z up, metres, relative to project zero.
scene.export(str(out/'zaklady_v02.obj'))
# glTF uses Y up; bake transform while preserving metre units.
gltf=scene.copy();gltf.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0]));gltf.export(str(out/'zaklady_v02.glb'))
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

for u in unresolved:
 xy=np.array(u['xy']);plan.plot(xy[:,0],xy[:,1],color='#bd8530',lw=.8,ls='--')
ax.set(xlim=(-2,63),ylim=(-2,62),zlim=(-6,-3),xlabel='X [m]',ylabel='Y [m]',zlabel='Relatívna výška [m]');ax.set_box_aspect((62,62,15));ax.view_init(26,-57);ax.tick_params(labelsize=8)
plan.set_aspect('equal');plan.set_title('Pôdorys · farba podľa spodnej kóty',fontsize=11);plan.tick_params(labelsize=8);plan.set_xlabel('X [m]');plan.set_ylabel('Y [m]')
fig.text(.055,.94,'BD ŠTUROVA / ZÁKLADY · ROZPRACOVANÝ MODEL v0.2',fontsize=24,color='#263f31',weight='bold');fig.text(.055,.9,'Geometria z DWG • pásy a pätky 800 mm • krčky a trámy s rozlíšenými výškami',fontsize=12,color='#58695b')
fig.legend(handles=[Patch(color=cols[k],label=f'{k:.3f} m')for k in cols]+[Patch(color='#d2d9de',label='Krčky / trámy'),Patch(color='#d9bc78',label='Horná kóta na kontrolu')],loc='lower center',bbox_to_anchor=(.50,.11),ncol=5,frameon=False)
fig.text(.055,.068,'±0,000 = 263,650 m. Pracovný model v lokálnych súradniciach; zvislé rozmery v obrázku sú zvýraznené.',fontsize=11,color='#58695b')
fig.text(.055,.037,'Červené ? = neurčené kóty P31/P41. Zlaté obrysy a trámy = nedoriešené detaily; model nie je kompletný.',fontsize=10,color='#58695b');fig.savefig(out/'zaklady_v02_nahlad.png',dpi=160)
figp=go.Figure(traces)
for u in unresolved:
 xy=np.array(u['xy']);figp.add_trace(go.Scatter3d(x=xy[:,0],y=xy[:,1],z=[-3.2]*len(xy),mode='lines',line=dict(color='#d69c38',width=3),showlegend=False,name=u['id'],hovertemplate=u['id']+' · nepotvrdený detail; iba obrys na zobrazovacej rovine<extra></extra>'))
for i in [31,41]:
 xy=np.array(ps[i]['xy']);figp.add_trace(go.Scatter3d(x=xy[:,0],y=xy[:,1],z=[-3.2]*len(xy),mode='lines',line=dict(color='#cc4e46',width=5),name=f'Neurčená výška P{i}',hovertemplate='Len 2D obrys; Z = −3,2 je zobrazovacia rovina, nie projektová kóta.<extra></extra>'))
figp.update_layout(title='BD Šturova · základové konštrukcie v0.2',paper_bgcolor='#f8faf7',margin=dict(l=0,r=0,b=0,t=50),scene=dict(aspectmode='data',xaxis_title='X [m]',yaxis_title='Y [m]',zaxis_title='Relatívna výška [m]',camera=dict(eye=dict(x=1.3,y=-1.5,z=.9))),updatemenus=[dict(type='buttons',direction='left',x=0,y=1.05,buttons=[dict(label='Skutočný pomer',method='relayout',args=[{'scene.aspectmode':'data'}]),dict(label='Zvýrazniť výšky',method='relayout',args=[{'scene.aspectmode':'manual','scene.aspectratio':dict(x=1,y=1,z=.22)}])])])
html=figp.to_html(full_html=True,include_plotlyjs=True,config=dict(scrollZoom=True,responsive=True,displaylogo=False));html=html.replace('<body>','<body><div style="font:14px Arial;padding:12px;color:#344d3b">Pracovný model v0.2 · metre · ±0,000 = 263,650 m. Otáčanie myšou, zoom kolieskom. Zlaté trámy: hlavná kóta −3,870 m, lokálne koncové stupne ešte neuzavreté. Zlaté obrysy: bez potvrdeného objemu. Červené obrysy: bez určenej výšky. Lokálny model, zatiaľ bez osadenia do DMR.</div>');(out/'zaklady_v02.html').write_text(html)
counts={k:sum(m['kind']==k for m in models)for k in set(m['kind']for m in models)};print('COUNTS',counts,'review',sum(m['status'].startswith('predbezna')for m in models));print('meshes',len(models),'all watertight')
(out/'README.txt').write_text("""BD ŠTUROVA – rozpracovaný model v0.2
Zdrojová geometria z DWG pôdorysov; spoločný základ ±0,000=263,650 m. Metre, lokálne súradnice. OBJ Z-up, GLB Y-up.
Spodné pásy a pätky podľa jednoznačných dvojíc kót: −5,000/−4,200; −5,400/−4,600; −5,800/−5,000.
Horné úrovne samostatných krčkov iba pri jednoznačnej kóte. Automatické vyberanie najbližšieho textu sa nepoužíva.
Doplnená úroveň −3,900 m pri severozápadnom jadre. Doplnené južné prepojovacie trámy s hlavnou úrovňou −3,870 m bez pôvodného nesprávneho orezania len nad pätkami. Ich miestne koncové stupne nie sú uzavreté, sú zlaté a nie sú označené ako presný finálny prvok.
Úplný presný model ešte nie je hotový. Zložité detaily s nedoriešeným lokálnym výškovým členením sú v neuzavrete_detaily.json a v HTML ako zlaté obrysy. Ich zobrazovacia rovina −3,2 m nie je projektová kóta.
P31/P41 nemajú jednoznačne priradené kóty, bez objemu. Dilatačná škára N13 šírky 50 mm nie je betónový prvok.
Model neobsahuje kompletné obvodové krčky, všetky schodiskové detaily, podkladný betón, dosky, výstuž ani stĺpy nad hornou hranou základových krčkov. Nejde o IFC BIM ani realizačný model.
Overenie objemových sietí nezaručuje súlad každého detailu s projektom. Zoznam stavu prvkov je v CSV a JSON.
""")
shutil.copy('/tmp/model_v02.py',out/'build_model.py')
for n in ['polygons.json','necks.json','aligned.json','section_text.json']:shutil.copy(base/n,out/n)
with zipfile.ZipFile('output/BD_STUROVA_zaklady_v02.zip','w',zipfile.ZIP_DEFLATED)as zf:
 for f in out.iterdir():zf.write(f,f.name)
