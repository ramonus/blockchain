#!/usr/bin/env python3

# -*- coding: utf-8 -*-

from ECDSA import ECDSA
from base58 import b58encode
import hashlib, os, json
from AES import AESC

sha = lambda x: hashlib.sha256(x).digest()

def ripemd160(x,_hex = False):
  ri = hashlib.new("ripemd160")
  ri.update(x)
  if _hex:
    return ri.hexdigest()
  else:
    return ri.digest()
def calcWallet(public):
  if type(public)==str:      
    public = bytes.fromhex(public)
  if public[0]!=b'\x04':
    public = b'\x04'+public
  s1 = sha(public)
  ri = b'\x00'+ripemd160(s1)
  s2 = sha(ri)
  s3 = sha(s2)
  chk = s3[:4]
  nri = ri+chk
  en = b58encode(nri)
  return en
def createWallet():
  e = ECDSA()
  public = e.publickey.to_string()
  private = e.privatekey.to_string()
  wallet_dir = calcWallet(public)
  wallet = {
      "direction":wallet_dir,
      "private":private.hex(),
      "public":public.hex()
      }
  return wallet




class filemanager:
  DEFAULT_AESKEY = "config/aeskey.bc"
  DEFAULT_TRANSACTIONS = "config/transactions.bc"
  DEFAULT_CHAIN = "config/blockchain.bc"
  DEFAULT_NODES = "config/nodes.bc"
  DEFAULT_WALLET = "config/wallets/wallet.dat"
  DEFAULT_PNODES = "config/pnodes.bc"
  def __init__(self,data=None):
    self.chainloc = self.DEFAULT_CHAIN
    self.keyloc = self.DEFAULT_AESKEY
    self.nodesloc = self.DEFAULT_NODES
    self.transloc = self.DEFAULT_TRANSACTIONS
    self.walletloc = self.DEFAULT_WALLET
    self.pnodesloc = self.DEFAULT_PNODES
    #some data input could be made here
  @staticmethod
  def __check_path(path):
    try:
      os.makedirs(path)
    except FileExistsError:
      pass
      
  def loadKey(self):
    fp = self.keyloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    if os.path.exists(fp):
      with open(fp,"rb") as f:
        key = f.read()
    else:
      aes = AESC()
      key = aes.key
      with open(fp,"wb") as f:
        f.write(key)
    return key
  def loadBC(self):
    key = self.loadKey()
    aes = AESC(key)
    fp = self.chainloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    if not os.path.exists(fp):
      bc = []
      with open(fp,"wb") as f:
        f.write(aes.encrypt(json.dumps(bc,sort_keys=True)))
    else:
      with open(fp,"rb") as f:
        edata = f.read()
      ddata = aes.decrypt(edata)
      try:
        bc = json.loads(ddata)
      except json.JSONDecodeError:
        return None
    return bc
  def loadTransactions(self):
    key = self.loadKey()
    aes = AESC(key)
    fp = self.transloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    if not os.path.exists(fp):
      t = []
      with open(fp,"wb") as f:
        f.write(aes.encrypt(json.dumps(t,sort_keys=True)))
    else:
      with open(fp,"rb") as f:
        edata = f.read()
      ddata = aes.decrypt(edata)
      try:
        t = json.loads(ddata)
      except json.JSONDecodeError:
        return None
    return t
  def loadNodes(self):
    key = self.loadKey()
    aes = AESC(key)
    fp = self.nodesloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    if not os.path.exists(fp):
      nodes = []
      with open(fp,"wb") as f:
        f.write(aes.encrypt(json.dumps(nodes,sort_keys=True)))
    else:
      with open(fp,"rb") as f:
        edata = f.read()
      ddata = aes.decrypt(edata)
      try:
        nodes = json.loads(ddata)
      except json.JSONDecodeError:
        return None
    return set(nodes)
  def loadPNodes(self):
    key = self.loadKey()
    aes = AESC(key)
    fp = self.pnodesloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    if not os.path.exists(fp):
      pnodes = []
      with open(fp,"wb") as f:
        f.write(aes.encrypt(json.dumps(pnodes,sort_keys=True)))
    else:
      with open(fp,"rb") as f:
        edata = f.read()
      ddata = aes.decrypt(edata)
      try:
        pnodes = json.loads(ddata)
      except json.JSONDecodeError:
        return None
    return pnodes
      
  def savePNodes(self,pnodes):
    key = self.loadKey()
    aes = AESC(key)
    fp = self.pnodesloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    with open(fp,"wb") as f:
      f.write(aes.encrypt(json.dumps(pnodes,sort_keys=True)))
    return True
  def saveBC(self,chain):
    key = self.loadKey()
    aes = AESC(key)
    fp = self.chainloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    with open(fp,"wb") as f:
      f.write(aes.encrypt(json.dumps(chain,sort_keys=True)))
    return True
  def saveTransactions(self,transactions):
    key = self.loadKey()
    aes = AESC(key)
    fp = self.transloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    with open(fp,"wb") as f:
      f.write(aes.encrypt(json.dumps(transactions,sort_keys=True)))
    return True
  def saveNodes(self,nodes):
    if type(nodes)==set:
      nodes = list(nodes)
    key = self.loadKey()
    aes = AESC(key)
    fp = self.nodesloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    with open(fp,"wb") as f:
      f.write(aes.encrypt(json.dumps(nodes,sort_keys=True)))
    return True
  def loadWallet(self):
    fp = self.walletloc
    ppath = fp[:fp.rfind("/")]
    self.__check_path(ppath)
    if not os.path.exists(fp):
      wallet = createWallet()
      with open(fp,"w") as f:
        f.write(json.dumps(wallet,sort_keys=True))
    else:
      with open(fp,"r") as f:
        wallet = json.loads(f.read())
    return wallet

