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
from flask import Flask, request, Response, jsonify, send_from_directory
#from jsonhelp import *
from help_json import *
from geoprovdm import *
from prov import *

import os
from flask import  abort, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from flask import request
from logging.handlers import TimedRotatingFileHandler
import datetime
import logging
import traceback

'''
set environment variables:
    AWS_ACCESS_KEY_ID - Your AWS Access Key ID
    AWS_SECRET_ACCESS_KEY - Your AWS Secret Access Key
'''
import boto.sqs
from boto.sqs.message import Message

conn = boto.sqs.connect_to_region("us-west-2")#, aws_access_key_id=access_key, aws_secret_access_key = secret_key)
provaas_queue = conn.create_queue('provaas_queue_v1')

# initialization
app = Flask(__name__) #, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
handler = TimedRotatingFileHandler('/var/www/provaas/provaas_requests.log',when="d",interval=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# extensions
users_db = SQLAlchemy(app)
if not os.path.exists('users_db.sqlite'):
   users_db.create_all()
auth = HTTPBasicAuth()

#in this case, neo4j server and flask server are on the same machine, same SERVER_IP
SERVER_IP="127.0.0.1"

ENVIRON = os.environ.get('PROV_ENVIRON')
if (ENVIRON == None):
   ENVIRON = 'PROD'

db = GeoProvDM(ENVIRON, "http://%s:7474/db/data/"%SERVER_IP, False)

@app.before_request
def log_request():
    print  "Now logging"
    now = datetime.datetime.now()
    if request.authorization is None:
        username = "NoUser"
    else:
        username = request.authorization.username
    log_string = "%s user:%s baseUrl:%s data=%s" %\
                 (now.strftime("%Y-%m-%d %H:%M:%S"), username, request.base_url, request.data)
    print log_string
    #print  app.getlogger()
    app.logger.info(log_string)
    return

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
    print "HEre1"
    if not user:
        # try to authenticate with username/password
        print "here2"
        user = User.query.filter_by(username=username_or_token).first()
        print "here3"
        if not user or not user.verify_password(password):
            print "here4"
            return False
    g.user = user
    print "here5"
    return True


@app.route('/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    try:
        user = User(username=username)
        user.hash_password(password)
        users_db.session.add(user)
        users_db.session.commit()
    except:
        e = sys.exc_info()
        print "Errorx:",e
        traceback.print_exc()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/resource')
@auth.login_required
def get_resource():
    print "Here we reached"
    return jsonify({'data': 'Hello, %s!' % g.user.username})
    #return jsonify({'data': 'Hello, "Tanu"'})  #%s!' % g.user.username})

@app.route('/provenance/', methods=['POST'])
@auth.login_required
def create_resource_prov():


    obj = request.json
    #validate obj
    isvalid,message = validateJSONRequest(obj)

    if not (isvalid):
        data = {"Error:": message}
        return Response(dumps(data), mimetype='application/json',status=400)
    #valid JSON, then rename JSON ids
    namespace,obj = jsonid_rename(obj)
    print "namespace" + namespace
    # all ready to insert into database

    try:
        # the RequestID of this POST
        if db.getRequestId(namespace) is None:
            requestId = db.addRequestId(namespace)
        else:
            requestId = db.updateRequestId(namespace)
    except:
        e = sys.exc_info()
        print "Errorx:",e
        traceback.print_exc()
    print "reqId: ",requestId

    submitting_time = datetime.datetime.utcnow()
    data = {"request id: ": requestId, "provenance submitted at": submitting_time, "submitted provenance": obj}
    if request.authorization is None:
        username = "NoUser"
    else:
        username = request.authorization.username
    m = Message()
    jsonForLaterProcessing = json.dumps({'obj':obj, 'namespace':namespace, 'user':username,
                                         'requestIP':request.remote_addr,'requestId':requestId,
                                         'submitAt':submitting_time},default=outputJSON)
    m.set_body(jsonForLaterProcessing)
    provaas_queue.write(m)

    return Response(dumps(data,default=outputJSON), mimetype='application/json',status=201)


@app.route('/<string:namespace>/provenance/<string:uuid>', methods=['GET'])
@auth.login_required
def get_resource_provenance(namespace,uuid):
 
  #obj = db.getSubgraph(uuid)
  uuid1 = uuid
  namespace1 = namespace
  obj = db.getNodeByUuid(namespace1,uuid1)
  obj_json = neo2json(obj)
  return Response(obj_json,mimetype='application/json',status=200)

@app.route('/<string:namespace>/provenance/<string:uuid>', methods=['DELETE'])
@auth.login_required
def delete_resource_provenance(namespace,uuid):
  namespace1 = namespace
  uuid1 = uuid
  obj = db.deleteNodeByUuid(namespace1,uuid1)
  if (obj == True):
    data = {"Deleted:": obj}
  else:  
    data = {"Deleted:": obj, "Reason": "namespace or uuid does not exist"}
  return Response(dumps(data),mimetype='application/json',status=200)

@app.route('/<string:namespace>/provenance/request/<string:rid>', methods=['DELETE'])
@auth.login_required
def delete_provenance_request(namespace,rid):
  namespace1 = namespace
  rid1 = rid
  obj = db.deleteNodeByRequestid(namespace1,rid1)
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
    app.run(host=SERVER_IP, port=5000, debug=True)
