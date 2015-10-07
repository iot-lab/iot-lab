#!/bin/bash
USER=vandaele
SITE=lille

# experiment-cli info -li --site lille
# experiment-cli submit ...
# experiment-cli wait ...

gnome-terminal --tab -t tunnel -e "socat tcp-listen:9000,fork,reuseaddr exec:'ssh $USER@$SITE.iot-lab.info \"serial_aggregator\"'" --tab -t nodejs --profile demo --working-directory /home/fun/iot-lab/web-view3D -e "nodejs app.js && bash" &
sleep 2
firefox localhost:3000
