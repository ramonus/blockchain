#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import json, hashlib,datetime,requests
from ECDSA import ECDSA
from ecdsa import BadSignatureError
#from dateutil import parser
#from threading import Thread
from dbm2 import calcWallet
from urllib.parse import urlparse
from multiping import multi_ping, MultiPing
import random

class Node:
  BLOCK_SIZE = 10
  DEFAULT_MAX_NODES = 8
  DEFAULT_PORT = 5000
  def __init__(self,fm,*args,**kwargs):
    self.port = self.DEFAULT_PORT
    self.max_nodes = kwargs["max_nodes"] if "max_nodes" in kwargs and kwargs["max_nodes"]>2 else self.DEFAULT_MAX_NODES
    self.fm = fm
    self.chain = self.fm.loadBC()
    self.current_transactions = self.fm.loadTransactions()
    self.nodes = self.fm.loadNodes()
    self.pnodes = self.fm.loadPNodes()
#    self.cleanTransactions()
    self.wallet = self.fm.loadWallet()
    if self.chain==[]:
      self.updateChain(self.createGenesisBlock())
#    if not self.isValidChain(self.chain):
#      self.resolveConflicts()
  def updateChain(self,block):
    self.chain.append(block)
    self.fm.saveBC(self.chain)
    return True
  def updateTransactions(self):
    self.fm.saveTransactions(self.current_transactions)
    return True
  def isValidChain(self,chain=None):
    if chain!=None:
      chain = chain.copy()
    else:
      chain = self.chain.copy()
    gb = chain.pop(0)
    state = {}
    # genesisBlock
    if gb["hash"] != self.hashBlock(gb) or gb["block_n"]!=0:
      return False
    state = self.updateState(state,gb["tokens"])
    last_block = gb
    for i in range(1,len(self.chain)):
      block = self.chain[i]
      if self.isValidNextBlock(last_block,block):
        tokens = block["tokens"]
        state = self.updateState(state,tokens)
      else:
        return False
    return state
  @staticmethod
  def verifyTransaction(t):
    t = t.copy()
    pub = t["public_key"]
    e = ECDSA(publickey=bytes.fromhex(pub))
    s = t["signature"]
    del t["signature"]
    try:
      e.verify(s,t)
      return True
    except BadSignatureError:
      return False
  def isValidNextBlock(self,last_block,block):
    vchash = block["hash"]==self.hashBlock(block)
    vlhash = last_block["hash"]==self.hashBlock(last_block)
    vphash = block["previous_hash"]==last_block["hash"]
    vnn = block["block_n"]==last_block["block_n"]+1
    PoW = hashlib.sha256((str(last_block["pow"])+last_block["hash"]+str(block["pow"])).encode()).hexdigest()[:4]=="0000"
    return vchash and vlhash and vphash and vnn and PoW
  def createGenesisBlock(self):
    return self.createBlock(0,datetime.datetime.now(),[],"0")
  def createNextBlock(self,tokens):
    last_block = self.chain[-1]
    last_block_hash = last_block["hash"]
    n = last_block["block_n"]
    return self.createBlock(n+1,datetime.datetime.now(),tokens,last_block_hash,last_block["pow"])
  def createBlock(self,n,timestamp,tokens,previous_hash,previous_pow=None):
    t = self.createRewardTransaction(self.wallet)
    tokens = tokens.copy()
    tokens.append(t)
    if type(timestamp)==datetime.datetime:
      timestamp = timestamp.isoformat()
    block = {"block_n":n,
             "timestamp":timestamp,
             "token_n":len(tokens),
             "tokens":tokens,
             "miner":self.wallet["direction"],
             "previous_hash":previous_hash,
             "pow":9 if previous_pow==None else self.POW(previous_pow,previous_hash)}
    block["hash"] = self.hashBlock(block)
    return block
  @staticmethod
  def hashBlock(block):
    block = block.copy()
    if "hash" in block:
      del block["hash"]
    return hashlib.sha256(json.dumps(block,sort_keys=True).encode()).hexdigest()
  @staticmethod
  def __checkNode(node):
    # simple ping check
    try:
      t = Node.__ping(node)
      return t<2 and t!=-1
    except:
      return False
    
    
  def preparePNode(self):
    return self.__preparePNode()
  def ping(self,host,n=0):
    return self.__ping(host,n)
  
  
  def __preparePNode(self):
    if self.pnodes:
      #pick random pnode
      while self.pnodes:
        pnode = random.choice(self.pnodes)
        t = self.__ping(pnode,4)
        print("Available pnodes:",len(self.pnodes))
        del self.pnodes[self.pnodes.index(pnode)]
        if t<2 and t!=-1:
          return pnode
        print("Not valid node:",pnode)
      return None
  def resolveNodes(self):
    # clean nodes
    nodes = set([node for node in list(self.nodes) if self.__checkNode(node)])
    added = []
    while len(nodes)<self.max_nodes and len(self.pnodes)>0:
      nnode = self.__preparePNode()
      if nnode:
        self.addNode(nnode)
        # let node know we are alive
        url = f'http://{nnode}/pnodes/register'
        self.__prequest(url,["http://localhost:"+str(self.port)])
        added.append(nnode)
    print("Added {} new nodes".format(len(added)))
    
    return {"added_nodes":added}
  @staticmethod
  def __ping(node,n=0):
    if ":" in node:
      node = node.split(":")[0]
    if n>0:
      avg = 0
      for i in range(n):
        avg += Node.__ping(node)
      avg/=n
    try:
      mp = MultiPing([node])
      mp.send()
      r,nr = mp.receive(1)
      for addr, rtt in r.items():
        RTT = rtt
      if nr:
        mp.send()
        r,nr = mp.receive(1)
        RTT = -1
      return RTT
    except:
      return -1
  def cleanTransactions(self):
    s = self.current_transactions.copy()
    if not self.isValidChain(self.chain):
      self.resolveConflicts()
    status = {}
#    for block in self.chain[]
  @staticmethod
  def __srequest(end):
    headers = {"Content-Type":"application/json"}
    return requests.get(end,headers=headers).json()
  @staticmethod
  def __prequest(end,data):
    headers = {"Content-Type":"application/json"}
    return requests.post(end,json=data,headers=headers).json()
  def resolveConflicts(self):
    self.resolveNodes()
    
  @staticmethod
  def isValidTxn(state,txn):
    #verify
    public = txn["public_key"]
    e = ECDSA(publickey=bytes.fromhex(public))
    sender = txn["sender"]
    amount = txn["amount"]
    s = bytes.fromhex(txn["signature"])
    recipient = txn["recipient"]
    v = txn.copy()
    del v["signature"]
    return ((sender=="0" and calcWallet(public)==recipient) or (calcWallet(public)==sender and (state.get(sender,0)-amount)>=0)) and e.verify(s,v)
  @staticmethod
  def updateState(state,txn):
    state = state.copy()
    for i,tx in enumerate(txn):
      if Node.isValidTxn(state,tx):
        sender = tx["sender"]
        recipient = tx["recipient"]
        amount = tx["amount"]
        if sender!="0":
          state[sender] -= amount
        state[recipient] = state.get(recipient,0)+amount
      else:
        del txn[i]
    return state
  def getNodes(self):
    return list(self.nodes)
  @staticmethod
  def createTransaction(wallet,recipient,amount):
    d = wallet["direction"]
    public = wallet["public"]
    priv = wallet["private"]
    if d==calcWallet(public):
      t = {"sender":d,
           "recipient":recipient,
           "amount":amount,
           "timestamp":datetime.datetime.now().isoformat(),
           "public_key":public}
      e = ECDSA(privatekey=bytes.fromhex(priv))
      t["signature"] = e.sign(t).hex()
      return t
    return False
  def POW(self,last_proof,last_hash):
    proof = 0
    while not self.valid_proof(last_proof,last_hash,proof):
      proof +=1
    return proof
  @staticmethod
  def valid_proof(last_proof,last_hash,proof):
    guess = f'{last_proof}{last_hash}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[0:4]=="0000"
  @staticmethod
  def createRewardTransaction(wallet):
    if wallet["direction"]!=calcWallet(wallet["public"]):
      return False
    t = {"sender":"0",
         "recipient":wallet["direction"],
         "amount":1.0,
         "timestamp":datetime.datetime.now().isoformat(),
         "public_key":wallet["public"]}
    public = bytes.fromhex(wallet["public"])
    private = bytes.fromhex(wallet["private"])
    e = ECDSA(privatekey=private,publickey=public)
    t["signature"] = e.sign(t).hex()
    return t
  def getLastBlock(self):
    return self.chain[-1]
  def isFull(self):
    return len(self.current_transactions)>=self.BLOCK_SIZE
  def addPNode(self,address):
    try:
      parsed_url = urlparse(address)
      self.pnodes.append(parsed_url.netloc)
      self.updatePNodes()
      return True
    except:
      return False
  def updatePNodes(self,nodes=None):
    if nodes==None:
      pnodes = self.pnodes
    self.fm.savePNodes(pnodes)
    return True
  def addNode(self,address):
    try:
      self.nodes.add(address)
      self.updateNodes()
      return True
    except:
      return False
  def updateNodes(self,nodes=None):
    if nodes==None:
      nodes = self.nodes
    self.fm.saveNodes(nodes)
    return True
  def addTransaction(self,transaction):
    state = self.isValidChain(self.chain)
    if self.isValidTxn(state,transaction):
      self.current_transactions.append(transaction)
      self.fm.saveTransactions(self.current_transactions)
      return True
    return False
  def mine(self):
    if not self.isFull():
      tr = self.current_transactions
    else:
      tr = self.current_transactions[:self.BLOCK_SIZE]
    last_block = self.chain[-1]
    rt = self.createRewardTransaction(self.wallet)
    tr.append(rt)
    b = self.createNextBlock(tr)
    if self.isValidNextBlock(last_block,b):
      self.updateChain(b)
      return b
    return False
    