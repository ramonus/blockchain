#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import json, hashlib,datetime
from ECDSA import ECDSA
#from dateutil import parser
#from threading import Thread
from dbm2 import calcWallet

class Node:
  def __init__(self,fm):
    self.fm = fm
    self.chain = self.fm.loadBC()
    self.current_transactions = self.fm.loadTransactions()
    self.nodes = self.fm.loadNodes()
    self.cleanTransactions()
    self.wallet = self.fm.loadWallet()
    if self.chain==list():
      self.updateChain(self.createGenesisBlock())
    if not self.isValidChain(self.chain):
      self.resolveConflicts()
  def updateChain(self,block):
    self.chain.append(block)
    self.fm.saveBC(self.chain)
    return True
  def isValidChain(self,chain):
    chain = chain.copy()
    gb = chain.pop(0)
  def isValidNextBlock(self,last_block,block):
    vchash = block["hash"]==self.hashBlock(block)
    vlhash = last_block["hash"]==self.hashBlock(last_block)
    vphash = block["previous_hash"]==self.last_block["hash"]
    vnn = block["block_n"]==last_block["block_n"]+1
    return vchash and vlhash and vphash and vnn
  def createGenesisBlock(self):
    return self.createBlock(0,datetime.datetime.now(),[],"0")
  def createBlock(self,n,timestamp,tokens,previous_hash):
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
             "previous_hash":previous_hash}
    block["hash"] = self.hashBlock(block)
    return block
  @staticmethod
  def hashBlock(block):
    block = block.copy()
    if "hash" in block:
      del block["hash"]
    return hashlib.sha256(json.dumps(block,sort_keys=True).encode()).hexdigest()
  def cleanTransactions(self):
    pass
  def resolveConflicts(self):
    pass
  @staticmethod
  def createRewardTransaction(wallet):
    if wallet["direction"]!=calcWallet(wallet["public"]):
      return False
    t = {"sender":"0",
         "recipient":wallet["direction"],
         "amount":1,
         "public_key":wallet["public"]}
    public = bytes.fromhex(wallet["public"])
    private = bytes.fromhex(wallet["private"])
    e = ECDSA(privatekey=private,publickey=public)
    t["signature"] = e.sign(hashlib.sha256(json.dumps(t,sort_keys=True).encode()).digest()).hex()
    return t