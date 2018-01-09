#!/usr/bin/env python3

# -*- coding: utf-8 -*-


from flask import Flask, request, jsonify
from app import Node
from dbm2 import filemanager

fm = filemanager()
node = Node(fm)

app = Flask(__name__)

@app.route("/transactions/isfull",methods=['GET'])
def isFull():
  return jsonify(node.isFull()), 200
@app.route("/transactions/new",methods=["POST"])
def newTransaction():
  transaction = request.get_json()
  if node.isValidTxn(node.isValidChain(),transaction):
    return transaction, 200
  else:
    return jsonify(False), 200
@app.route("/chain/last",methods=["GET"])
def last_block():
  return jsonify(node.getLastBlock()), 200
@app.route("/chain",methods=["GET"])
def get_chain():
  return jsonify(node.chain), 200
@app.route("/pnodes/register",methods=["POST"])
def register_pnodes():
  nodes = request.get_json()
  print(nodes)
  if type(nodes)==list:
    if len(nodes)>10 and nodes!=[]:
      nodes = nodes[:10]
    s = []  #succeed
    f = []  #failed
    for addr in nodes:
      if node.addPNode(addr):
        s.append(addr)
      else:
        f.append(addr)
    resp = {"Added PNodes":s,
            "Not added pnodes":f}
    return jsonify(resp), 200
  resp = {"Error":"Input format error"}
  return jsonify(resp), 400
@app.route("/pnodes/size",methods=["GET"])
def pnodes_size():
  return jsonify(len(node.pnodes)), 200
@app.route("/nodes",methods=["GET"])
def get_nodes():
  nodes = list(node.nodes)
  return jsonify(nodes), 200

@app.route("/nodes/resolve",methods=["GET"])
def resolve_nodes():
  added_nodes = node.resolveNodes()
  if added_nodes:
    return jsonify(added_nodes), 200
  else:
    return "0 nodes added",400


if __name__=="__main__":
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("-p","--port",default=node.DEFAULT_PORT,type=int,help='port to listen on')
  args = parser.parse_args()
  port = args.port
  node.port=port
  app.run(host="",port=port)
  
