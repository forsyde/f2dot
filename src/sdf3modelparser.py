'''          
 * File:    forsydemodelparser.py
 * Author:  George Ungureanu <ugeorge@kth.se> 
 * Purpose: implementing xml parsers for different ForSyDe-based 
            intermediate models. All parsers inherit the ModelParser
            class
 * License: BSD3
'''

'''
Copyright (c) 2014, George Ungureanu 
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import xml.dom.minidom as xmlparser
import pygraphviz as pgv
import os
import logging
import utils
import dictionary as dic
from parsemethods import *

## Controller class for parsing SDF3-XML models.
#
#  This is a controller class which contains the main method for
#  parsing SDF3-XML models and plotting the DOT graphs.
class Sdf3ModelParser:
	
	## Class constructor
	# @param Sdf3ModelParser $self The object pointer
	# @param Settings $settings The f2dot.settings.Settings object
	#        holding the run-time settings
	def __init__(self, settings): 
		self.logger = logging.getLogger('f2dot.sdf3parser')
		self.logger.debug('Initializing the parser...')
		self.set = settings
		
		## @var logger 
		#  Logger for this class

		## @var set 
		#  Settings object

		## @var vertical 
		#  \c True if the plot was set to TB (top-bottom)
		

	## Function to parse a ForSyDe-XML model and plot a DOT graph,
	## according to the settings.
	# @param Sdf3ModelParser $self The object pointer
	def plotModel(self):
		G = pgv.AGraph(directed=True, rankdir=self.set.dir,
                       fontname='Helvetica', strict=False, overlap='prism',
                       splines='true')

		root = xmlparser.parse(self.set.inPathAndFile)
		appName = root.getElementsByTagName(dic.APPLICATION_GRAPH_TAG)[0].getAttribute('name')
		self.logger.debug("Parsing <"+ appName + ">")

		bgColor = utils.computeBackground(self.set.compColorCoeffs,1)
		frame = G.subgraph( \
			name="cluster_" + self.set.inFile, \
			label = appName, \
			style = 'filled, rounded', \
			color = bgColor, \
			fontsize = '13')

		self.logger.info('Starting the parser on process network "' +
                         self.set.rootProcess + '"...')
		self.__parseXmlFile(root, frame)
	
		G.write(self.set.outPathAndFile)
		G.draw(path=self.set.outPathAndFile, format=self.set.format, prog=self.set.program)
		self.logger.info('Process network plotted in ' +
                         self.set.outPathAndFile)

	def __parseXmlFile(self, root, graph):
		graph.add_node('dummy',style='invisible')

		# sdf graph
		for sdf in root.getElementsByTagName(dic.SDF_TAG):
			list_of_actors = []

			#child actors
			for actor in sdf.getElementsByTagName(dic.SDF_ACTOR_TAG):

				actorId    = actor.getAttribute('name')
				var1, exp  = settings.leafTags                  # TODO: different labels for different formats
				actorLabel = getXpathVarList(node, exp, var1)

				list_of_actors.append(actorId)				
				list_of_ports = getLeafPortList(leaf, self.set)
				nodeLabel = buildRecord(actorLabel, list_of_ports)

				# add leaf process node to the appropriate cluster
				graph.add_node("cluster_" + self.set.inFile, \
					node = actorId, 
					label = nodeLabel, \
					fillcolor = self.set.leafColor)

			self.logger.debug( 'Found ' + str(len(list_of_actors)) + ' actors' 
				+ ' \n\t' + str(list_of_actors))

			
			#channes child nodes
			for channel in sdf.getElementsByTagName(dic.channel_TAG):
				channelInfo = getBasicChannelInfo(channel, parentId, self.set)

				#build channel info
				if self.vertical:
					compassIn='n'
					compassOut='s'
				else:
					compassIn='w'
					compassOut='e'
				if channelInfo.source in list_of_actors:
					# source is a leaf process
					if channelInfo.target in list_of_actors:
						# target is a leaf process
						src = channelInfo.source
						dst = channelInfo.target
						src_p = channelInfo.source_port + ':' + compassOut
						dst_p = channelInfo.target_port + ':' + compassIn
					else:
						# target is a composite process
						src = channelInfo.source
						dst = channelInfo.target + dic.ID_SEP + channelInfo.target_port
						src_p = channelInfo.source_port + ':' + compassOut
						dst_p = '' + compassIn
				else:
					# source is a composite process
					if channelInfo.target in list_of_leaves:
						# target is a leaf process
						src = channelInfo.source + dic.ID_SEP + channelInfo.source_port
						dst = channelInfo.target
						src_p = '' + compassOut
						dst_p = channelInfo.target_port + ':' + compassIn
					else:
						# target is a composite process
						src = channelInfo.source + dic.ID_SEP + channelInfo.source_port
						dst = channelInfo.target + dic.ID_SEP + channelInfo.target_port
						src_p = '' + compassOut
						dst_p = '' + compassIn

				#add edge
				graph.add_edge(src, dst, tailport=src_p, headport=dst_p, \
					style=style, penwidth=penwidth, label=prettyPrintLables(channelInfo.label))
				self.logger.debug( 'Added channel %s:%s->%s:%s',src, src_p, dst, dst_p )

		# flush the root node
		del root


## Object class for extracting all ports from a leaf process and yeld
## them as lists of tuples of type \c (port_name, information)
class getActorPortList(object):
	## @var in_ports
	#       List of input ports, represented as tuples of (port_name,
	#       information) (lst(tuple))
	## @var out_ports
	#       List of input ports, represented as tuples of (port_name,
	#       information) (lst(tuple))

	## Class constructor.
	# @param $self
    #        The object pointer
	# @param Node $parentNode
    #        The \c xml.dom.Node object representing the (parent) leaf
    #        process
    # @param Settings $settings
    #        The f2dot.settings.Settings object holding the run-time
    #        settings
	def __init__(self, parentNode, settings):
		self.in_ports = []
		self.out_ports = []
		for port in parentNode.getElementsByTagName(dic.SDF_PORT_TAG):		
			port_name = port.getAttribute('name')
			port_dir  = port.getAttribute('type')
			var1, exp = settings.portLeafTags
			info = getXpathVarList(port, exp, var1)
			logger.debug('Got port info:' + str(info))
			# build port lists having tuples of name and info
			if port_dir == dic.INPUT_DIR:
				self.in_ports.append((port_name, info))
			else:
				self.out_ports.append((port_name, info))


class getBasicChannelInfo(object):
	## @var name
	#       The name of this process (str)
	## @var ID
	#       The generated unique ID (str)
	## @var label
	#       The list of extracted information from the XML file, based
	#       on the provided XPath queries queries.
    #  @see f2dot.utils.parseLableTags
	#  @see prettyPrintLables
	#  @see getXpathList
	
	## Class constructor.
	# @param $self
    #        The object pointer
	# @param Node $node
    #        The \c xml.dom.Node object representing the composite
    #        process
    # @param str $parentID
    #        The unique ID of its parent process
    # @param Settings $settings
    #        The f2dot.settings.Settings object holding the run-time
    #        settings
	def __init__(self, node, parentID, settings):
		self.name = node.getAttribute('name')
		self.source = node.getAttribute('srcActor')
		self.source_port = node.getAttribute('srcPort')
		self.target = node.getAttribute('dstActor')
		self.target_port = node.getAttribute('dstPort')
		var1, exp = settings.signalTags		
		self.label = getXpathVarList(node, exp, var1)
		logger.debug('Labels for channel %s:%s->%s:%s\n  %s', \
					 self.source, self.source_port, self.target, \
                     self.target_port, self.label)