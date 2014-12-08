'''
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
Author: Tanu Malik <tanum@ci.uchicago.edu>
'''
#!/usr/local/bin/python2.7
import sys, json, datetime
from json import dumps
from flask import Flask, request, Response, jsonify
#from jsonhelp import *
from help_json import *
from geoprovdm import *

app = Flask(__name__)

db = GeoProvDM("http://localhost:7474/db/data/", False)

@app.route("/provenance/test")
def hello():
    return "Hello World!"

@app.route('/provenance/resource', methods=['POST'])
def create_resource_prov():

    # Atleast one entity should be present
    if not request.json or not 'entity' in request.json:
        return Response(status=400)

    obj = request.json

    # make all entities
    if 'entity' in obj:
    	entities = obj['entity']
    	for k in entities.keys():
            if 'foundry:UUID' in entities[k]: 
	     	entity = json2obj(entities[k])
             	entity[u'_id'] = k
             	node = db.addEntity(entity)
            	#db.addProperty(node,entity)
   	    else:
	     	return Response(status=400)
    else:
	return Response(status=400)
	 
    # make all agents
    if 'agent' in obj:
    	agents = obj['agent']
    	for k in agents.keys():
            agent = json2obj(agents[k])
            agent[u'_id'] = k
            db.addAgent(agent)
        
    # make all activities
    if 'activity' in obj:
    	acts = obj['activity']
    	for k in acts.keys():
            act = json2obj(acts[k])
            act[u'_id'] = k
            db.addActivity(act)
    
    # =========================
    # === add all relations ===
    for rel in db.getRequiredIdsInRelation().keys():
        try:
            relations = obj[rel]
            for name in relations.keys():
                db.addRelation(rel, name, relations[name])
        except KeyError:
            pass
 
    data = {"provenance submitted at": datetime.datetime.utcnow(), "submitted provenance": obj}
    return Response(dumps(data,default=outputJSON), mimetype='application/json',status=201)


@app.route('/provenance/b/resource/<string:uuid>', methods=['GET'])
def get_resource_provenance(uuid):
 
  #obj = db.getSubgraph(uuid)
  uuid1 = uuid
  obj = db.getNodeByUuid(uuid1)
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)

@app.route('/resource/<string:uuid>', methods=['DELETE'])
def delete_resource_provenance(uuid):
  uuid1 = uuid
  obj = db.deleteNodeByUuid(uuid1)
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)

@app.route('/provenance/b/resource/<string:uuid>/activity/<string:activityproperty>', methods=['GET'])
def get_resource_provenance_with_uuid_activityproperty(uuid,aprop):
  uuid1 = uuid
  aprop1 = aprop
  obj = db.getNodeByUuidWithActivity(uuid1,aprop1)
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)

@app.route('/provenance/<string:direction>/resource/<string:resourceproperty>', methods=['GET'])
def get_resource_provenance_with_resource_property(direction,rprop):
  direction1 = direction
  rprop1 = rprop
  if (direction1 == "b"):
     obj = db.getNodeByPropAncestral(rprop1)
  elif (direction1 == "f"):
     obj = db.getNodeByPropForward(rprop1)
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)

@app.route('/provenance/<string:direction>/resource/<string:resourceproperty>/activity/<string:activityproperty>', methods=['GET'])
def get_resource_provenance_with_resource_activity_property(direction, rprop, aprop):
  direction1 = direction
  rprop1 = rprop
  aprop1 = aprop
  if (direction1 == "b"):
     obj = db.getNodeByUuidWithAncestral(rprop1,aprop1)
  elif (direction1 == "f"):
     obj = db.getNodeByUuidWithForward(rprop1,aprop1)	
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)

@app.route('/provenance/<string:direction>/activity/<string:activityproperty>/from/<string:datetime1>/to/<string:datetime2>', methods=['GET'])
def get_resource_provenance_with_activity_from_to(direction, aprop, t1,t2):
  direction1 = direction
  aprop1 = aprop
  t11 = t1
  t21 = t2
  if (direction1 == "b"):
     obj = db.getNodeUsedByActivityWithTimestamp(aprop1,t11,t21)
  elif (direction1 == "f"):
     obj = db.getNodeGeneratedByActivityWithTimestamp(aprop1,t11,t21)
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)
	
if __name__ == '__main__':
    app.run(debug=True)
