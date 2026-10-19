import json, csv, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
C={ # curated city-level coordinates (approximate)
'gn:104515':(21.42,39.83,'Mecca'),'gn:360630':(30.04,31.24,'Cairo'),'gn:352261':(30.01,31.23,None),'gn:170654':(33.51,36.29,'Damascus'),
'gn:109223':(24.47,39.61,'Medina'),'gn:170063':(36.20,37.16,'Aleppo'),'#TMP-L-00036':(21.49,39.19,None),'gn:266826':(34.44,35.83,None),
'#TMP-L-00042':(31.50,34.47,None),'gn:281184':(31.78,35.23,'Jerusalem'),'gn:361058':(31.20,29.92,None),'gn:277130':(34.01,36.21,None),
'#TMP-L-00041':(14.20,43.32,'Zabīd'),'gn:358048':(31.42,31.81,None),'gn:293100':(32.97,35.50,None),'#TMP-L-00044':(30.97,31.17,None),
'gn:285066':(31.53,35.10,None),'gn:170017':(35.13,36.75,None),'#TMP-L-00081':(24.09,38.06,None),'#TMP-L-00050':(13.58,44.02,None),
'#TMP-L-00140':(15.21,43.06,None),'gn:2464470':(36.80,10.18,'Tunis'),'#TMP-L-00049':(12.79,45.03,'Aden'),'#TMP-L-00010':(13.97,44.18,None),
'#TMP-L-00051':(34.03,-4.98,'Fez'),'#TMP-L-00055':(29.59,52.58,'Shiraz'),'#TMP-L-00047':(37.91,40.24,None),'#TMP-L-00062':(34.73,36.71,None),
'#TMP-L-00204':(30.79,31.00,None),'#TMP-L-00059':(31.93,34.87,None),'gn:2505329':(36.75,5.07,None),'#TMP-L-00011':(40.63,48.64,None),
'#TMP-L-00056':(21.27,40.42,None),'gn:282615':(32.22,35.26,None),'gn:2517117':(37.18,-3.60,'Granada'),'#TMP-L-00043':(33.31,44.36,'Baghdad'),
'gn:304922':(38.35,38.31,None),'gn:305608':(38.35,38.31,None),'gn:325363':(37.00,35.32,None),'#TMP-L-00173':(37.71,41.41,None),'gn:1265873':(11.25,75.78,'Calicut'),
'#TMP-L-00205':(30.28,57.08,None),'#TMP-L-00067':(22.31,72.62,'Cambay'),'#TMP-L-00315':(30.07,32.37,None),'#TMP-L-00052':(31.18,35.70,None),
'#TMP-L-00068':(37.31,40.74,None),'gn:276781':(33.89,35.50,None),'#TMP-L-00060':(38.08,46.29,'Tabriz'),'#TMP-L-00101':(11.35,43.47,None),
'#TMP-L-00191':(23.78,38.79,None),'gn:105995':(23.78,38.79,None),'gn:359146':(27.78,30.80,None),'#TMP-L-00096':(42.30,59.15,'Khwārazm'),
'#TMP-L-00168':(26.10,34.28,None),'#TMP-L-00242':(37.30,-3.14,None),'gn:2516422':(37.30,-3.14,None),'gn:268064':(33.56,35.37,None),
'gn:315372':(39.75,39.49,None),'gn:361546':(31.13,33.80,None),'gn:349715':(30.96,31.24,None),'gn:2485926':(35.70,-0.63,None),
'gn:340218':(15.70,40.10,None),'gn:1273294':(28.65,77.23,'Delhi'),'gn:105299':(16.89,42.55,None),'gn:2464917':(35.83,10.64,None),
'gn:2464915':(35.83,10.64,None),'gn:2507026':(36.75,3.06,None),'gn:750269':(40.19,29.06,'Bursa'),'gn:299817':(36.92,34.89,None),
'gn:692713':(45.03,35.09,'Crimea'),'gn:170905':(32.62,36.10,None),'#TMP-L-00102':(18.60,41.40,None),'gn:415189':(12.79,45.03,None),
'#TMP-L-00254':(30.46,30.93,None),'#TMP-L-00243':(31.32,31.72,None),'#TMP-L-00267':(30.97,30.66,None),
}
cnt={}
for r in csv.DictReader(open('/mnt/user-data/uploads/AINet-DB-Sakhawi/docs/poster_LP12/data/places.tsv',encoding='utf-8'),delimiter='\t'):
    if r['ref'] in C:
        la,lo,_=C[r['ref']]; k=(round(la,1),round(lo,1)); cnt[k]=cnt.get(k,0)+int(r['count'])
labels={(round(la,1),round(lo,1)):nm for la,lo,nm in C.values() if nm}
land=json.load(open('/home/claude/geo/ne_50m_land.geojson'))
fig=plt.figure(figsize=(17.0,8.8),dpi=250); ax=fig.add_axes([0,0,1,1])
ax.set_facecolor('#DCE6F2')
patches=[]
for f in land['features']:
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for poly in polys: patches.append(Polygon(poly[0],closed=True))
ax.add_collection(PatchCollection(patches,facecolor='#F3F0E8',edgecolor='#8C97A8',linewidth=0.5))
ax.set_xlim(-11,80); ax.set_ylim(6,47.5); ax.set_aspect(1.0/__import__('math').cos(__import__('math').radians(28)))
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)
# Qalasadi route (al-Ḍawʾ + PUA)
route=[(37.49,-2.77,'Basṭa (b. before 815)'),(34.88,-1.32,'Tlemcen 840'),(36.80,10.18,'847'),(30.04,31.24,'850, 852'),(21.42,39.83,'851')]
xs=[p[1] for p in route]; ys=[p[0] for p in route]
ax.plot(xs,ys,color='#8A5F0D',lw=3.2,ls=(0,(6,3)),zorder=4)
for la,lo,nm in route:
    ax.plot(lo,la,'o',ms=9,mfc='#D8AD52',mec='#8A5F0D',mew=1.5,zorder=6)
import math
for (la,lo),c in sorted(cnt.items(),key=lambda x:-x[1]):
    ax.scatter(lo,la,s=12+math.sqrt(c)*28,color='#1C3F8F',alpha=0.55,edgecolors='#0D2050',linewidths=0.6,zorder=5)
for (la,lo),nm in labels.items():
    right=lo>70
    ax.annotate(nm,(lo,la),xytext=(-8 if right else 6,4),textcoords='offset points',ha='right' if right else 'left',fontsize=15,fontweight='bold',color='#0D2050',zorder=7,
                path_effects=[pe.withStroke(linewidth=4,foreground='white')])
for la,lo,nm in route:
    if True:
        ax.annotate(nm,(lo,la),xytext=(6,-16),textcoords='offset points',fontsize=14,fontweight='bold',color='#8A5F0D',zorder=7,
                path_effects=[pe.withStroke(linewidth=4,foreground='white')])
fig.savefig('map.png'); print(len(cnt),'points', sum(cnt.values()),'mentions')
