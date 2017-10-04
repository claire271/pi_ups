#!/bin/bash

# Install gambezi
wget https://github.com/tigerh/gambezi_rpi/archive/master.zip
unzip master.zip
rm master.zip
cd gambezi_rpi-master
./install.sh
cd ..
rm -rf gambezi_rpi-master

# Install gambezi-python
wget https://github.com/tigerh/gambezi_python/archive/master.zip
unzip master.zip
rm master.zip
mv gambezi_python-master gambezi_python

# Install packages
sudo apt-get install python3-pip
sudo pip3 install wiringpi websocket-client

# Enable I2C
sudo bash -c ". raspi-config nonint; do_i2c 0"

# Install init scripts
sudo cp pi_ups.sh /etc/init.d/
sudo ln -s /etc/init.d/pi_ups.sh /etc/rc5.d/S99pi_ups.sh
