import csv,collections,networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
D="/mnt/user-data/uploads/AINet-DB-Sakhawi/docs/poster_LP12/data"
E=list(csv.DictReader(open(D+"/edges.tsv",encoding='utf-8'),delimiter='\t'))
KIN={'father','son','brother','grandfather','uncle','mother','spouse','cousin','relative','siblings_child','father-in-law','maternal_grandfather','daughter','sister','grandson','maternal_uncle','brother-in-law','son-in-law','ancestor','grandmother','granduncle','relative_by_marriage'}
G=nx.Graph()
for e in E:
    t='kin' if e['subtype'] in KIN else 'int' if e['subtype'] in ('teacher','student') else None
    if t: G.add_edge(e['src'],e['tgt'],t=t)
cc=max(nx.connected_components(G),key=len); C=G.subgraph(cc).copy()
pos=nx.spring_layout(C,seed=7,k=0.9/ (len(C)**0.5),iterations=300)
import pickle; pickle.dump((C,pos),open('net.pkl','wb'))
deg=dict(C.degree())
fig=plt.figure(figsize=(18,13),dpi=200); ax=fig.add_axes([0,0,1,1]); ax.axis('off')
for t,col,w,a in (('int','#1C3F8F',0.5,0.35),('kin','#C8961E',1.1,0.8)):
    nx.draw_networkx_edges(C,pos,edgelist=[(u,v) for u,v,d in C.edges(data=True) if d['t']==t],edge_color=col,width=w,alpha=a,ax=ax)
sz=[4+min(deg[n],600)*1.2 for n in C]
nx.draw_networkx_nodes(C,pos,node_size=sz,node_color='#0D2050',linewidths=0,ax=ax)
fig.savefig('net_test.png'); print(len(C), C.number_of_edges(), sorted(deg.items(),key=lambda x:-x[1])[:12])
