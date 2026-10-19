from rdflib import Graph
g=Graph(); g.parse("aind_all.ttl")
P="""PREFIX aindv:<https://wkmisr.github.io/arab-islamic-networks/vocab#> PREFIX crm:<http://www.cidoc-crm.org/cidoc-crm/> PREFIX prov:<http://www.w3.org/ns/prov#>"""
for lab,q in [
("relationships","SELECT (COUNT(?r) AS ?n) WHERE {?r a aindv:Relationship}"),
("rel by cert","SELECT ?c (COUNT(?r) AS ?n) WHERE {?r a aindv:Relationship . OPTIONAL{?r aindv:certainty ?c}} GROUP BY ?c"),
("events","SELECT (COUNT(?e) AS ?n) WHERE {?e a crm:E5_Event}"),
("distinct wd","SELECT (COUNT(DISTINCT ?o) AS ?n) WHERE {?s ?p ?o FILTER(STRSTARTS(STR(?o),'http://www.wikidata.org/entity/'))}"),
("distinct gn","SELECT (COUNT(DISTINCT ?o) AS ?n) WHERE {?s ?p ?o FILTER(STRSTARTS(STR(?o),'https://sws.geonames.org/'))}"),
("distinct TMP","SELECT (COUNT(DISTINCT ?o) AS ?n) WHERE {?s ?p ?o FILTER(CONTAINS(STR(?o),'/id/TMP-'))}"),
("distinct AIND-D objects w/o record","SELECT (COUNT(DISTINCT ?o) AS ?n) WHERE {?s ?p ?o FILTER(CONTAINS(STR(?o),'/id/AIND-D')) FILTER NOT EXISTS {?o a crm:E21_Person}}"),
("relations both ends AIND","SELECT (COUNT(?r) AS ?n) WHERE {?r aindv:active ?a ; aindv:passive ?b FILTER(CONTAINS(STR(?a),'/id/AIND-D'))}"),
]:
    print(lab, [tuple(str(x) for x in r) for r in g.query(P+q)])
