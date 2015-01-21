import sys, os, datetime, decimal
import json
import network as nx

class PROV:
  """ Main PROV class that cretaes a PROV graph from JSON object and validates it. 
  """

  def __init__(self, jsonobj):
     provg  = nx.DiGraph()

     #add nodes; currently entities and activities 
     entities = obj['entity']  
     activities = obj['activity']

     for k in entities
	entity_attr_key = entities[k].keys()
	entity_attr_value = entities[k].values()
	provg.add_node()

     #add relationships


  def _validate(provgraph)


  return True    
