TEST 
====

1°) Edit run_all.sh and change parameters : site, duration

2°) Add in your config SSH (e.g. ~/.ssh/config) :

	Host fit-$site 
    	   Hostname $site.iot-lab.info
    	   Port 2222
    	   User root

	Host a8-* m3-* node-a8-*
    	   User root
    	   HostName %h
    	   ProxyCommand ssh fit-$site -W %h:%p
    	   StrictHostKeyChecking no

3°) Test your ssh configuration

        ssh m3-1 or ssh a8-1

ENHANCEMENT :

1) add on open node a8 test for using gateway serial communication:

    root@iotlab-board:~# while true; do cat /dev/mtd2 > /dev/null ; sleep 5; done

2) add in run_all.sh an ssh connexion check before launching get_failed_open_node_a8_logs.sh script
