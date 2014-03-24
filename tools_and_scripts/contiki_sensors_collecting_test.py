#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Tests for contiki iotlab code """

from iotlab_firmware_autotest import AutomatedIoTLABTests


class ContikiIoTLabTest(AutomatedIoTLABTests):  # pylint:disable=I0011,R0904
    """ Test contiki firmwares """

    def _contiki_sensors_collecting(self, _, msg):
        """ Asyncronous test runner """
        try:
            # msg format:
            #    accel: -58 -1 -993 xyz mg
            #    gyros: 971 691 -35 xyz m°/s
            #    magne: 300 -67 212 xyz mgauss
            #    light: 7.6293945E-2 lux
            #    press: 9.849651E2 mbar
            line = msg.split(' ')
            if line[0] in self.state['sensors'].keys():
                self.state['sensors'][line[0]].add(tuple(line[1:]))
        except IndexError:
            pass  # unkown line
        finally:
            # check test completed
            test_ok = True
            test_ok &= len(self.state['sensors']['press:']) >= 10
            test_ok &= len(self.state['sensors']['light:']) >= 1
            test_ok &= len(self.state['sensors']['accel:']) >= 10
            test_ok &= len(self.state['sensors']['gyros:']) >= 10
            test_ok &= len(self.state['sensors']['magne:']) >= 10
            if test_ok:
                self.finished.set()

    def test_contiki_sensors_collecting(self):
        """ Test Contiki example 'iotlab/sensors_collecting' """
        self.state['sensors'] = {}
        self.state['sensors']['press:'] = set()
        self.state['sensors']['light:'] = set()
        self.state['sensors']['accel:'] = set()
        self.state['sensors']['gyros:'] = set()
        self.state['sensors']['magne:'] = set()

        node = self.nodes_aggregator.values()[0]
        node.line_handler.append(self._contiki_sensors_collecting)

        self.finished.wait(20)
        self.assertTrue(self.finished.is_set())  # timeout or test_ok

        node.line_handler.remove(self._contiki_sensors_collecting)


if __name__ == "__main__":
    import unittest
    unittest.main()
