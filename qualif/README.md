TEST 
====

0°) You need root ssh access to the frontend to fetch gateway logs


1°) Add the following lines in your ssh config (e.g. ~/.ssh/config) :

	Host fit-$site 
    	   Hostname $site.iot-lab.info
    	   Port 2222
    	   User root

	Host a8-* m3-* node-a8-*
    	   User root
    	   ProxyCommand ssh fit-$site -W %h:%p
    	   StrictHostKeyChecking no

2°) Test your ssh configuration :

        ssh m3-1 or ssh a8-1


3°) Test the tests :

	site=$site nb_runs=1 ./run_all.sh m3
	site=$site nb_runs=1 ./run_all.sh a8

Note: if your $site is managed by the production platform, comment-out
      the definition of variable IOTLAB_API_URL in source.me


4°) Optionally, edit ``run_all.sh`` and set default value for site

	``site=${site:-devgrenoble}`` => set to your $site

5°) Run the tests :

	./run_all.sh m3
	./run_all.sh a8
