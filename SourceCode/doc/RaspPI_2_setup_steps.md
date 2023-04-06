# Raspberry Pi 2 set up

These are the steps that have been done in order to set up Raspberry Pi 2

# Installation 

From a new Raspberry Pi 2 image flashed the following commands where executed:

## Update 

```
$ sudo apt update
$ sudo apt upgrade -y
```

## Install Influxdb

Add Influx repositories to apt:

```
$ wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/os-release
echo "deb https://repos.influxdata.com/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
```