#! /usr/bin/env python
import sys, time, os
from daemon import Daemon

import urllib2, urllib
import socket
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from optparse import OptionParser

def get_next_free_port(port):
	s = socket.socket()
	try:
		s.connect((u'localhost', port))
		return get_next_free_port(port + 1)
	except socket.error:
		return port

class MyHandler(SimpleHTTPRequestHandler):
	def do_OPTIONS(self):
		self.send_response(200, "ok")
		self.send_header("Content-Type", "application/json; charset=UTF-8")
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
		self.send_header("Access-Control-Allow-Headers", "Content-Type")
		self.end_headers()
		return

	def do_GET(self):
		self.send_response(200, "ok")
		self.send_header("Content-Type", "application/json; charset=UTF-8")
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
		self.send_header("Access-Control-Allow-Headers", "Content-Type")
		self.end_headers()
		# Is this a special request to /__ajaxproxy/
		prefix = u'/__ajaxproxy/'
		if self.path.startswith(prefix):
			# Strip off the prefix.
			newPath = self.path.lstrip(prefix)
			print u'GET remote: ', newPath
			try:
				self.copyfile(urllib2.urlopen(newPath), self.wfile)
			except IOError, e:
				print u"ERROR:   ", e
		else:
			SimpleHTTPRequestHandler.do_GET(self)
		return

class myHTTPServer(MyHandler):
	pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	pass

class MyProxy(Daemon):
	def run(self):
		try:
			proxyport = os.environ['PROXY_PORT']
		except KeyError:
			proxyport = 8000
		try:	
			next_free_port = get_next_free_port(int(proxyport))
			server = ThreadedHTTPServer((u'',next_free_port),myHTTPServer)
			print u'server started at port ', next_free_port
			server.serve_forever()
		except KeyboardInterrupt:
			server.socket.close()
			
if __name__ == "__main__":
	daemon = MyProxy('/tmp/myproxy.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
			sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)