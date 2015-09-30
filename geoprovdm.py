import sys, os, datetime, decimal
#import dateutil.parser, calendar
import json

# http://book.py2neo.org/en/latest/fundamentals/#node-relationship-abstracts
from py2neo import neo4j, node, rel

# VERSION
_geoprovdm_version=0.75

class GeoProvDM:
  """ Main class that provides  all functionality needed
  to create entities, agents, activities and to relations among them
  """
  # global connections for neo4j
  _neo_graph = None

  # reset db command
  # neo4j (http://localhost:7474/browser/): match (n) optional match (n)-[r]-() delete n, r

  def __init__(self, environ, url = "http://localhost:7474/db/data/", cleanStart = False):
    self._neo_graph = neo4j.GraphDatabaseService(url)
    # reset the neo graph 
    if cleanStart:
      neo4j.CypherQuery(self._neo_graph,\
        "MATCH (n) WHERE n._geoprovdm_version = " + str(_geoprovdm_version) + " OPTIONAL MATCH (n)-[r]-() DELETE n, r").execute()
    ENVIRON = environ

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
    order= self._getOrder(act[u'prov:type'],act[u'provdb:projectId'])
    if order is None:
      self._addOrder(act[u'prov:type'],act[u'provdb:projectId'])
      self._addObject(self._ACTIVITY, act)
      self._updateOrder(act[u'prov:type'],act[u'provdb:projectId'])
      return True
    else:                
      isobj = self._addObject(self._ACTIVITY,act)
      if (isobj):
        old=self._getNodeInformant(act[u'prov:type'],str((int(order["provdb:order"])-1)),order["provdb:projectId"])
        if (old is not None):
      	  nodelist=json.loads(json.dumps({"prov:informed":act[u'_id'],"prov:informant":old["_id"]}))
      	  self._addRelation("wasInformedBy","_:wIB"+act[u'_id']+old['_id'],nodelist)
      	  self._updateOrder(act[u'prov:type'],act[u'provdb:projectId'])
        return True 
    
  _ENTITY = "Entity"
  def addEntity(self, entity):
    """ Add an entity to database
    
    :param entity: a dictionary of attributes of the entity
    """
    #find an entity with that UUID
    #replace that entity as the entity to be connected to

    return self._addObject(self._ENTITY, entity)
     
  _REQUESTID = "RequestId"
  def addRequestId(self,namespace):
    tmp= {}
    tmp["_id"]= namespace+":rid1" #self._REQUESTID
    tmp["provdb:type"]="RequestId"
    tmp["provdb:number"]="1"
    tmp["provdb:projectId"]=namespace
    rid= json.loads(json.dumps(tmp))
    self._addObject(self._REQUESTID, rid)
    return tmp["provdb:number"]

  _ORDER = "Order"
  def _addOrder(self,actType,namespace):
    tmp= {}
    tmp["_id"]= namespace+":"+actType #self._ORDER+actType
    tmp["provdb:type"]="Order"
    tmp["provdb:actType"]=actType
    tmp["provdb:projectId"]=namespace
    tmp["provdb:order"]="0"
    order= json.loads(json.dumps(tmp))
    return self._addObject(self._ORDER, order)  
  
  def _addObject(self, objType, obj):
    #if not obj.has_key("_id"):
    #  obj["_id"] = hex(random.getrandbits(128))[2:-1] 
    if not self._getNodeById(objType, obj["_id"]) is None:
      return False
      
    obj['_geoprovdm_version'] = _geoprovdm_version
    #if book-keeping nodes
    if objType!="RequestId" and objType!="Order":
        obj['provdb:RequestId'] = self._getRequestId(obj["provdb:projectId"])["provdb:number"]
    # if activity nodes
    if objType=="Activity":
        obj['provdb:order'] = self._getOrder(obj['prov:type'],obj["provdb:projectId"])["provdb:order"]
 
    a_node, = self._neo_graph.create(obj)
    a_node.add_labels(objType)
    return True

  def addRelation(self, relationType, name, objectIdList):    
    return self._addRelation(relationType, name, objectIdList)

  def _addRelation(self, relationType, name, objectIdList):
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
        # check if relationship prev exists and of same type
        rellist = self._neo_graph.match_one(source,(relationType,{"_id":name}),dest,False)
        if (rellist is None):
	  print relationType
	  print name
          self._neo_graph.create(rel(source, (relationType, {"_id":name}), dest))
    except KeyError:
      print "Error: Incorrect type or id list"


###**********************************************************************************


  def _getNodeById(self, nodeType, nodeId):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH (ee:" + nodeType.title() + ") WHERE ee._id = {p_id} RETURN ee;")
    node = query.execute_one(p_id = nodeId)
    return node


  def _getNodeInformant(self, actId,order,namespace):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH (ee:Activity) WHERE ee.`prov:type` = {act} AND ee.`provdb:order`={a_order} and ee.`provdb:projectId` = {namespace} RETURN ee;")
    node = query.execute_one(act = actId,a_order=order,namespace=namespace)
    return node

  def _getRequestId(self,namespace):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH (rId:RequestId) where rId.`provdb:projectId` = {namespace} RETURN rId;")
    node = query.execute_one(namespace=namespace)
    return node

  def getRequestId(self,namespace):
    return self._getRequestId(namespace)

  def updateRequestId(self,namespace):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH (rId:RequestId) where rId.`provdb:projectId` = {namespace} RETURN rId;")
    node = query.execute_one(namespace=namespace)
    tmp=node["provdb:number"]
    node["provdb:number"]=str(int(tmp)+1)
    return node["provdb:number"]

  def _updateOrder(self,actType,namespace):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH (o:Order) Where o.`provdb:actType`={atype} and o.`provdb:projectId` = {namespace} RETURN o;")
    node = query.execute_one(atype=actType,namespace=namespace)
    tmp=node["provdb:order"]
    node["provdb:order"]=str(int(tmp)+1)
    return node

  def _getOrder(self,actType,namespace):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH (o:Order) Where o.`provdb:actType`={atype} and o.`provdb:projectId` = {namespace} RETURN o;")
    node = query.execute_one(atype=actType,namespace=namespace)
    return node

  def getOrder(self,actType,namespace):
    return self._getOrder(actType,namespace)

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
    'wasEndedBy':['activity', 'entity'], \
    'sameAs':['entity','entity']}

  def getRequiredIdsInRelation(self):
    return self._requiredIdsInRelation

 

############################
#Retrieve PROV-DM compliant provenance about the resource with the given 'uuid'.
  def getNodeByUuid(self, namespace, nodeUuid):
    str = 'MATCH path = (en:Entity)-[*..2]->a \
	WHERE en.`%(namespace1)s:UUID` = "%(p_uuid)s" \
	AND NOT ()-[:wasInformedBy]->a  \
	RETURN path;' %{"namespace1":namespace,"p_uuid":nodeUuid}
    query = neo4j.CypherQuery(self._neo_graph,str)
    result = query.execute()

    #query = neo4j.CypherQuery(self._neo_graph, \
    #  "Start en=node(*)\
    #  MATCH path = en-[*..2]->a \
    #  WHERE en.`{namespace1}:UUID` = \"{p_uuid}\" \
    #  AND NOT ()-[:wasInformedBy]->a  \
    #  RETURN path;")
    #result = query.execute(namespace1=namespace,p_uuid = nodeUuid)
    return result  

  def deleteNodeByUuid(self, namespace,uuid):
      # TM: No clue why the statements below will not work.
      #query = neo4j.CypherQuery(self._neo_graph, \
      #	"MATCH (n {`{namespace1}:UUID` : \"{uuid1}\"}) RETURN n;")
      #node = query.execute_one(namespace1=namespace.strip(),uuid1 = uuid.strip())
    str = "MATCH (n:Entity {`"+namespace+":UUID` : \""+uuid+"\"}) RETURN n;"
    query = neo4j.CypherQuery(self._neo_graph, str)
    #node = query.execute_one() 
    results = query.execute() 
    if (results is not None):
      for r in results:
         print r
         node = r[0] 
         props = node.get_properties()
         print props
         requestId = node["provdb:RequestId"]
         self.deleteNodeByRequestid(namespace,requestId)
      return True
    else:
      return False
 

  def deleteNodeByRequestid(self, namespace,rid):
    query = neo4j.CypherQuery(self._neo_graph, \
	"MATCH (n {`provdb:RequestId` : {rid}}) OPTIONAL MATCH (n)-[r]-() DELETE r;")
    result = query.execute(rid = rid)
	
    query = neo4j.CypherQuery(self._neo_graph, \
	"MATCH (n {`provdb:RequestId` : {rid}}) DELETE n;")
    result = query.execute(rid = rid)
    return result
 
#Retrieve PROV-DM compliant provenance  of a resource with a given 'uuid', and which has activity 'activityname' in its path
  def getNodeByUuidWithActivity(self, nodeUuid, activityname):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH path = (en:Entity)-[*..]->a,(act:Activity) \
      WHERE en.`foundry:UUID` = {p_uuid} AND  act.`prov:type`={aname} AND act IN nodes(path)\
      RETURN path;") 
    result = query.execute(p_uuid = nodeUuid, aname=activityname)
    return result

# #Retrieve PROV-DM compliant provenance  of a resource with a given ''uuid', and which was generated by resource UUID2
  def getNodeByUuidwasGeneratedBy(self, enUuid, UUID2):        #UUID2 must be Activity,enUuid must be Entity
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH path = (en:Entity)-[*..]->a, en-[r:`wasGeneratedBy`]->(act:Activity) \
      WHERE en.`foundry:UUID` = {p_uuid} AND act._id = {aid} \
      RETURN path;")
    result = query.execute(p_uuid = enUuid, aid = UUID2)
    return result

#Retrieve PROV-DM compliant provenance  of a resource with a given 'uuid', and which generated resource UUID2
  def getNodeByUuidGenerate(self, acUuid, UUID2):   #UUID2 must be Entity, acUuid must be Activity
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH path = a-[*..]->act, (en:Entity)-[r:`wasGeneratedBy`]->act \
      WHERE en.`foundry:UUID` = {p_uuid} AND act._id = {aid} \
      RETURN path;")
    result = query.execute(p_uuid = UUID2, aid = acUuid)
    return result

#Retrieve PROV-DM compliant provenance  of a resource with a given ''uuid', which has activity 'activity name' and resource 'id2' in its ancestral path
  def getNodeByUuidWithAncestral(self, nodeUuid, activityname, id2):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH path = (en:Entity)-[*..]->a,(act:Activity), (e:Entity) \
      WHERE en.`foundry:UUID` = {p_uuid} AND  act.`prov:type`={aname}\
      AND e._id = {rid2} AND act IN nodes(path) AND e IN nodes(path)\
      RETURN path;")  
    result= query.execute(p_uuid = nodeUuid, aname= activityname,rid2= id2)
    return result

#Retrieve PROV-DM compliant provenance  of a resource with a given ''uuid', which has activity 'activity name' and resource 'id2' in its forward path
  def getNodeByUuidWithForward(self, nodeUuid, activityname, id2):
    query = neo4j.CypherQuery(self._neo_graph, \
      "MATCH path = (en:Entity)<-[*..]-a,(act:Activity), (e:Entity) \
      WHERE en.`foundry:UUID` = {p_uuid} AND  act.`prov:type`={aname}\
      AND e._id = {rid2} AND act IN nodes(path) AND e IN nodes(path)\
      RETURN path;")  
    result = query.execute(p_uuid = nodeUuid, aname= activityname,rid2= id2)
    return result


#Retrieve PROV-DM compliant provenance  of all resources used by an activity 'activity name' between time 'datetime1' and 'datetime2'
  def getNodeUsedByActivityWithTimestamp(self, activityname, datetime1, datetime2):
    query = neo4j.CypherQuery(self._neo_graph, \
     "MATCH path = (act:Activity)-[r:`used`]->a \
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
      "MATCH path = (en:Entity)-[r:`wasGeneratedBy`]->(act:Activity) \
      WHERE act.`prov:type`={aname}\
      AND ((act.`prov:startTime`>={t1} AND act.`prov:startTime`<={t2})\
      OR (act.`prov:endTime`>={t1} AND act.`prov:endTime`>={t2})\
      OR (act.`prov:startTime`<{t1} AND act.`prov:endTime`>{t2}))\
      RETURN path;") 
    result = query.execute(aname=activityname, t1= datetime1, t2 = datetime2)
    return result

  
