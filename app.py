#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import json, hashlib,datetime
from ECDSA import ECDSA
from ecdsa import BadSignatureError
#from dateutil import parser
#from threading import Thread
from dbm2 import calcWallet

class Node:
  BLOCK_SIZE = 10
  def __init__(self,fm):
    self.fm = fm
    self.chain = self.fm.loadBC()
    self.current_transactions = self.fm.loadTransactions()
    self.nodes = self.fm.loadNodes()
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
  def isValidChain(self,chain):
    chain = chain.copy()
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
    PoW = hashlib.sha256(str(last_block["pow"])+last_block["hash"]+str(block["pow"])).encode()).hexdigest()[:4]=="0000"
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
  def cleanTransactions(self):
    s = self.current_transactions.copy()
    if not self.isValidChain(self.chain):
      self.resolveConflicts()
    status = {}
#    for block in self.chain[]
  def resolveConflicts(self):
    pass
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
         "amount":1,
         "timestamp":datetime.datetime.now().isoformat(),
         "public_key":wallet["public"]}
    public = bytes.fromhex(wallet["public"])
    private = bytes.fromhex(wallet["private"])
    e = ECDSA(privatekey=private,publickey=public)
    t["signature"] = e.sign(t).hex()
    return t
  def addTransaction(self,transaction):
    state = self.isValidChain(self.chain)
    if self.isValidTxn(state,transaction):
      self.current_transactions.append(transaction)
      self.fm.saveTransactions(self.current_transactions)
      return True
    return False
  def mine(self):
    if len(self.current_transactions)<self.BLOCK_SIZE:
      tr = self.current_transactions
    else:
      tr = self.current_transactions[:BLOCK_SIZE]
    last_block = self.chain[-1]
    
    