#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Aggregate multiple tcp connections """

import sys
import asyncore
import threading
import socket

from iotlabaggregator import LOGGER


class Connection(object, asyncore.dispatcher):  # pylint:disable=R0904
    """
    Handle the connection to one node
    Data is managed with asyncore. So to work asyncore.loop() should be run.

    Child class should re-implement 'handle_data'
    """
    port = 20000

    def __init__(self, hostname):
        super(Connection, self).__init__()
        asyncore.dispatcher.__init__(self)
        self.hostname = hostname  # node identifier for the user
        self.data_buff = ''       # received data buffer

    def handle_data(self, data):
        """ Dummy handle data """
        LOGGER.info("%s received %u bytes", self.hostname, len(data))
        return ''  # Remaining unprocessed data

    def start(self):
        """ Connects to node serial port """
        self.data_buff = ''      # reset data
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.hostname, self.port))

    def handle_close(self):
        """ Close the connection and clear buffer """
        self.data_buff = ''
        LOGGER.error('%s;Connection closed', self.hostname)
        self.close()

    def handle_read(self):
        """ Append read bytes to buffer and run data handler. """
        self.data_buff += self.recv(8192)
        self.data_buff = self.handle_data(self.data_buff)

    def handle_error(self):
        """ Connection failed """
        LOGGER.error('%s;%r', self.hostname, sys.exc_info())


class Aggregator(dict):  # pylint:disable=too-many-public-methods
    """
    Create a dict of Connection from 'nodes_list'
    Each node is stored in the entry with it's node_id

    It as a thread that runs asyncore.loop() in the background.

    After init, it can be manipulated like a dict.
    """
    def __init__(self, nodes_list, connection_class=Connection,
                 *args, **kwargs):
        if not nodes_list:
            raise ValueError("%sAggregator: Empty nodes list %r" %
                             (connection_class.__name__, nodes_list))
        super(Aggregator, self).__init__()

        self.thread = threading.Thread(target=asyncore.loop,
                                       kwargs={'timeout': 1, 'use_poll': True})
        # create all the Connections
        for node_url in nodes_list:
            node = connection_class(node_url, *args, **kwargs)
            self[node_url] = node

    def start(self):
        """ Connect all nodes and run asyncore.loop in a thread """
        for node in self.itervalues():
            node.start()
        self.thread.start()
        LOGGER.info("Aggregator started")

    def stop(self):
        """ Stop the nodes connection and stop asyncore.loop thread """
        for node in self.itervalues():
            node.close()
        self.thread.join()

    def send_nodes(self, nodes_list, message):
        """ Send the `message` to `nodes_list` nodes

        If nodes_list is None, send to all nodes """
        if nodes_list is None:
            LOGGER.debug("Broadcast: %r", message)
            self.broadcast(message)
        else:
            LOGGER.debug("Send: %r to %r", message, nodes_list)
            for node in nodes_list:
                self._send(node, message)

    def _send(self, hostname, message):
        """ Safe send message to node """
        try:
            self[hostname].send(message)
        except KeyError:
            LOGGER.warning("Node not managed: %s", hostname)
        except socket.error:
            LOGGER.warning("Send failed: %s", hostname)

    def broadcast(self, message):
        """ Send a message to all the nodes serial links """
        for node in self.iterkeys():
            self._send(node, message)
