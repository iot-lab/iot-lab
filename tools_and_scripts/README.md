Tools Description
=================

See the associated script files for more information.


Serial aggregator
-----------------

Aggregate all the serial links of an experiment and print it to stdout.

### Usage ###

    $ experiment-cli get -r -i <exp_id> | ./aggregate_log.py
    1395240359.286712;node46; Type Enter to stop printing this help
    1395240359.286853;node46;
    1395240359.292523;node9;
    1395240359.292675;node9;Senslab Simple Demo program
    1395240359.292820;node9;Type command
    1395240359.293094;node9;    h:  print this help
    1395240359.293241;node9;    t:  temperature measure
    1395240359.293612;node9;    l:  luminosity measure
    1395240359.293760;node9;    s:  send a radio packet
    1395240359.294044;node9;
    1395240359.294212;node9; Type Enter to stop printing this help
    1395240359.294781;node37;
    1395240359.294949;node37;Senslab Simple Demo program
    1395240359.295098;node37;Type command
    ...



CLI JSON Parser
---------------

It allows extracting informations from jsons directly from command line.

It parses stdint and apply the argument on the equivalent python object as a
`(lambda x: <argument>)`

### Usage ###

Get all 'Alive' nodes from Grenoble site

    $ experiment-cli info -rs | parse_json.py \
        "[entry['Alive'] for entry in x['items'] if \
          entry['site'] == 'grenoble'][0]"
    1-7+9-47+49+51+53-67+70-72+74-99+101-102+126-129+131-134+136-166+168-169+\
    171-183+185-191+194-201+204-215+217-222+224-227+229-235+237-251+253-255


