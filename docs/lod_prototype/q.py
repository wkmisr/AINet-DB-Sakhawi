import sys
from rdflib import Graph
g=Graph(); g.parse("aind_all.ttl")
P="""PREFIX aind:<https://wkmisr.github.io/arab-islamic-networks/id/> PREFIX aindv:<https://wkmisr.github.io/arab-islamic-networks/vocab#>
PREFIX crm:<http://www.cidoc-crm.org/cidoc-crm/> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX prov:<http://www.w3.org/ns/prov#>"""
qs={
"top_teachers":"""SELECT ?t (SAMPLE(?l) AS ?lab) (COUNT(DISTINCT ?s) AS ?n) WHERE { ?t aindv:teacherOf ?s . OPTIONAL{?t rdfs:label ?l} } GROUP BY ?t ORDER BY DESC(?n) LIMIT 12""",
"kazaruni":"""SELECT ?s ?name ?m WHERE { ?r aindv:relType aindv:teacher ; aindv:active aind:AIND-D06936 ; aindv:passive ?s . OPTIONAL{?r aindv:methodText ?m} OPTIONAL{?s rdfs:label ?name} }""",
"kin_cotaught":"""SELECT DISTINCT ?t ?a ?b ?k WHERE { ?t aindv:teacherOf ?a , ?b . ?a ?kp ?b . FILTER(?kp IN (aindv:brotherOf, aindv:fatherOf, aindv:sonOf)) BIND(STRAFTER(STR(?kp),"#") AS ?k) FILTER(STRSTARTS(STR(?t),"https://wkmisr.github.io/arab-islamic-networks/id/AIND")) } LIMIT 400""",
"counts":"""SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?r a aindv:Relationship }""",
"agents":"""SELECT ?ty (COUNT(DISTINCT ?a) AS ?n) (COUNT(?q) AS ?acts) WHERE { ?q prov:agent ?a . ?a a ?ty } GROUP BY ?ty""",
}
for k in sys.argv[1:]:
    print("==",k)
    for row in g.query(P+qs[k]): print("\t".join(str(x) for x in row))
