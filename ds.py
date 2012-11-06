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
			new = True							# if the address is new, add it
			for (myAddress, myLink, myCost) in self.table:
				if address == myAddress:
					new = False					# if seen before, update
					if (cost + 1) < myCost:		# better cost -> update table
						self.table.remove((myAddress, myLink, myCost))
						self.table.append((address, sender, cost + 1))
						tableModified = True
					elif sender == myLink and not(cost == (myCost - 1)):
						self.table.remove((myAddress, myLink, myCost))
						new = True				# a better route: change route
			if new:
				self.table.append((address, sender, cost + 1))
				tableModified = True
		print
		if tableModified:
			self.sendTable()

# Read the file to create the network. Requires a well-formed file
def parseInputFile(filename):
	f = open(filename, 'r')
	try:
	    rawData = f.readlines()
	finally:
	    f.close()
	
	for line in rawData:
		matchNode = re.match('node ', line)
		if matchNode:						# create a new node
			nodeInfo = line[matchNode.end():].split()
			network[nodeInfo[0]] = Node(nodeInfo[0], nodeInfo[1:])
		matchLink = re.match('link ', line)
		if matchLink:						# create a new link
			linkInfo = line[matchLink.end():].split()
			network[linkInfo[0]].links.append(linkInfo[1])
			network[linkInfo[1]].links.append(linkInfo[0])
		matchCommand = re.match('send ', line)
		if matchCommand:					# send the table from the start node
			network[line[matchCommand.end():]].sendTable()

parseInputFile(args[1])
while len(messages) > 0:					# Run until nodes are silent
	currentMessage = (sender, recipient, sentTable) = messages.pop(0)
	network[recipient].readMessage(currentMessage)
for node in network.itervalues():			# Print tables for all nodes
	print 'table {0}'.format(node.name),
	for entry in node.table:
		print '({0}|{1}|{2})'.format(entry[0], entry[1],entry[2]),
	print

# Question 1:
#		Yes, it is necessary to reply with the table. Consider a chain of nodes:
# node n1 1
# node n2 2
# node n3 3

# link n1 n2
# link n2 n3

# send n1
# 
# 		In this situation, node n1 or n2 will not hear about the existence of
#		n3 due to it not replying. Without these pending messages, the algorithm
#		will converge early with an incomplete graph. The addition of replies
#		ensures the information exchange is always bi-directional.

# Question 2:
#		There are fewer messages sent, and therefore fewer events so in the
#		best case (a cyclic or highly connected graph) a complete and correct
#		map would be found sooner. Therefore, network topology does have an
#		effect on the requirement for reply messages. For the correctness of
#		the algorithm in all topologies however, the reply messages are
#		required. Of note is that different results are found depending on
#		which node initiates sending of tables - if n2 in the example above
#		were to send its table first, the complete graph would be found in ##
#		events, rather than 16 with the standard algorithm.

#		The aforementioned issue is irrelevent when nodes periodically resend
#		their tables since, for example, n2 would hear from n3 in time even
#		if not immediately, and the graph would be completed on the next
#		iteration.