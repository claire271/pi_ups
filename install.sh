#!/bin/bash

# Install gambezi
wget https://github.com/tigerh/gambezi_rpi/archive/master.zip
unzip master.zip
rm master.zip
cd gambezi_rpi-master
./install.sh
cd ..
rm -rf gambezi_rpi-master

# Install packages

# Install init scripts
sudo cp pi_ups.sh /etc/init.d/
sudo ln -s /etc/init.d/pi_ups.sh /etc/rc5.d/S99pi_ups.sh
