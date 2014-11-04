#!/usr/bin/env python

from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

from simplejson import JSONEncoder, JSONDecoder
from subprocess import check_output
from urllib import unquote


class Reqs:

  def get_owned_nodes(self, site, archi):
	res = call("experiment-cli get -l --state Running")
	state = {}
	for experiment in res["items"]:
		for fqdn in experiment["resources"]:
			if (not site in fqdn) or (not archi in fqdn):
				continue
			node_id = fqdn.split('-')[1].split('.')[0]
			state[node_id] = experiment["id"]
	return state

  def get_system_state(self, site, archi):
	res = call("experiment-cli info -li --site " + site)
	state = res["items"][0][site][archi]
	return state

  def save_node_set(self, name, nodes):
	name = unquote(name)
	nodes = unquote(nodes)
	file_name = "nodes-sets.json"
	data = JSONDecoder().decode(file(file_name).read())
	data[name] = nodes
	open(file_name, "w").write(
		JSONEncoder(indent=4,sort_keys=1).encode(data))
	return {"name": name}

  def set_target_sensors(self, file_name):
	cmd = "ln -sf " + file_name + " sensors.js"
	return check_output(cmd.split(" "));

  def start_nodes(self, nodes, site, archi, exp_id):
	return call("node-cli --start -i " + exp_id
			+ " -l " + ",".join([site, archi, nodes]))

  def stop_nodes(self, nodes, site, archi, exp_id):
	return call("node-cli --stop -i " + exp_id
			+ " -l " + ",".join([site, archi, nodes]))

  def reset_nodes(self, nodes, site, archi, exp_id):
	return call("node-cli --reset -i " + exp_id
			+ " -l " + ",".join([site, archi, nodes]))

  def update_nodes(self, firmware, nodes, site, archi, exp_id):
	firmware = unquote(firmware)
	return call("node-cli --update " + firmware + " -i " + exp_id
			+ " -l " + ",".join([site, archi, nodes]))

  def grab_nodes(self, nodes, site, archi, duration, exp_id="unused"):
	return call("experiment-cli submit -d " + duration
			+ " -l " + ",".join([site, archi, nodes]))

  def get_exp_status(self, exp_id):
	return call("experiment-cli get -p -i " + exp_id)

class Handler(Reqs, SimpleHTTPRequestHandler):

  def do_GET(self):
	path, args = self.parse_req()
	if not hasattr(self, path):
		SimpleHTTPRequestHandler.do_GET(self)
		return
	try:
		res = eval("self." + path, {"self":self}, {})(**args)
	except Exception, e:
		self.error(e.message)
		return
	self.send_response(200)
	self.send_header("Content-type", "text/plain")
	self.end_headers()
	self.wfile.write(JSONEncoder().encode(res))

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
		return JSONDecoder().decode(check_output(cmd.split(" ")))
	except ValueError:
		raise Exception("invalid json returned by experiment-cli")
	except Exception:
		raise Exception("error calling experiment-cli")
	
def main():
	server = ThreadedHTTPServer(('localhost', 8000), Handler)
	server.serve_forever()
 
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
