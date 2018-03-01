#!/usr/bin/env python
#coding=utf-8
from xml.dom import minidom
from collections import namedtuple

class Parsing_XML():
	def __init__(self):
		pass
	
	def get_attrvalue(self, node, attrname):
		return node.getAttribute(attrname) if node else ''
	
	def get_nodevalue(self, node, index=0):
		return node.childNodes[index].nodeValue if node else ''
	
	def get_xmlnode(self, node, name):
		return node.getElementsByTagName(name) if node else []
	
	def xml_to_string(self, filename):
		doc = minidom.parse(filename)
		return doc.toxml('UTF-8')
	
	def get_ftp_config(self, filename='config.xml'):
		doc = minidom.parse(filename)
		root = doc.documentElement
		ftp_nodes = self.get_xmlnode(root, 'ftpserver')
		ftp_parameters = {}
		for node in ftp_nodes:
			node_ftphost = self.get_xmlnode(node, 'fhost')
			ftp_host = self.get_nodevalue(node_ftphost[0])
			node_ftpuser = self.get_xmlnode(node, 'ftpuser')
			ftp_user = self.get_nodevalue(node_ftpuser[0])
			node_ftppw = self.get_xmlnode(node, 'ftppw')
			ftp_pw = self.get_nodevalue(node_ftppw[0])
			node_dlthreadnum = self.get_xmlnode(node, 'dlthreadnum')
			ftp_dlthreadnum = self.get_nodevalue(node_dlthreadnum[0])
			node_ulthreadnum = self.get_xmlnode(node, 'ulthreadnum')
			ftp_ulthreadnum = self.get_nodevalue(node_ulthreadnum[0])
			node_dllocalpath = self.get_xmlnode(node, 'dllocalpath')
			ftp_dllocalpath = self.get_nodevalue(node_dllocalpath[0])
			node_dlremotepath = self.get_xmlnode(node, 'dlremotepath')
			ftp_dlremotepath = self.get_nodevalue(node_dlremotepath[0])
			node_ullocalpath = self.get_xmlnode(node, 'ullocalpath')
			ftp_ullocalpath = self.get_nodevalue(node_ullocalpath[0])
			node_ulremotepath = self.get_xmlnode(node, 'ulremotepath')
			ftp_ulremotepath = self.get_nodevalue(node_ulremotepath[0])
			node_servicetime = self.get_xmlnode(node, 'service_time')
			ftp_servicetime = self.get_nodevalue(node_servicetime[0])
			node_sourceaddress = self.get_xmlnode(node, 'source_address')
			ftp_sourceaddress = self.get_nodevalue(node_sourceaddress[0])
			ftp_parameters['ftp_host'],ftp_parameters['ftp_user'],ftp_parameters['ftp_pw'],ftp_parameters['ftp_dlthreadnum'],\
			ftp_parameters['ftp_ulthreadnum'],ftp_parameters['ftp_dllocalpath'],ftp_parameters['ftp_dlremotepath'],\
			ftp_parameters['ftp_ullocalpath'],ftp_parameters['ftp_ulremotepath'],ftp_parameters['ftp_servicetime'],ftp_parameters['ftp_sourceaddress']=\
			ftp_host, ftp_user, ftp_pw, ftp_dlthreadnum, ftp_ulthreadnum, ftp_dllocalpath,ftp_dlremotepath, ftp_ullocalpath,\
			ftp_ulremotepath, ftp_servicetime, ftp_sourceaddress
		return ftp_parameters

if __name__ == "__main__":
	print(Parsing_XML().get_ftp_config())