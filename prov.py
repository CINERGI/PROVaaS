import sys, os, decimal
import json
import networkx as nx
from pprint import pprint
import uuid
from time import strptime
import copy
from dateutil import parser
from pytz import utc
import calendar
#from datetime import datetime, timedelta
import datetime #, timedelta

#"2014-11-01T00:06:00" ,  "2015-02-02T12:39:51-08:00"
#DATETIME_FORMATS = ['%Y-%m-%dT%H:%M:%S' , '%Y-%m-%dT%H:%M:%S%:z' ]

# checks if input string contains a date in one of acceptable date-time formats
def is_valid_date(input_date_time):
    result = None

    #for format in DATETIME_FORMATS:
    try:
        result = parser.parse(input_date_time) #(input_date_time, format)

    except:
        print "Unexpected error:", sys.exc_info()[0]
        pass

    if result is None:
        # print 'Malformed date.'
        return False
    else:
        # print 'Date is fine.'
        return True
    return True


# returns a "date" format from a string containing a date in one of acceptable date-time formats
def get_date(input_date_time):
    result = None
    print input_date_time
    try:
        result = parser.parse(input_date_time)
    except:
        pass

    if result.tzinfo is None:
        return utc.localize(result)
    else:
        return result

# returns value of a field of an element from a list of elements
def getField(elementsList, element, filedId):
  return elementsList[element][elementsList[element]['__namespace']+':'+filedId]


def validateJSONRequest(jsonobj):

    provg  = nx.DiGraph()

        #check that project field is in json request
        #projectId = jsonobj.get('provdb:projectId') or ""
        #if projectId == "":
        #    return False, "There is no projectId specified in JSON request"

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
            return False, "There is no UUID in entity "+k
        if entities[k].get(namespace+':creationTime') is None:
            return False, "There is no creationTime in entity "+k
        if entities[k].get(namespace+':version') is None:
            return False, "There is no version in entity "+k
        if not is_valid_date(entities[k][namespace+':creationTime']['$']):
            return False, "Invalid creationTime format in entity "+k

        entities[k]['__namespace'] = namespace
        #print entities[k][namespace+':creationTime']['$']
        # All good with entity
        provg.add_node(k, entities.get(k) )

    for k in activities:
        namespace , entity_name = k.split(':')
        #print "adding activity " +str (k) + " having value ="
        #pprint(activities[k])
        if activities[k].get('prov:type') is None:
            return  False, "There is no type in activity "+k
        if activities[k].get('prov:startTime') is None:
            return  False, "There is no startTime in activity "+k
        if activities[k].get('prov:endTime') is None:
            return  False, "There is no endTime in activity "+k
        if get_date(activities[k]['prov:endTime']) < \
                get_date(activities[k]['prov:startTime']):
            return  False, "StartTime should be before endTime in activity "+k

        if not is_valid_date(activities[k]['prov:startTime']):
            return False, "Invalid startTime format in activity "+k
        if not is_valid_date(activities[k]['prov:endTime']):
            return False, "Invalid endTime format in activity "+k

        activities[k]['__namespace'] = 'prov' #namespace
        
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
        if get_date(getField(activities, activity, 'endTime')) < \
            get_date(getField(entities, entity, 'creationTime')['$']):
                return  False, "wasGeneratedBy error for "+k+":creationTime of entity "+entity+\
               " should be between startTime and endTime of activity "+activity
        if get_date(getField(activities, activity, 'startTime')) > \
            get_date(getField(entities, entity, 'creationTime')['$']):
                return  False, "wasGeneratedBy error for "+k+":creationTime of entity "+entity+\
               " should be between startTime and endTime of activity "+activity
        provg.add_edge(entity,activity, dict(type=wasGeneratedBy, name=k) )

    for k in used:
        #The set of all entity nodes that were "used" by an activity A have creation time less than activity A's end_time.
        #print "adding used edge " +str (k) + " having value =" + str(used[k])
        activity = used[k]['prov:activity']
        entity = used[k]['prov:entity']
        if get_date(getField(activities,activity,'endTime')) < get_date(getField(entities, entity, 'creationTime')['$']):
            return  False, "used error for "+k+":creationTime of entity "+entity+\
                " should be before endTime of activity "+activity
        provg.add_edge(activity,entity, dict(type=used, name=k) )
    for k in wasDerivedFrom:
        #In the "wasDerivedBy" edge the source entity has a version number and creation time that is
        # lower than destination entity version number and creation time, but have the same UUID.
        entity_source = wasDerivedFrom[k]['prov:usedEntity']
        entity_destination =wasDerivedFrom[k]['prov:generatedEntity']
        #print "source details: "
        #pprint(entities[entity_source])
        #print "destination details: "
        #pprint(entities[entity_destination])
        if getField(entities, entity_source, 'UUID') != getField(entities, entity_destination, 'UUID'):
            return  False, "wasDerivedFrom error for "+k+":UUID of entity "+entity_source+\
               " should be the same as UUID of entity "+entity_destination
        if get_date(getField(entities, entity_source, 'creationTime')) >= \
                get_date(getField(entities, entity_destination, 'creationTime')):
            return  False, "wasDerivedFrom error for "+k+":creationTime of entity "+entity_source+\
               " should be lower than creationTime of entity "+entity_destination
        #if getField(entities, entity_source, 'version') >= getField(entities, entity_destination, 'version'):
        #    return  False, "wasDerivedFrom error for "+k+":version of entity "+entity_source+\
        #           " should be lower than version of entity "+entity_destination

        #print "adding wasDerivedFrom edge  " +str (k) + " having value =" + str(wasDerivedFrom[k])
        provg.add_edge(entity_source, entity_destination, dict(type=wasDerivedFrom, name=k) )


    # remove additional

    #print "-------------"
    #print provg.nodes()
    #print provg.edges()
    return True,"validation successful"


def jsonid_rename(jsonobj):
 
    #graph_uuid = projectId #"need to figure out what is a good id"
    #str(uuid.uuid3(uuid.NAMESPACE_DNS, str("need to figure out what is a good id")))
    name_mapping = {} # old_name:new_name
    namespace = None
    entities = jsonobj.get('entity')
    activities = jsonobj.get('activity') or []

    jsonobj2 = copy.deepcopy(jsonobj)

    for k in entities:
        namespace , entity_name = k.split(':')
        namespace = namespace
        #big_string = k[namespace+':UUID'] + k[namespace+':creationTime'] + k[namespace+':version']
        big_string = str(namespace) + str(jsonobj['entity'][k][namespace+':UUID']) + \
                   str(jsonobj['entity'][k][namespace+':creationTime'])
                     #str(jsonobj['entity'][k][namespace+':version'])
        name_mapping[k] = str(uuid.uuid3(uuid.NAMESPACE_DNS, big_string))
        #print "new value for entity "+str(k) +" is "+ name_mapping[k]
        #add field to identify subgraph
        jsonobj2['entity'][k]['provdb:projectId'] = namespace #graph_uuid
        # we found the new name for object, let's change it
        jsonobj2['entity'].setdefault(name_mapping[k], jsonobj2['entity'].pop(k))


    for k in activities or []:
        big_string = str(namespace) + str(jsonobj['activity'][k]['prov:type']) + \
                   str(jsonobj['activity'][k]['prov:startTime']) + \
                   str(jsonobj['activity'][k]['prov:endTime'])
                     #str(jsonobj['entity'][k][namespace+':version'])
        name_mapping[k] = str(uuid.uuid3(uuid.NAMESPACE_DNS, big_string))

        #name_mapping[k] = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(jsonobj['activity'][k]['prov:type'])))
        #print "new value for activity "+str(k) +" is "+ name_mapping[k]
        #add field to identify subgraph
        jsonobj2['activity'][k]['provdb:projectId'] = namespace #graph_uuid
        # we found the new name for object, let's change it
        jsonobj2['activity'].setdefault(name_mapping[k], jsonobj2['activity'].pop(k))


    wasGeneratedBy = jsonobj.get('wasGeneratedBy') or []
    used = jsonobj.get('used') or []
    wasDerivedFrom = jsonobj.get('wasDerivedFrom') or []
    for k in wasGeneratedBy:
        activity = wasGeneratedBy[k]['prov:activity']
        entity = wasGeneratedBy[k]['prov:entity']
        big_string = str(namespace) + str("activity") + str(jsonobj['wasGeneratedBy'][k]['prov:activity']) + \
                   str(jsonobj['wasGeneratedBy'][k]['prov:entity'])

        name_mapping[k] = str(uuid.uuid3(uuid.NAMESPACE_DNS, big_string))
        #add field to identify subgraph
        jsonobj2['wasGeneratedBy'][k]['provdb:projectId'] = namespace#graph_uuid
        # change values with new node names
        jsonobj2['wasGeneratedBy'][k]['prov:activity'] = name_mapping[activity]
        jsonobj2['wasGeneratedBy'][k]['prov:entity'] = name_mapping[entity]

        jsonobj2['wasGeneratedBy'].setdefault(name_mapping[k], jsonobj2['wasGeneratedBy'].pop(k))

    for k in used:
        activity = used[k]['prov:activity']
        entity = used[k]['prov:entity']
        big_string = str(namespace) + str("used") + str(jsonobj['used'][k]['prov:activity']) + \
                   str(jsonobj['used'][k]['prov:entity'])

        name_mapping[k] = str(uuid.uuid3(uuid.NAMESPACE_DNS, big_string))
        #add field to identify subgraph
        jsonobj2['used'][k]['provdb:projectId'] = namespace #graph_uuid
        # change values with new node names
        jsonobj2['used'][k]['prov:activity'] = name_mapping[activity]
        jsonobj2['used'][k]['prov:entity'] = name_mapping[entity]
        jsonobj2['used'].setdefault(name_mapping[k], jsonobj2['used'].pop(k))

    for k in wasDerivedFrom:
        entity_source = wasDerivedFrom[k]['prov:usedEntity']
        entity_destination =wasDerivedFrom[k]['prov:generatedEntity']

        big_string = str(namespace) + str("wasDerivedFrom") + str(jsonobj['wasDerivedFrom'][k]['prov:generatedEntity']) + \
                   str(jsonobj['wasDerivedFrom'][k]['prov:usedentity'])

        name_mapping[k] = str(uuid.uuid3(uuid.NAMESPACE_DNS, big_string))
        #add field to identify subgraph
        jsonobj2['wasDerivedFrom'][k]['provdb:projectId'] = namespace #graph_uuid
        # change values with new node names
        jsonobj2['wasDerivedFrom'][k]['prov:usedEntity'] = name_mapping[entity_source]
        jsonobj2['wasDerivedFrom'][k]['prov:generatedEntity'] = name_mapping[entity_destination]
        jsonobj2['wasDerivedFrom'].setdefault(name_mapping[k], jsonobj2['wasDerivedFrom'].pop(k))
    return namespace,jsonobj2

if __name__ == "__main__":
    # For testing
    json_data=open('C1-file1.json')
    obj = json.load(json_data)
    json_data.close()
    #xxx=PROV(obj)
    obj2 = jsonid_rename(obj)
    pprint(obj2)



