#from geoprovdm import *
import sys,json,datetime,uuid
from py2neo import neo4j, node, rel
from pprint import pprint
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
                    elif r.type == 'wasGeneratedBy':
                        res['wasGeneratedBy'][r["_id"]]={"prov:entity": r.start_node["_id"], "prov:activity":  r.end_node["_id"]}
                    elif r.type == 'used':
                        res['used'][r["_id"]]={"prov:entity": r.start_node["_id"], "prov:activity":  r.end_node["_id"]}
                    elif r.type == 'wasDerivedFrom':
                        res['wasDerivedFrom'][r["_id"]]={"prov:usedEntity": r.start_node["_id"], "prov:generatedEntity":  r.end_node["_id"]}
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
                        res["activity"][n["_id"]]={n["__namespace"]+"type":{"$":  n[n["__namespace"]+":type"], "type": "xsd:string"},\
                                                  n["__namespace"]+":startTime":n[n["__namespace"]+":startTime"],\
                                                  n["__namespace"]+":endTime":n[n["__namespace"]+":endTime"], \
                          n["__namespace"]+":how":n[n["__namespace"]+":how"]}
                    elif "Entity" in n.get_labels():
                        if "entity" not in res:
                            res["entity"]={}
                        res["entity"][n["_id"]]={n["__namespace"]+":sourceId":{"$": n[n["__namespace"]+":sourceId"], "type": "xsd:string"},\
                                                      n["__namespace"]+":UUID":n[n["__namespace"]+":UUID"], \
                              n["__namespace"]+":creationTime":n[n["__namespace"]+":creationTime"],\
                                                      n["__namespace"]+":batchId":n[n["__namespace"]+":batchId"], \
                              n["__namespace"]+":label":"\"" + n[n["__namespace"]+":label"] + "\""}
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


def _jsonRefresh(fileIn, fileOut):
    with open(fileIn) as content_file:
        obj = json.loads(content_file.read())
    tmp=[]
    dic={}
    for attr in obj:
        if attr!="prefix" and type(obj[attr]) is dict:
            tmp+=obj[attr].keys()
    for ele in tmp:
        #ele=json.dumps(ele)
        dic[ele]=str(uuid.uuid1())
    print dic
    with open(fileOut, "wt") as fout:
        with open(fileIn, "rt") as fin:
            for line in fin:
                for key, val in dic.iteritems():
                    #print key[1:-1], type(key), type(val)
                    line=line.replace(key,val)
                print line
                fout.write(line)
    return fout


def jsonRefresh(inputJson):
    with open('request.json', "wt") as fout:
       json.dump(inputJson, fout)

    _jsonRefresh('request.json','response.json')
    
    with open('response.json','r') as json_data:
       obj = json.load(json_data)
    print obj
    return obj 



