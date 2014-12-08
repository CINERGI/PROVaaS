#from geoprovdm import *
import sys,json,datetime
from py2neo import neo4j, node, rel

# convert a prov-dm json to a python dictionary object
#   with key and value of type string
def json2obj(ajson):
    res = {}
    for attr in ajson:
        if type(ajson[attr]) is dict:
            if ajson[attr]['type'] == 'xsd:string':
                res[attr] = ajson[attr]['$']
            else:
                res[attr] = str(ajson[attr]['$'])
        else:
            res[attr] = str(ajson[attr])
    return res

def neo2json(aneo):
    res={}
    if aneo is not None:
        for paths in aneo:
            for path in paths:
                rels= path.relationships               
                nodes= path.nodes
                for r in rels:
                    if r.type not in res:
                            res[r.type] ={}
                    if r.type == 'wasDerivedFrom':
                        res['wasDerivedFrom'][r["name"]]={"prov:generatedEntity": r.start_node["_id"], "prov:usedEntity": r.end_node["_id"]}
                    elif r.type == 'actedOnBehalfOf':
                        res['actedOnBehalfOf'][r["name"]]={"prov:delegate": r.start_node["_id"], "prov:responsible": r.end_node["_id"]}
                    elif r.type == 'wasInformedBy':
                        res['wasInformedBy'][r["name"]]={"prov:informed": r.start_node["_id"], "prov:informant": r.end_node["_id"]}
                    elif r.type == 'wasStartedBy':
                        res['wasStartedBy'][r["name"]]={"prov:activity": r.start_node["_id"], "prov:trigger":  r.end_node["_id"]}
                    elif r.type == 'wasEndedBy':
                        res['wasEndedBy'][r["name"]]={"prov:activity": r.start_node["_id"], "prov:trigger":  r.end_node["_id"]}    
                    else:
                        s=r.start_node.get_labels()# type is set
                        e=r.end_node.get_labels()
                        if "Activity" in s:
                            st='activity'
                        elif "Entity" in s:
                            st='entity'
                        elif "Agent" in s:
                            st='agent'
                        if "Activity" in e:
                            et='activity'
                        elif "Entity" in e:
                            et='entity'
                        elif "Agent" in e:
                            et='agent'
                        snode='prov:'+ st
                        enode='prov:'+ et 
                        res[r.type][r["name"]]={snode: r.start_node["_id"], enode: r.end_node["_id"]}
                            
                for n in nodes:
                    if "Activity" in n.get_labels():
                        if "activity" not in res:
                            res["activity"]={}
                        res["activity"][n["_id"]]={"prov:type":{"$":  n["prov:type"], "type": "xsd:string"},\
                                                  "prov:startTime":n["prov:startTime"],\
                                                  "prov:endTime":n["prov:endTime"]}
                    elif "Entity" in n.get_labels():
                        if "entity" not in res:
                            res["entity"]={}
                        res["entity"][n["_id"]]={"foundry:sourceId":{"$": n["foundry:sourceId"], "type": "xsd:string"},\
                                                      "foundry:UUID":n["foundry:UUID"],"foundry:creationTime":n["foundry:creationTime"],\
                                                      "foundry:batchId":n["foundry:batchId"]}
                    elif "Agent" in n.get_labels():#if node[size]["prov:type"] is not None:#and not node[size].has_key("prov:startTime") and not node[size].has_key("foundry:UUID"):
                        if "agent" not in res:
                            res["agent"] ={}
                        res["agent"][n["_id"]]={"prov:type":{"$":n["prov:type"], "type": "xsd:string"}}
                    else:
                        pass
                
        res2 = json.dumps(res,ensure_ascii=True)
        #print res2
    return res2
    
def outputJSON(obj):
    """Default JSON serializer."""

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()

        return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
    return str(obj)


def quote(str):
    return "\"" + str + "\""
