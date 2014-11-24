apt-get -y install cmake curl git 
apt-get -y install gcc-arm-none-eabi gcc-msp430
apt-get -y install python-matplotlib
apt-get -y install vim emacs
apt-get -y install python-setuptools
apt-get -y install python-argparse python-pip
pip install requests

echo "clone Iot-LAB git"
cd /home/vagrant | git clone https://github.com/iot-lab/iot-lab.git

echo "install Iot-LAB CLI Toools"
CLI_TOOLS_VERSION="1.3.2"
cd /home/vagrant | wget -qO - https://github.com/iot-lab/cli-tools/archive/v$CLI_TOOLS_VERSION.tar.gz | tar xz
cd /home/vagrant/cli-tools-$CLI_TOOLS_VERSION && python setup.py install
rm -rf /home/vagrant/cli-tools-$CLI_TOOLS_VERSION

echo "install tunslip6 Contiki tool"
wget -qO - https://github.com/iot-lab/contiki/raw/master/tools/tunslip6.c > /home/vagrant/tunslip6.c
cc /home/vagrant/tunslip6.c -o /home/vagrant/tunslip6
rm -f /home/vagrant/tunslip6.c
