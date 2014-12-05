import sys, os, datetime, decimal

# http://book.py2neo.org/en/latest/fundamentals/#node-relationship-abstracts
from py2neo import neo4j, node, rel

# VERSION
_geoprovdm_version=0.1

class GeoProvDM:
  """ Main class that provides  all functionality needed
  to create entities, agents, activities and to relations among them
  """
  # global connections for neo4j
  _neo_graph = None

  # reset db command
  # neo4j (http://localhost:7474/browser/): match (n) optional match (n)-[r]-() delete n, r

  def __init__(self, url = "http://localhost:7474/db/data/", cleanStart = False):
    self._neo_graph = neo4j.GraphDatabaseService(url)
    # reset the neo graph 
    if cleanStart:
      neo4j.CypherQuery(self._neo_graph,\
        "MATCH (n) WHERE n._geoprovdm_version = " + str(_geoprovdm_version) + " OPTIONAL MATCH (n)-[r]-() DELETE n, r").execute()

  _AGENT = "Agent"
  def addAgent(self, agent):
    """ Add an agent to database
  
    :param agent: a dictionary of attributes of the agent
    """
    return self._addObject(self._AGENT, agent)
    
  _ACTIVITY = "Activity"
  def addActivity(self, act):
    """ Add an activity to database
    
    :param act: a dictionary of attributes of the activity
    """
    return self._addObject(self._ACTIVITY, act)
    
  _ENTITY = "Entity"
  def addEntity(self, entity):
    """ Add an entity to database
    
    :param entity: a dictionary of attributes of the entity
    """
    return self._addObject(self._ENTITY, entity)
    
  def _addObject(self, objType, obj):
    if not obj.has_key("_id"):
      obj["_id"] = hex(random.getrandbits(128))[2:-1] 
    elif not self._getNodeById(objType, obj["_id"]) is None:
      return False
      
    obj['_geoprovdm_version'] = _geoprovdm_version
    a_node, = self._neo_graph.create(obj)
    a_node.add_labels(objType)
    return True
    
  def addRelation(self, relationType, name, objectIdList):
    """ Add a relation to database
    
    :param relationType: one of the relation type specified in requiredIdsInRelation
    :param name: name of the relation
    :param objectIdList: a dictionary o f2 object identities of source and dest 
    of the relation specified as 'prov:xxx' where xxx is entity, agent, or activity
    """
    try:
      sType = self._requiredIdsInRelation[relationType][0]
      dType = self._requiredIdsInRelation[relationType][1]
      if relationType=='wasDerivedFrom':
        if 'prov:generatedEntity' in objectIdList:
          sId = objectIdList['prov:generatedEntity']
        if 'prov:usedEntity' in objectIdList:
          dId = objectIdList['prov:usedEntity']
      elif relationType=='wasInformedBy':
        if 'prov:informed' in objectIdList:
          sId = objectIdList['prov:informed']
        if 'prov:informant' in objectIdList:
          dId = objectIdList['prov:informant']
      elif relationType=='actedOnBehalfOf': 
        if 'prov:delegate' in objectIdList:
          sId = objectIdList['prov:delegate']
        if 'prov:responsible' in objectIdList:
          dId = objectIdList['prov:responsible']
      elif relationType=='wasStartedBy' or relationType=='wasEndedBy': 
        if 'prov:activity' in objectIdList:
          sId = objectIdList['prov:activity']
        if 'prov:trigger' in objectIdList:
          dId = objectIdList['prov:trigger']
      else:
          sId = objectIdList['prov:'+ sType]
          dId = objectIdList['prov:'+ dType]              
      #~ print "addRelation", relationType, name, sId, dId
      if sId is not None:
          source = self._getNodeById(sType, sId)
      if dId is not None:
          dest = self._getNodeById(dType, dId)
      if not (source is None or dest is None):
        self._neo_graph.create(rel(source, (relationType, {"name":name}), dest))
    except KeyError:
      print "Error: Incorrect type or id list"

  def _getNodeById(self, nodeType, nodeId):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH (ee:" + nodeType.title() + ") WHERE ee._id = {p_id} RETURN ee;")
    node = query.execute_one(p_id = nodeId)
    return node

  #'used':['activity', 'entity'], 
  _requiredIdsInRelation = {'wasAssociatedWith':['activity', 'agent'],\
    'used':['activity', 'entity'],\
    'wasInvalidatedBy':['entity', 'activity'], \
    'wasGeneratedBy':['entity', 'activity'], \
    'wasAttributedTo':['entity', 'agent'], \
    'wasDerivedFrom':['entity', 'entity'], \
    'actedOnBehalfOf':['agent', 'agent'], \
    'wasInformedBy':['activity', 'activity'],\
    'wasStartedBy':['activity', 'entity'], \
    'wasEndedBy':['activity', 'entity']}

  def getRequiredIdsInRelation(self):
    return self._requiredIdsInRelation

 

############################
#Retrieve PROV-DM compliant provenance about the resource with the given 'uuid'.
  def getNodeByUuid(self, nodeUuid):
    query = neo4j.CypherQuery(self._neo_graph, \
      "Start en=node(*)\
      MATCH path = en-[*..]->a \
      WHERE en.`foundry:UUID` = {p_uuid} \
      RETURN path;")
    result = query.execute(p_uuid = nodeUuid)
    return result  #*

  def deleteNodeByUuid(self, nodeUuid):
      query = neo4j.CypherQuery(self._neo_graph, \
	"MATCH (n {`_id` : {p_uuid}}) OPTIONAL MATCH (n)-[r]-() DELETE n,r;")
      result = query.execute(p_uuid = nodeUuid)
      return result
 
#Retrieve PROV-DM compliant provenance  of a resource with a given 'uuid', and which has activity 'activityname' in its path
  def getNodeByUuidWithActivity(self, nodeUuid, activityname):
    query = neo4j.CypherQuery(self._neo_graph, \
      "Start en=node(*)\
      MATCH path = en-[*..]->a,(act:Activity) \
      WHERE en.`foundry:UUID` = {p_uuid} AND  act.`prov:type`={aname} AND act IN nodes(path)\
      RETURN path;") 
    result = query.execute(p_uuid = nodeUuid, aname=activityname)
    return result

# #Retrieve PROV-DM compliant provenance  of a resource with a given ''uuid', and which was generated by resource UUID2
  def getNodeByUuidwasGeneratedBy(self, enUuid, UUID2):        #UUID2 must be Activity,enUuid must be Entity
    query = neo4j.CypherQuery(self._neo_graph, \
      "Start en=node(*)\
      MATCH path = en-[*..]->a, en-[r:`wasGeneratedBy`]->(act:Activity) \
      WHERE en.`foundry:UUID` = {p_uuid} AND act._id = {aid} \
      RETURN path;")
    result = query.execute(p_uuid = enUuid, aid = UUID2)
    return result

#Retrieve PROV-DM compliant provenance  of a resource with a given 'uuid', and which generated resource UUID2
  def getNodeByUuidGenerate(self, acUuid, UUID2):   #UUID2 must be Entity, acUuid must be Activity
    query = neo4j.CypherQuery(self._neo_graph, \
      "Start act=node(*)\
      MATCH path = a-[*..]->act, (en:Entity)-[r:`wasGeneratedBy`]->act \
      WHERE en.`foundry:UUID` = {p_uuid} AND act._id = {aid} \
      RETURN path;")
    result = query.execute(p_uuid = UUID2, aid = acUuid)
    return result

#Retrieve PROV-DM compliant provenance  of a resource with a given ''uuid', which has activity 'activity name' and resource 'id2' in its ancestral path
  def getNodeByUuidWithAncestral(self, nodeUuid, activityname, id2):
    query = neo4j.CypherQuery(self._neo_graph, \
      "Start en=node(*)\
      MATCH path = en-[*..]->a,(act:Activity), (e:Entity) \
      WHERE en.`foundry:UUID` = {p_uuid} AND  act.`prov:type`={aname}\
      AND e._id = {rid2} AND act IN nodes(path) AND e IN nodes(path)\
      RETURN path;")  
    result= query.execute(p_uuid = nodeUuid, aname= activityname,rid2= id2)
    return result

#Retrieve PROV-DM compliant provenance  of a resource with a given ''uuid', which has activity 'activity name' and resource 'id2' in its forward path
  def getNodeByUuidWithForward(self, nodeUuid, activityname, id2):
    query = neo4j.CypherQuery(self._neo_graph, \
      "Start en=node(*)\
      MATCH path = en<-[*..]-a,(act:Activity), (e:Entity) \
      WHERE en.`foundry:UUID` = {p_uuid} AND  act.`prov:type`={aname}\
      AND e._id = {rid2} AND act IN nodes(path) AND e IN nodes(path)\
      RETURN path;")  
    result = query.execute(p_uuid = nodeUuid, aname= activityname,rid2= id2)
    return result


#Retrieve PROV-DM compliant provenance  of all resources used by an activity 'activity name' between time 'datetime1' and 'datetime2'
  def getNodeUsedByActivityWithTimestamp(self, activityname, datetime1, datetime2):
    query = neo4j.CypherQuery(self._neo_graph, \
     "Start act=node(*)\
      MATCH path = act-[r:`used`]->a \
      WHERE act.`prov:type`={aname}\
      AND ((act.`prov:startTime`>={t1} AND act.`prov:startTime`<={t2})\
      OR (act.`prov:endTime`>={t1} AND act.`prov:endTime`>={t2})\
      OR (act.`prov:startTime`<{t1} AND act.`prov:endTime`>{t2}))\
      RETURN path;") 
    result = query.execute(aname=activityname, t1= datetime1, t2 = datetime2)
    return result

# #Retrieve PROV-DM compliant provenance  of all resources generated by 'activity name' between time 'dateime1' and 'datetime2'
  def getNodeGeneratedByActivityWithTimestamp(self, activityname, datetime1, datetime2):
    query = neo4j.CypherQuery(self._neo_graph, \
      "Start en=node(*)\
      MATCH path = (en:Entity)-[r:`wasGeneratedBy`]->(act:Activity) \
      WHERE act.`prov:type`={aname}\
      AND ((act.`prov:startTime`>={t1} AND act.`prov:startTime`<={t2})\
      OR (act.`prov:endTime`>={t1} AND act.`prov:endTime`>={t2})\
      OR (act.`prov:startTime`<{t1} AND act.`prov:endTime`>{t2}))\
      RETURN path;") 
    result = query.execute(aname=activityname, t1= datetime1, t2 = datetime2)
    return result

  
