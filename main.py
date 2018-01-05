#!/usr/bin/env python3

# -*- coding: utf-8 -*-


from Server import Server
from app import Node
from dbm import filemanager

fm = filemanager()
node = Node(fm)
server = Server(node)
server.listen(5000)
