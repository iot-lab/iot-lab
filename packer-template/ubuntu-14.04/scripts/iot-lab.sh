apt-get -y install cmake curl git 
apt-get -y install gcc-arm-none-eabi gcc-msp430
apt-get -y install python-matplotlib
apt-get -y install vim emacs
apt-get -y install python-setuptools
apt-get -y install python-argparse python-pip
pip install requests

echo "clone Iot-LAB git"
cd /home/vagrant && git clone https://github.com/iot-lab/iot-lab.git

echo "install Iot-LAB CLI Toools"
pip install -e git+https://github.com/iot-lab/cli-tools.git#egg=iotlabcli[secure]

echo "install tunslip6 Contiki tool"
wget -qO - https://github.com/iot-lab/contiki/raw/master/tools/tunslip6.c > /home/vagrant/tunslip6.c
cc /home/vagrant/tunslip6.c -o /home/vagrant/tunslip6
rm -f /home/vagrant/tunslip6.c
