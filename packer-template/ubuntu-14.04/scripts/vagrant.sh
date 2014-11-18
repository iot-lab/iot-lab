date > /etc/vagrant_box_build_time

mkdir /home/vagrant/.ssh
wget --no-check-certificate \
    'https://github.com/mitchellh/vagrant/raw/master/keys/vagrant.pub' \
    -O /home/vagrant/.ssh/authorized_keys
chown -R vagrant /home/vagrant/.ssh
chmod -R go-rwsx /home/vagrant/.ssh

#autologin 
echo "[SeatDefaults]" > /etc/lightdm/lightdm.conf.d/12-autologin.conf
echo "autologin-user=vagrant" >> /etc/lightdm/lightdm.conf.d/12-autologin.conf
