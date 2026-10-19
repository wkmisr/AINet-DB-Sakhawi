import pickle, matplotlib, networkx as nx
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.patheffects as pe
C,pos=pickle.load(open('net.pkl','rb')); deg=dict(C.degree())
xs=[p[0] for p in pos.values()]; ys=[p[1] for p in pos.values()]
fig=plt.figure(figsize=(11.0,7.4),dpi=300); ax=fig.add_axes([0.01,0.01,0.98,0.98]); ax.axis('off')
ax.set_xlim(min(xs)-0.02,max(xs)+0.02); ax.set_ylim(min(ys)-0.02,max(ys)+0.02)
for t,col,w,a in (('int','#1C3F8F',0.35,0.4),('kin','#C8961E',0.8,0.9)):
    nx.draw_networkx_edges(C,pos,edgelist=[(u,v) for u,v,d in C.edges(data=True) if d['t']==t],edge_color=col,width=w,alpha=a,ax=ax)
nx.draw_networkx_nodes(C,pos,node_size=[2+min(deg[n],600)*0.6 for n in C],node_color='#0D2050',linewidths=0,ax=ax)
K='AIND-D06936'; ego=[K]+list(C.neighbors(K))
nx.draw_networkx_nodes(C,pos,nodelist=ego,node_size=[90 if n==K else 35 for n in ego],node_color='#D8AD52',edgecolors='#0D2050',linewidths=0.9,ax=ax)
L={'wd:Q4120128':'al-Sakhāwī (the author)','wd:Q471116':'Ibn Ḥajar','AIND-D10690':'al-Zayn al-Marāghī','AIND-D09163':'Ibn al-Jazarī',
   'AIND-D09211':'al-Taqī Ibn Fahd','AIND-D08850':'Ibn al-Kuwayk',K:'al-Jamāl al-Kāzarūnī (Medina)'}
for n,l in L.items():
    x,y=pos[n]
    ax.annotate(l,(x,y),xytext=(8,6),textcoords='offset points',fontsize=13,fontweight='bold',color='#000000',path_effects=[pe.withStroke(linewidth=4,foreground='white')])
fig.savefig('network_s.png')
