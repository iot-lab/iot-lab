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

