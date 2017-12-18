#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import hashlib, json
from dbm import *

sha256 = lambda x: hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
class BManager:
  def __init__(self,validator=None):
    self.validator = validator
    self.chain = loadBC()
  def createBlock(self,tokens):
    if len(self.chain)==0:
      # generate a genesis block
      print("Starting chain with a genesis block...")
      gblock = {"block_n":0,
               "parent_hash":None,
               "token_n":len(tokens),
               "tokens":tokens,
               "hash":sha256(tokens)
               }
      print("Done!")
      return gblock
    else:
      #non genesis block
      print("Creating a new block...")
      block = {"block_n":len(self.chain),
               "parent_hash":sha256(self.chain[-1]),
               "token_n":len(tokens),
               "tokens":tokens,
               "hash":sha256(tokens)
               }
      print("Done!")
      return block
  def addBlock(self,block):
    if (self.validator != None and self.validator(self.chain,block)) or self.validator == None:
      self.chain.append(block)
      saveBC(self.chain)
      print("Block added")