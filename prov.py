import sys, os, datetime, decimal
import json
import networkx as nx
from pprint import pprint

class PROV:
    """ Main PROV class that cretaes a PROV graph from JSON object and validates it.
    """


    def __init__(self, jsonobj):
        def is_invalid_date(input_date_time):
            #from time import mktime, strptime
            from datetime import datetime

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

        provg  = nx.DiGraph()

        #add nodes; currently entities and activities
        entities = jsonobj.get('entity')
        if entities is None:
            return False, "there are no entities"
        activities = jsonobj.get('activity') or []

        for k in entities:
            #print "adding entity " +str (k) + " having value ="
            #pprint(entities[k])
            if entities[k].get('foundry:UUID') is None:
                ret = False, "there is no UUID in entity "+k
            if entities[k].get('foundry:creationTime') is None:
                ret = False, "there is no creationTime in entity "+k
            if entities[k].get('foundry:version') is None:
                ret = False, "there is no version in entity "+k
            if is_invalid_date(entities[k]['foundry:creationTime']['$']):
                ret = False, "invalid creationTime format in entity "+k

            print entities[k]['foundry:creationTime']['$']
            provg.add_node(k, entities.get(k) )
        for k in activities:
            print "adding activity " +str (k) + " having value ="
            pprint(activities[k])
            if activities[k].get('prov:type') is None:
                ret =  False, "there is no type in activity "+k
            if activities[k].get('prov:startTime') is None:
                ret =  False, "there is no startTime in activity "+k
            if activities[k].get('prov:endTime') is None:
                ret =  False, "there is no endTime in activity "+k
            if activities[k]['prov:endTime'] > activities[k]['prov:startTime']:
                ret =  False, "startTime should be before endTime in activity "+k

            if is_invalid_date(activities[k]['prov:startTime']):
                ret = False, "invalid startTime format in activity "+k
            if is_invalid_date(activities[k]['prov:endTime']):
                ret = False, "invalid endTime format in activity "+k


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
            if activities[activity]['prov:endTime'] < entities[entity]['foundry:creationTime']:
                ret =  False, "wasGeneratedBy error for "+k+":creationTime of entity "+entity+\
                       " should be between startTime and endTime of activity "+activity
            if activities[activity]['prov:startTime'] < entities[entity]['foundry:creationTime']:
                ret =  False, "wasGeneratedBy error for "+k+":creationTime of entity "+entity+\
                       " should be between startTime and endTime of activity "+activity
            provg.add_edge(entity,activity, dict(type=wasGeneratedBy, name=k) )
        for k in used:
            #The set of all entity nodes that were "used" by an activity A have creation time less than activity A's end_time.
            #print "adding used edge " +str (k) + " having value =" + str(used[k])
            activity = used[k]['prov:activity']
            entity = used[k]['prov:entity']
            if activities[activity]['prov:endTime'] < entities[entity]['foundry:creationTime']:
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
            if entities[entity_source]['foundry:UUID'] != entities[entity_destination]['foundry:UUID']:
                ret =  False, "wasDerivedFrom error for "+k+":UUID of entity "+entity_source+\
                       " should be the same as UUID of entity "+entity_destination
            if entities[entity_source]['foundry:creationTime'] >= entities[entity_destination]['foundry:creationTime']:
                ret =  False, "wasDerivedFrom error for "+k+":creationTime of entity "+entity_source+\
                       " should be lower than creationTime of entity "+entity_destination
            if entities[entity_source]['foundry:version'] >= entities[entity_destination]['foundry:version']:
                ret =  False, "wasDerivedFrom error for "+k+":version of entity "+entity_source+\
                       " should be lower than version of entity "+entity_destination

            print "adding wasDerivedFrom edge  " +str (k) + " having value =" + str(wasDerivedFrom[k])
            provg.add_edge(entity_source, entity_destination, dict(type=wasDerivedFrom, name=k) )
        print "-------------"
        print provg.nodes()
        print provg.edges()

    def _validate(self, provgraph):

        return True


if __name__ == "__main__":
    # For testing


    json_data=open('C1-file1.json')
    obj = json.load(json_data)
    json_data.close()
    xxx=PROV(obj)


