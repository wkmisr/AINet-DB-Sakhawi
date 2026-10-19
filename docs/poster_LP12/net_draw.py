import pickle, matplotlib, networkx as nx
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.patheffects as pe
C,pos=pickle.load(open('net.pkl','rb')); deg=dict(C.degree())
fig=plt.figure(figsize=(18,12.2),dpi=220); ax=fig.add_axes([0,0,1,1]); ax.axis('off')
for t,col,w,a in (('int','#1C3F8F',0.5,0.35),('kin','#C8961E',1.2,0.85)):
    nx.draw_networkx_edges(C,pos,edgelist=[(u,v) for u,v,d in C.edges(data=True) if d['t']==t],edge_color=col,width=w,alpha=a,ax=ax)
nx.draw_networkx_nodes(C,pos,node_size=[4+min(deg[n],600)*1.2 for n in C],node_color='#0D2050',linewidths=0,ax=ax)
K='AIND-D06936'; ego=[K]+list(C.neighbors(K))
nx.draw_networkx_nodes(C,pos,nodelist=ego,node_size=[160 if n==K else 60 for n in ego],node_color='#D8AD52',edgecolors='#0D2050',linewidths=1.2,ax=ax)
L={'wd:Q4120128':'al-Sakhāwī (the author)','wd:Q471116':'Ibn Ḥajar al-ʿAsqalānī','AIND-D10690':'al-Zayn al-Marāghī','AIND-D09163':'Ibn al-Jazarī',
   'AIND-D09211':'al-Taqī Ibn Fahd','AIND-D08850':'Ibn al-Kuwayk',K:'al-Jamāl al-Kāzarūnī (Medina)'}
for n,l in L.items():
    if n not in pos: print('missing',n); continue
    x,y=pos[n]
    ax.annotate(l,(x,y),xytext=(14,10),textcoords='offset points',fontsize=19,fontweight='bold',color='#000000',
                path_effects=[pe.withStroke(linewidth=5,foreground='white')])
fig.savefig('network.png'); 
