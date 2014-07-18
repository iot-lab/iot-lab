#!/usr/bin/env python

from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

from simplejson import JSONEncoder, JSONDecoder
from subprocess import check_output
from urllib import unquote


class Reqs:

  def get_owned_nodes(self, site):
	res, err = call("experiment-cli get -l --state Running")
	if err: return ["", err]

	state = {}
	for experiment in res["items"]:
		nodes = experiment["resources"]
		if nodes[0].find("." + site + ".") == -1:
			continue
		for n in nodes:
			node_id = n.split('-')[1].split('.')[0]
			state[node_id] = "owned"
	return ["text/plain", JSONEncoder().encode(state)]

  def get_system_state(self, site, archi):
	res, err = call("experiment-cli info -li --site " + site)
	if err: return ["", err]

	state = res["items"][0][site][archi]
	return ["text/plain", JSONEncoder().encode(state)]

  def save_node_set(self, name, nodes):
	set_name = unquote(name)
	return ["text/plain", set_name]

  def get_firmwares_list(self):
	res = [ "firmware 1", "firmware 2" ]
	return ["text/plain", JSONEncoder().encode(res)]

  def start_nodes(self, nodes, site, archi):
	res = {}
	return ["text/plain", JSONEncoder().encode(res)]

  def stop_nodes(self, nodes, site, archi):
	res = {}
	return ["text/plain", JSONEncoder().encode(res)]

  def reset_nodes(self, nodes, site, archi):
	res = {}
	return ["text/plain", JSONEncoder().encode(res)]

  def update_nodes(self, firmware, nodes, site, archi):
	firmware = unquote(firmware)
	res = {}
	return ["text/plain", JSONEncoder().encode(res)]

  def grab_nodes(self, nodes, site, archi, duration):
	res = {}
	return ["text/plain", JSONEncoder().encode(res)]


class Handler(Reqs, SimpleHTTPRequestHandler):

  def do_GET(self):
	path, args = self.parse_req()
	if not hasattr(self, path):
		return SimpleHTTPRequestHandler.do_GET(self)
	typ, res = eval("self." + path, {"self":self}, {})(**args)
	if not typ:
		return self.error(res)
	self.send_response(200)
	self.send_header("Content-type", typ)
	self.end_headers()
	self.wfile.write(res)

  def do_POST(self):
	#print self.rfile.read()
	return self.do_GET()

  def parse_req(self):
	try:
		path, args = self.path.split('?')
		args = dict([kv.split('=')
			for kv in args.strip('&').split('&')])
	except:
		path = self.path
		args = {}
	return [path.strip('/'), args]

  def error(self, msg):
	self.send_response(500)
	self.end_headers()
	self.wfile.write(msg)

  def log_message(self, format, *args):
	pass
 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	#address_family = socket.AF_INET6
	pass
 
def call(cmd):
	try:
		return JSONDecoder().decode(check_output(cmd.split(" "))), 0
	except ValueError:
		return 0, "invalid json returned by experiment-cli"
	except Exception:
		return 0, "error calling experiment-cli"
	
def main():
	server = ThreadedHTTPServer(('localhost', 8000), Handler)
	server.serve_forever()
 
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
