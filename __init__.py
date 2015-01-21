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

import os
from flask import  abort, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
users_db = SQLAlchemy(app)
auth = HTTPBasicAuth()

#in this case, neo4j server and flask server are on the same machine, same SERVER_IP
SERVER_IP="127.0.0.1"

ENVIRON = os.environ.get('PROV_ENVIRON')
if (ENVIRON == None):
   ENVIRON = 'PROD'

db = GeoProvDM(ENVIRON, "http://%s:7474/db/data/"%SERVER_IP, False)

@app.route("/provenance/test")
def hello():
    return "Hello World!"

class User(users_db.Model):
    __tablename__ = 'users'
    id = users_db.Column(users_db.Integer, primary_key=True)
    username = users_db.Column(users_db.String(32), index=True)
    password_hash = users_db.Column(users_db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    users_db.session.add(user)
    users_db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/provenance/resource', methods=['POST'])
@auth.login_required
def create_resource_prov():

    # Atleast one entity should be present
    if not request.json or not 'entity' in request.json:
        return Response(status=400)

    obj = request.json
    obj = jsonRefresh(obj) 
    # make all entities
    if 'entity' in obj:
        if db.getRequestId() is None:
            requestId = db.addRequestId()
        else:
            requestId = db.updateRequestId()  	

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

    data = {"request id: ": requestId, "provenance submitted at": datetime.datetime.utcnow(), "submitted provenance": obj}
    return Response(dumps(data,default=outputJSON), mimetype='application/json',status=201)


@app.route('/provenance/b/resource/<string:uuid>', methods=['GET'])
@auth.login_required
def get_resource_provenance(uuid):
 
  #obj = db.getSubgraph(uuid)
  uuid1 = uuid
  obj = db.getNodeByUuid(uuid1)
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)

@app.route('/resource/<string:uuid>', methods=['DELETE'])
@auth.login_required
def delete_resource_provenance(uuid):
  uuid1 = uuid
  obj = db.deleteNodeByUuid(uuid1)
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)

@app.route('/provenance/b/resource/<string:uuid>/activity/<string:activityproperty>', methods=['GET'])
@auth.login_required
def get_resource_provenance_with_uuid_activityproperty(uuid,aprop):
  uuid1 = uuid
  aprop1 = aprop
  obj = db.getNodeByUuidWithActivity(uuid1,aprop1)
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)

@app.route('/provenance/<string:direction>/resource/<string:resourceproperty>', methods=['GET'])
@auth.login_required
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
@auth.login_required
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
@auth.login_required
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
    if not os.path.exists('users_db.sqlite'):
        users_db.create_all()
    app.run(host=SERVER_IP, port=5000, debug=True)