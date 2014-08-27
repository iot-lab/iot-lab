#!/usr/bin/env python

import sys, time, select, json, argparse

queue = []

def main():
	args = parse_args()
	while   feed_queue(sys.stdin, args.event_timeout):
		trim_queue(args.max_age, args.queue_size)
		dump_queue("user-state.json")

def parse_args():
	parser = argparse.ArgumentParser(description="""
	Feeds user-state.json with 'splash events' as received on stdin.

	Events must come in one per line, as: <node id> [style [style...]]
	Default style is 'splash' when node id is specified alone as input.
	Events are kept for some time in a queue, aged, and eventually go away.
	The aging process is controlled by specified optional arguments.
	""".replace("\t", "  "), formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument("-m", "--max-age", type=float, default=2)
	parser.add_argument("-s", "--queue-size", type=int, default=5)
	parser.add_argument("-t", "--event-timeout", type=float, default=.2)
	return parser.parse_args()

def feed_queue(f, event_timeout):
	rlist, wlist, xlist = select.select([f], [], [], event_timeout)
	if not rlist: return True
	line = f.readline()
	if not line: return False
	event = parse_line(line)
	queue.append(event)
	#print event.node_id
	return True

def trim_queue(max_age, queue_size):
	stamp = time.time()
	for event in queue:
		if event.stamp < (stamp - max_age):
			queue.remove(event)
	if len(queue) > queue_size:
		queue.pop(0)

def dump_queue(fname):
	res = {}
	for event in queue:
		if event.node_id == None: continue
		node_id = event.node_id
		style = event.data
		res[node_id] = { "style": style if style else "splash" }
	f = open(fname, "w")
	f.write(json.dumps(res))
	f.close()

def parse_line(line):
	x = line.strip().split()
	if not x: return Event(time.time(), None, 0)
	node_id = x[0]
	data = " ".join(x[1:])
	return Event(time.time(), node_id, data)

class Event:
	def __init__(self, stamp, node_id, data):
		self.stamp = stamp
		self.node_id = node_id
		self.data = data

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
