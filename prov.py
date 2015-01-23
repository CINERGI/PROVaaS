import sys, os, datetime, decimal
import json
import networkx as nx
from pprint import pprint
import uuid
#from time import mktime, strptime
from datetime import datetime
import copy

def is_invalid_date(input_date_time):

    result = None

    for format in ['%Y%m%d', '%Y%m%d.%H']:
	try:
	    result = datetime.strptime(input_date_time, format)
	except:
	    pass

    if result is None:
	# print 'Malformed date.'
	return True
    else:
	# print 'Date is fine.'
	return False

# returns value of a filed of an element from a list of elements
def getField(elementsList, element, filedId):
    return elementsList[element][elementsList[element]['__namespace']+':'+filedId]


def validateJSONRequest(jsonobj)

	provg  = nx.DiGraph()

	#add nodes; currently entities and activities
	entities = jsonobj.get('entity')
	if entities is None:
	    return False, "There are no entities"

	activities = jsonobj.get('activity') or []

	for k in entities:
	    # "foundry:en9"
	    namespace , entity_name = k.split(':')
	    #print "adding entity " +str (k) + " having value ="
	    #pprint(entities[k])
	    if entities[k].get(namespace+':UUID') is None:
		     ret = False, "There is no UUID in entity "+k
	    if entities[k].get(namespace+':creationTime') is None:
		     ret = False, "There is no creationTime in entity "+k
	    if entities[k].get(namespace+'version') is None:
		     ret = False, "There is no version in entity "+k
	    if is_invalid_date(entities[k][namespace+':creationTime']['$']):
		     ret = False, "Invalid creationTime format in entity "+k

	    entities[k]['__namespace'] = namespace
	    print entities[k][namespace+':creationTime']['$']
      # All good with entity
	    provg.add_node(k, entities.get(k) )

	for k in activities:
	    namespace , entity_name = k.split(':')
	    print "adding activity " +str (k) + " having value ="
	    pprint(activities[k])
	    if activities[k].get(namespace+':type') is None:
		     ret =  False, "There is no type in activity "+k
	    if activities[k].get(namespace+':startTime') is None:
		     ret =  False, "There is no startTime in activity "+k
	    if activities[k].get(namespace+':endTime') is None:
		     ret =  False, "There is no endTime in activity "+k
	    if activities[k][namespace+':endTime'] > activities[k][namespace+':startTime']:
		     ret =  False, "StartTime should be before endTime in activity "+k

	    if is_invalid_date(activities[k][namespace+':startTime']):
		     ret = False, "Invalid startTime format in activity "+k
	    if is_invalid_date(activities[k][namespace+':endTime']):
		     ret = False, "Invalid endTime format in activity "+k

	    activities[k]['__namespace'] = namespace
	    
	    provg.add_node(k, activities.get(k) )


	#add relationships
	wasGeneratedBy = jsonobj.get('wasGeneratedBy') or []
	used = jsonobj.get('used') or []
	wasDerivedFrom = jsonobj.get('wasDerivedFrom') or []

	for k in wasGeneratedBy:
	    #The set of all entity nodes that were "wasGeneratedBy" an activity A have creation time between activity A's start_time and end_time
	    #print "adding wasGeneratedBy edge " +str (k) + " having value =" + str(wasGeneratedBy[k])
	    activity = wasGeneratedBy[k]['prov:activity']
	    entity = wasGeneratedBy[k]['prov:entity']
	    if getField(activities, activity, 'endTime') < getField(entities, entity, 'creationTime'):
		     ret =  False, "wasGeneratedBy error for "+k+":creationTime of entity "+entity+\
		       " should be between startTime and endTime of activity "+activity
	    if getField(activities, activity, 'startTime') > getField(entities, entity, 'creationTime'):
		     ret =  False, "wasGeneratedBy error for "+k+":creationTime of entity "+entity+\
		       " should be between startTime and endTime of activity "+activity
	    provg.add_edge(entity,activity, dict(type=wasGeneratedBy, name=k) )

	for k in used:
	    #The set of all entity nodes that were "used" by an activity A have creation time less than activity A's end_time.
	    #print "adding used edge " +str (k) + " having value =" + str(used[k])
	    activity = used[k]['prov:activity']
	    entity = used[k]['prov:entity']
	    if activities[activity]['prov:endTime'] < getField(entities, entity, 'creationTime'):
		     ret =  False, "used error for "+k+":creationTime of entity "+entity+\
		       " should be before endTime of activity "+activity
	    provg.add_edge(activity,entity, dict(type=used, name=k) )
	for k in wasDerivedFrom:
	    #In the "wasDerivedBy" edge the source entity has a version number and creation time that is
	    # lower than destination entity version number and creation time, but have the same UUID.
	    entity_source = wasDerivedFrom[k]['prov:usedEntity']
	    entity_destination =wasDerivedFrom[k]['prov:generatedEntity']
	    print "source details: "
	    pprint(entities[entity_source])
	    print "destination details: "
	    pprint(entities[entity_destination])
	    if getField(entities, entity_source, 'UUID') != getField(entities, entity_destination, 'UUID'):
		     ret =  False, "wasDerivedFrom error for "+k+":UUID of entity "+entity_source+\
		       " should be the same as UUID of entity "+entity_destination
	    if getField(entities, entity_source, 'creationTime') >= getField(entities, entity_destination, 'creationTime'):
		     ret =  False, "wasDerivedFrom error for "+k+":creationTime of entity "+entity_source+\
		       " should be lower than creationTime of entity "+entity_destination
	    #if getField(entities, entity_source, 'version') >= getField(entities, entity_destination, 'version'):
	    #    ret =  False, "wasDerivedFrom error for "+k+":version of entity "+entity_source+\
	    #           " should be lower than version of entity "+entity_destination

	    print "adding wasDerivedFrom edge  " +str (k) + " having value =" + str(wasDerivedFrom[k])
	    provg.add_edge(entity_source, entity_destination, dict(type=wasDerivedFrom, name=k) )


	# remove additional

	print "-------------"
	print provg.nodes()
	print provg.edges()


def jsonid_rename(jsonobj):

    graph_uuid = "need to figure out what is a good id"
    #str(uuid.uuid3(uuid.NAMESPACE_DNS, str("need to figure out what is a good id")))
    name_mapping = {} # old_name:new_name
    entities = jsonobj.get('entity')
    activities = jsonobj.get('activity') or []

    jsonobj2 = copy.deepcopy(jsonobj)

    for k in entities:
        namespace , entity_name = k.split(':')
        #big_string = k[namespace+':UUID'] + k[namespace+':creationTime'] + k[namespace+':version']
        big_string = str(jsonobj['entity'][k][namespace+':UUID']) + \
                     str(jsonobj['entity'][k][namespace+':creationTime'])
                     #str(jsonobj['entity'][k][namespace+':version'])
        name_mapping[k] = str(uuid.uuid3(uuid.NAMESPACE_DNS, big_string))
        print "new value for entity "+str(k) +" is "+ name_mapping[k]
        #add field to identify subgraph
        jsonobj2['entity'][k]['provdb:projectID'] = graph_uuid
        # we found the new name for object, let's change it
        jsonobj2['entity'].setdefault(name_mapping[k], jsonobj2['entity'].pop(k))


    for k in activities or []:
        name_mapping[k] = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(jsonobj['activity'][k]['prov:type'])))
        print "new value for activity "+str(k) +" is "+ name_mapping[k]
        #add field to identify subgraph
        jsonobj2['activity'][k]['provdb:projectID'] = graph_uuid
        # we found the new name for object, let's change it
        jsonobj2['activity'].setdefault(name_mapping[k], jsonobj2['activity'].pop(k))


    wasGeneratedBy = jsonobj.get('wasGeneratedBy') or []
    used = jsonobj.get('used') or []
    wasDerivedFrom = jsonobj.get('wasDerivedFrom') or []
    for k in wasGeneratedBy:
        activity = wasGeneratedBy[k]['prov:activity']
        entity = wasGeneratedBy[k]['prov:entity']
        #add field to identify subgraph
        jsonobj2['wasGeneratedBy'][k]['provdb:projectID'] = graph_uuid
        # change values with new node names
        jsonobj2['wasGeneratedBy'][k]['prov:activity'] = name_mapping[activity]
        jsonobj2['wasGeneratedBy'][k]['prov:entity'] = name_mapping[entity]
    for k in used:
        activity = used[k]['prov:activity']
        entity = used[k]['prov:entity']
        #add field to identify subgraph
        jsonobj2['used'][k]['provdb:projectID'] = graph_uuid
        # change values with new node names
        jsonobj2['used'][k]['prov:activity'] = name_mapping[activity]
        jsonobj2['used'][k]['prov:entity'] = name_mapping[entity]
    for k in wasDerivedFrom:
        entity_source = wasDerivedFrom[k]['prov:usedEntity']
        entity_destination =wasDerivedFrom[k]['prov:generatedEntity']
        #add field to identify subgraph
        jsonobj2['wasDerivedFrom'][k]['provdb:projectID'] = graph_uuid
        # change values with new node names
        jsonobj2['wasDerivedFrom'][k]['prov:usedEntity'] = name_mapping[entity_source]
        jsonobj2['wasDerivedFrom'][k]['prov:generatedEntity'] = name_mapping[entity_destination]
    return jsonobj2

if __name__ == "__main__":
    # For testing
    json_data=open('C1-file1.json')
    obj = json.load(json_data)
    json_data.close()
    #xxx=PROV(obj)
    obj2 = uuid_rename(obj)
    pprint(obj2)



