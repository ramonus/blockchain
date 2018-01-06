#!/usr/bin/env python3

# -*- coding: utf-8 -*-


from flask import Flask, request, jsonify
from app import Node
from dbm2 import filemanager

fm = filemanager()
node = Node(fm)

app = Flask(__name__)

@app.route("/isfull",methods=['GET'])
def isFull():
  return jsonify(node.isFull()), 200
@app.route("/transactions/new",methods=["POST"])
def newTransaction():
  transaction = request.get_json()
  if node.isValidTxn(node.isValidChain(),transaction):
    return transaction, 200
  else:
    return jsonify(False), 200
  
if __name__=="__main__":
  app.run(host="",port=5000)
  
