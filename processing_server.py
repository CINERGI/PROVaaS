import boto.sqs
from boto.sqs.message import Message
from time import sleep

from help_json import *
from geoprovdm import *
from datetime import datetime
import argparse

'''
run with arguments '--test 1' to obtain TEST mode
'''
#in this case, neo4j server and flask server are on the same machine, same SERVER_IP
NEO4J_SERVER_IP="127.0.0.1"
# NEO4J_SERVER_IP="192.168.1.105"

ENVIRON = os.environ.get('PROV_ENVIRON')
if (ENVIRON == None):
   ENVIRON = 'PROD'

db = GeoProvDM(ENVIRON, "http://%s:7474/db/data/"%NEO4J_SERVER_IP, False)

parser = argparse.ArgumentParser()
parser.add_argument("--test", help="start server in test mode")
args = parser.parse_args()
if args.test:
    print "Starting server in TEST mode"
else:
    print "Starting server in NORMAL mode"

'''
set the environment variables:
    AWS_ACCESS_KEY_ID - Your AWS Access Key ID
    AWS_SECRET_ACCESS_KEY - Your AWS Secret Access Key
'''

conn = boto.sqs.connect_to_region("us-west-2")#, aws_access_key_id=access_key, aws_secret_access_key = secret_key)
q = conn.create_queue('provaas_queue_v1')

import json
bRequiresNewLine = False

max_processing_seconds = 60
debug_ips = ["89.136.140.39","192.168.1.105"]
if args.test:
    print "Processing ONLY requests submitted from: ",debug_ips
else:
    print "Processing all, EXCEPT requests submitted from: ",debug_ips
while True:
    m = q.read(max_processing_seconds) # we estimate that processing this message will take less than that seconds
    if m is None:
        sleep(300) # wait 5 minutes, maybe requests will come
        print ".",
        bRequiresNewLine = True
        continue

    if bRequiresNewLine: print
    bRequiresNewLine = False
    obj_received = json.loads(m.get_body())
    obj = obj_received['obj']
    requestId = obj_received['requestId']
    submitAt = obj_received['submitAt']
    requestIP = obj_received['requestIP']
    user = obj_received['user']

    # client_ips for test - ignored in provaas.org
    if requestIP in debug_ips:
        if not args.test:
            print "%s: request from %s will be ignored for %s seconds"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),requestIP, max_processing_seconds)
            continue
    else:
        pass
        # all other IPs are processed normally

    processing_starttime = datetime.now()
    print "start processing at: ", processing_starttime.strftime("%Y-%m-%d %H:%M:%S.%f")
    print "Processing id={requestId}, submitted from {requestIP} at {submitAt} by {user}, containing: {obj}".format(
           requestId=requestId,requestIP=requestIP,submitAt=submitAt,user=user,obj=obj)

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
    processing_endtime = datetime.now()
    print "end processing at: ", processing_endtime.strftime("%Y-%m-%d %H:%M:%S.%f")
    print "processing took: ",str(processing_endtime-processing_starttime)