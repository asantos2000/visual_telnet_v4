#!/usr/bin/python
#import os
import math
import time
from pygraphviz import *
from time import gmtime, strftime

TIMESTAMP = str(math.trunc(time.time())) # Generate a sequence for file name

#
# Desenha o grafico
#
def draw(result_filename, diagram_filename):
	#nodeA = origin_
	#nodeB = destination_
	#connector = connector_

	result_file = open(result_filename, 'r')

	A=AGraph()

	# set some default node attributes
	A.node_attr['style']='filled'
	A.node_attr['shape']='component'
	A.node_attr['fixedsize']='false'
	A.node_attr['fontcolor']='#000000'

	i = 0
	#A -(C)-> B
	for line in result_file:
		i += 1

		l = line.strip()
		print l
		
		if l == 'ip_from\tip_to\tport\tresult\tresult_msg':
			print 'Ignoring header... ' + str(i)
		else:
			try:
				ip_from, ip_to, port_to, result, result_msg = l.split('\t')
			except ValueError, e:
				print 'Ignoring line: ' + str(i)
				print e 
				print line
			else:
				print '(' + str(i) + ') Connecting... ' + ip_from + '->' + ip_to + ':' + port_to + ' - ' + str(result) + ' ' + result_msg
				A.add_edge(ip_from, ip_to + ':' + port_to)
				n=A.get_node(ip_to + ':' + port_to)
				if result == "0":
					n.attr['fillcolor']='green'
				else:
					n.attr['fillcolor']='tomato'

	# make timestamp
	A.node_attr['shape']='none'
	A.node_attr['fillcolor']='none'
	A.node_attr['style']='dotted'
	A.add_node(strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime()))

	# write files (dot and png)
	print A.string() # print to screen
	A.write(diagram_filename + '.dot') # write to <file_name>.dot
	print 'Wrote ' + diagram_filename + '.dot'
	A.draw(diagram_filename + '.png',prog='circo') # draw to png using circo
	print 'Wrote ' + diagram_filename + '.png'