import sys, os, datetime, decimal
import json
import networkx as nx

class PROV:
    """ Main PROV class that cretaes a PROV graph from JSON object and validates it.
    """


    def __init__(self, jsonobj):
        provg  = nx.DiGraph()

        #add nodes; currently entities and activities
        entities = jsonobj.get('entity') or []
        activities = jsonobj.get('activity') or []

        for k in entities:
            #print "adding " +str (k) + " having value =" + str(entities[k])
            provg.add_node(k, entities.get(k) )
        for k in activities:
            provg.add_node(k, activities.get(k) )

        #add relationships
        wasGeneratedBy = jsonobj.get('wasGeneratedBy') or []
        used = jsonobj.get('used') or []
        wasDerivedFrom = jsonobj.get('wasDerivedFrom') or []

        for k in wasGeneratedBy:
            #print "adding edge " +str (k) + " having value =" + str(wasGeneratedBy[k])
            provg.add_edge(wasGeneratedBy[k]['prov:entity'],wasGeneratedBy[k]['prov:activity'], dict(type=wasGeneratedBy, name=k) )
        for k in used:
            #print "adding edge " +str (k) + " having value =" + str(used[k])
            provg.add_edge(used[k]['prov:activity'],used[k]['prov:entity'], dict(type=used, name=k) )
        for k in wasDerivedFrom:
            #print "adding edge  " +str (k) + " having value =" + str(wasDerivedFrom[k])
            provg.add_edge(wasDerivedFrom[k]['prov:usedEntity'],wasDerivedFrom[k]['prov:generatedEntity'], dict(type=wasDerivedFrom, name=k) )
        print "-------------"
        print provg.nodes()
        print provg.edges()

    def _validate(provgraph):
       return True


if __name__ == "__main__":
    # For testing


    json_data=open('C1-file1.json')
    obj = json.load(json_data)
    json_data.close()
    xxx=PROV(obj)


