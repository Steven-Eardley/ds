# -*- coding: utf-8 -*-
# Distributed Systems Coursework 2012
# Steven Eardley s0934142

import re
import sys

# Check arguments and erase old results file
args = sys.argv
if (len(args) != 2):
	print "Invalid number of arguments. Usage: ds.py inputFile"
	sys.exit()

# Dictionary storing all nodes
network = dict()

# Queue of network messages
messages = []

# Object simulating a network node
class Node:
	def __init__(self, name, addresses):
		self.name = name				# The identifier for the node
		self.addresses = addresses		# The addresses of the node
		self.links = []					# The set of nodes it is connected to
		self.table = []					# The table of addresses and costs
		for address in self.addresses:
			self.table.append((address, 'local', 0))
	
	def sendTable(self):
		# send the table on all links
		for link in self.links:
			global messages
			messages.append((self.name, link, self.table))
			print 'send {0} {1}'.format(self.name, link),
			for entry in self.table:
				print '({0}|{1}|{2})'.format(entry[0], entry[1], entry[2]),
			print

	def readMessage(self, (sender, recipient, inTable)):
		# add message to table info
		tableModified = False
		print 'receive {0} {1}'.format(sender, recipient),
		for (address, link, cost) in inTable:
			print '({0}|{1}|{2})'.format(address, link, cost),
			new = True
			for (myAddress, myLink, myCost) in self.table:
				if address == myAddress:
					new = False
					if (cost + 1) < myCost:		# better cost -> update table
						self.table.remove((myAddress, myLink, myCost))
						self.table.append((address, sender, cost + 1))
						tableModified = True
					elif sender == myLink and not(cost == (myCost - 1)):
						self.table.remove((myAddress, myLink, myCost))
						new = True
			if new:
				self.table.append((address, sender, cost + 1))
				tableModified = True
		print
		if tableModified:
			self.sendTable()

def parseInputFile(filename):
	f = open(filename, 'r')
	try:
	    rawData = f.readlines()
	finally:
	    f.close()
	
	for line in rawData:
		matchNode = re.match('node ', line)
		if matchNode:
			nodeInfo = line[matchNode.end():].split()
			network[nodeInfo[0]] = Node(nodeInfo[0], nodeInfo[1:])
		matchLink = re.match('link ', line)
		if matchLink:
			linkInfo = line[matchLink.end():].split()
			network[linkInfo[0]].links.append(linkInfo[1])
			network[linkInfo[1]].links.append(linkInfo[0])
		matchCommand = re.match('send ', line)
		if matchCommand:
			network[line[matchCommand.end():].split()[0]].sendTable()

parseInputFile(args[1])
while len(messages) > 0:
	currentMessage = (sender, recipient, sentTable) = messages.pop(0)
	network[recipient].readMessage(currentMessage)
for node in network.itervalues():
	print 'table {0}'.format(node.name),
	for entry in node.table:
		print '({0}|{1}|{2})'.format(entry[0], entry[1],entry[2]),
	print

# Question 1:

# Question 2: