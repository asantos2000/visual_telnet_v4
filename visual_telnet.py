import base64
import cmd
import sys
import graphic_generator
import test_connection

prompt_str = ''

class RunCommand(cmd.Cmd):
	#Simple shell to run a command on the host
	prompt = 'visual_telnet: ' + prompt_str + '> '

	def __init__(self):
		cmd.Cmd.__init__(self)
		self.hosts = []
		self.connections = []
		self.host_file = ''
		self.filename = ''

	def do_add_host(self, args):
		#add_host <hostip,user,password>. Add the host to the host list
		if self.host_file == '':
			print 'Open file first!!! Command: open_file <file_name>'
		if args:
			ip, user, passwd = args.split(',')
			passwd_encoded = base64.b64encode(passwd)
			print passwd_encoded
			self.host_file.write(ip + '\t' + user + '\t' + passwd_encoded + '\n')
		#decoded = base64.b64decode(encoded)
		#print decoded
		else:
			print "usage: add_host <hostip>,<user>,<password>"

	def do_add_comment(self, args):
		#add_comment <some text>. Add comment to host_file
		if self.host_file == '':
			print 'Open file first!!! Command: open_file <file_name>'
			
		if args:
			self.host_file.write('#' + args + '\n')
		else:
			print 'usage: add_comment <some text>'

	def do_open_file(self, args):
		#open_file <filename>. Open filename to add new entries
		if args:
			self.host_file = open(args, 'ar')
			prompt_str = args 
		else:
			print 'usage: open_file <filename> (optional path)'

	def do_close_file(self, args):
		#close_file. Close filename
		try:
			self.host_file.close()
			print 'File closed...'
		except:
			print 'File already closed...'

	def do_view_content(self,args):
		try:
			if args:
				view_file = open(args, 'r')
				#view_content. View content of file
				print '\n'
				for line in view_file:
					print line,
				print '\n'
			else:
				print 'usage: view_content <filename>'
		except IOError,e:
			print 'Error reading file ' + args
			print e
			
	def do_help(self, args):
		long_tab = '\t\t\t\t'
		print '\n## Help ##'
		print 'visual_telnet v4.0'
		print 'Use this utility to manage and run connections tests.'
		print '\nCommand list:'
		print '\thelp\t' + long_tab + 'Show this help.'
		print '\tadd_host' + long_tab + 'Add the host to the host list.'
		print '\tadd_comment' + long_tab + 'Add comment to host_file.'
		print '\topen_file' + long_tab + 'Open filename to add new entries.'
		print '\tclose_file' + long_tab + 'Close filename.'
		print '\tview_content' + long_tab + 'View content of a file.'
		print '\tdraw_diagramv' + long_tab + 'Draw diagram from result file.'
		print '\texecute_test' + long_tab + 'Run connection test using hosts files.'
		print '\tquit\t' + long_tab + 'Close file and quit interactive command line.'
		print '\nType command for the parameters.'

	def do_draw_diagram(self, args):
		# Draw graphic from result file
		if args:
			result_filename, diagram_filename = args.split(',')
			# Generate graph
			graphic_generator.draw(result_filename, diagram_filename)
		else:
			print "usage: draw_diagram result_filename,diagram_filename(without extension)"
				

	def do_execute_test(self,args):
		if args:
			from_hosts_filename, to_hosts_filename, result_filename = args.split(',')
			test_connection.test(from_hosts_filename, to_hosts_filename, result_filename)
		else:
			print "usage: execute_test from_host_filename, to_host_filename, result_filename"
		
	def do_quit(self, args):
		#quit. Quit app
		print "Closing file..."
		self.do_close_file(args)
		sys.exit("Goodbye!")
		
if __name__ == '__main__':
	RunCommand().cmdloop()