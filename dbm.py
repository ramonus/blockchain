#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import json,os, codecs
from AES import *

dbn = "db.json"
keyn = "key.json"
to_hex = lambda x: codecs.decode(x,"hex_codec").decode()
to_barr = lambda x: codecs.encode(x,"hex_codec")
def loadkey():
  if not os.path.exists(keyn):
    aes = AESC()
    with open(keyn,"wb") as f:
      f.write(aes.key)
      key = aes.key
  else:
    with open(keyn,"rb") as f:
      key = f.read()
  return key
def loadBC():
  key = loadkey()
  aes = AESC(key)
  if not os.path.exists(dbn):
    with open(dbn,"wb") as f:
      f.write(aes.encrypt(json.dumps([],sort_keys=True)))
  with open(dbn,"rb") as f:
    return json.loads(aes.decrypt(f.read()))
def saveBC(chain):
  key = loadkey()
  aes = AESC(key)
  with open(dbn,"wb") as f:
    f.write(aes.encrypt(json.dumps(chain,sort_keys=True)))
  print("Chain with {} blocks saved".format(len(chain)))
def deleteBC():
  if os.path.exists(dbn):
    os.remove(dbn)
    print("BlockChain deleted")