Tools Description
=================

See the associated script files for more information.

CLI JSON Parser
---------------

It allows extracting informations from jsons directly from command line.

It parses stdint and apply the argument on the equivalent python object as a
`(lambda x: <argument>)`

### Usage ###

Get all 'Alive' nodes from Grenoble site

    $ experiment-cli info -li | ./parse_json.py "[entry['$HOSTNAME']['wsn430']['Alive'] for entry in x['items'] if '$HOSTNAME' in entry.keys()][0]"
    1-7+9-47+49+51+53-67+70-72+74-99+101-102+126-129+131-134+136-166+168-169+171-183+185-191+194-201+204-215+217-222+224-227+229-235+237-251+253-255


OML plot consumption
--------------------

`plot_oml_consum.py`

plot oml filename node consumption
           [-abcehptv] -i <filename> or --input=\<filename\>

for time verification --time or -t


for begin sample --begin=\<sample_beg\> or -b \<sample_beg\>

for end sample --end=\<sample_end\> or -e \<sample_end\>

for label title plot --label=\<title\> or -l \<title\>

for plot consumption --power or -p

for plot voltage --voltage or -v

for plot current --current or -c

for all plot --all or -a

for help use --help or -h


OML plot radio power
--------------------

`plot_oml_radio.py`

plot oml filename [-tbeaplh] -i \<filename\> or --input=\<filename\>

for time verification --time or -t

for begin sample --begin=\<sample_beg\> or -b \<sample_beg\>

for end sample --end=\<sample_end\> or -e \<sample_end\>

for label title plot --label=\<title\> or -l \<title\>

for plot in one window --all or -a

for plot in separate windows --plot or -p

for help use --help or -h


OML plot mobile node trajectory
-------------------------------

`plot_oml_traj.py`

plot oml robot trajectory [-behmt] -i \<filename\> or --input=\<filename\>

for time verification --time or -t

for begin sample --begin=\<sample_beg\> or -b \<sample_beg\>

for end sample --end=\<sample_end\> or -e \<sample_end\>

for label title plot --label=\<title\> or -l \<title\>

for plot maps and elements --maps=\<filename\> or -c \<filename\>

for help use --help or -h

An example of use :
 * `> cd ex_oml_traj/`
 * `> ../plot_oml_traj.py -i m3-382-c2.oml -m grenoble-map.txt`
 * `> ../plot_oml_traj.py --input=m3-382-c2.oml --maps=grenoble-map.txt --circuit=circuits/grenoble/circuit2.json`
 * `> ../plot_oml_traj.py --maps=strasbourg-map.txt --circuit=circuits/strasbourg/square.json`
