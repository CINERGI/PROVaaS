import boto.sqs
from boto.sqs.message import Message
from time import sleep

from help_json import *
from geoprovdm import *

#in this case, neo4j server and flask server are on the same machine, same SERVER_IP
SERVER_IP="127.0.0.1"
SERVER_IP="192.168.1.104"

ENVIRON = os.environ.get('PROV_ENVIRON')
if (ENVIRON == None):
   ENVIRON = 'PROD'

db = GeoProvDM(ENVIRON, "http://%s:7474/db/data/"%SERVER_IP, False)

'''
set the environment variables:
    AWS_ACCESS_KEY_ID - Your AWS Access Key ID
    AWS_SECRET_ACCESS_KEY - Your AWS Secret Access Key
'''

access_key = 'AKIAIQQYV2RQDHEF2Q4A'
secret_key = 'r1CMoVZ9CSr6HHaYYKA6VkAARf9bnnCvNyyBGy8P'

conn = boto.sqs.connect_to_region("us-west-2", aws_access_key_id=access_key, aws_secret_access_key = secret_key)

q = conn.create_queue('provaas_queue_v1')

import json
bRequiresNewLine = False

while True:
    m = q.read(60) # we estimate that processing this message will take less than that seconds
    if m is None:
        sleep(3)
        print ".",
        bRequiresNewLine = True
        continue

    if bRequiresNewLine: print
    bRequiresNewLine = False
    obj_received = json.loads(m.get_body())
    obj = obj_received['obj']
    requestId = obj_received['requestId']
    print "Processing id=%s containing: %s"%(str(requestId), str(obj))

    entities = obj['entity']
    for k in entities.keys():
        entity = json2obj(entities[k])
        entity[u'_id'] = k
        node = db.addEntity(entity)
        #db.addProperty(node,entity)

    # make all agents
    #agents = obj['agent']
    #for k in agents.keys():
    #    agent = json2obj(agents[k])
    #    agent[u'_id'] = k
    #    db.addAgent(agent)

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

    q.delete_message(m)