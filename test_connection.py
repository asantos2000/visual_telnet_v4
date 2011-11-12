#!/usr/bin/python
import socket
import math
import time
from time import gmtime, strftime
import threading, Queue
import paramiko
import base64

TIMEOUT=10
TIMESTAMP = str(math.trunc(time.time())) # Generate a sequence for file name

telnet_queue = Queue.Queue()
client = paramiko.SSHClient()

class ConnectionTestRemote(threading.Thread):

	def __init__(self, ip_, port_, seq, fo, ip_from):

		threading.Thread.__init__(self)
		self.fo = fo
		self.ip_from = ip_from
		self.ip = ip_
		self.port = int(port_)
		self.result = -1
		self.result_msg = ''
		self.seq = seq	

	def run(self):
		try:
			stdin, stdout, stderr = client.exec_command('python telnet.py ' + self.ip + ' ' + str(self.port))
			stdin.close()
			for line in stdout.read().splitlines():
				print line
				self.result, self.result_msg = line.split(';')
		except:
			print stderr
			self.result_msg = 'Error executing program...'
			
		print '(' + str(self.seq) + ') ' + str(self.result)
		print '(' + str(self.seq) + ') ' + self.result_msg
		
		self.fo.write(self.ip_from + '\t' + self.ip + '\t' + str(self.port) + '\t' + str(self.result) + "\t" + self.result_msg + '\n')

		telnet_queue.task_done() #signals to queue job is done

#
# Coordena as threads de testes
#
def coordinator(fi, fo, fh, hostname):

	# Interact on from_hosts.txt file
	j = 0
	for line_fh in fh:
		j += 1
		
		lfh = line_fh.strip()
		#print lfh
		
		# Trata comentarios
		if lfh.startswith('#'):
			print line_fh
		else:
			# Termina quando encontra o identificador de fim de linha <EOF>
			if lfh.startswith('<'):
				return
			else:
				if  (not lfh.startswith('-')) and (not lfh == ''):
					try:
						ip_from, user, passwd = lfh.split('\t')
					except ValueError, e:
						print 'Sintaxe error in line: ' + str(j)
						print e 
						print line_fh
					else:
						# Login remote host
						client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
						client.connect(ip_from,username=user,password=base64.b64decode(passwd))
						# Interact on hosts file (hosts to test)
						i = 0
						fi.seek(0) # Go to first line of file
						for line in fi:
						
							while threading.activeCount() > 20:
								time.sleep(10) # wait 5 seconds some threads finish
								
							i += 1
							
							l = line.strip()
							print l
							
							# Trata comentarios
							if l.startswith('#'):
								print '\n\n'
								print line
							else:
								# Termina quando encontra o identificador de fim de linha <EOF>
								if l.startswith('<'):
									#return
									print 'End of File encountered...'
								else:
									if  not l.startswith('-') and not l == '':
										try:
											#ip_port = line.split('\n')
											ip_to, port_to = l.split('\t')
											#port_to, ret_ = port_.split('\r')
										except ValueError, e:
											print 'Sintaxe error in line: ' + str(i)
											print e 
											print line
										else:
											print '\n'
											print '(' + str(i) + ') Testing from ' + ip_from + ' to ' + ip_to + ':' + port_to
											
											t = ConnectionTestRemote(ip_to, port_to, i, fo, ip_from)
											t.setDaemon(True)
											t.start()
											telnet_queue.put(i)
	
						# Wait all threads before close ssh connection
						telnet_queue.join()
						client.close()

# Main program
def test(from_hosts_filename, to_hosts_filename, result_filename): 
	start = time.time()

	# Command line parameters. TODO: Improve input parameters and generate help output
	print '\nExecution with parameters:' + from_hosts_filename + ', ' + to_hosts_filename + ', ' + result_filename 

	# Open files
	to_host_file = open(to_hosts_filename, 'r')
	result_file = open(result_filename, 'a')
	from_host_file = open(from_hosts_filename, 'r')

	# Valores padrao para o cabecalho
	hostname = socket.gethostname()
	hostIP = socket.gethostbyname(hostname)
	description = 'From: ' + hostname + ' (' + hostIP + ')' + '\n' + 'With TIMEOUT set to ' + str(TIMEOUT) + ' seconds' + '\nFrom: ' + from_hosts_filename + '\nTo: ' + to_hosts_filename + '\nResult: ' + result_filename +'-'+ str(TIMESTAMP) + '.txt|dot|png\n'

	if hostname == '':
		hostname = hostIP

	# screen feedback
	print '\n' + description

	# Write output header
	result_file.write(description)
	result_file.write(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
	result_file.write('\n\n\n')
	result_file.write('ip_from' + '\t' + 'ip_to' + '\t' + 'port' + '\t' + 'result' + "\t" + 'result_msg' + '\n')

	# Coordinate test execution
	coordinator(to_host_file, result_file, from_host_file, hostname)
	
	print 'Wait on the queue until everything has been processed...'     
	telnet_queue.join()
	
	print 'Elapsed Time: %s.' % (time.time() - start)
	print 'Main program waited until background was done.'