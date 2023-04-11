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

Update apt with the new repos, & install.

```
$ sudo apt update && sudo apt install -y influxdb
```

Then start the influxdb service and set it to run at boot:

```
$ sudo systemctl unmask influxdb.service
$ sudo systemctl start influxdb
$ sudo systemctl enable influxdb.service
```

### Troubleshooting - missing key

In case an error occurs during the installation of influxdb due to the key like:

```
$ sudo apt update && sudo apt install -y influxdb
Get:1 http://archive.raspberrypi.org/debian bullseye InRelease [23.6 kB]
Get:2 http://raspbian.raspberrypi.org/raspbian bullseye InRelease [15.0 kB]
Get:3 https://repos.influxdata.com/debian bullseye InRelease [7031 B]
Get:4 http://archive.raspberrypi.org/debian bullseye/main armhf Packages [316 kB]
Err:3 https://repos.influxdata.com/debian bullseye InRelease
  The following signatures couldn't be verified because the public key is not available: NO_PUBKEY D8FF8E1F7DF8B07E
Get:5 http://raspbian.raspberrypi.org/raspbian bullseye/main armhf Packages [13.2 MB]
Reading package lists... Done
W: GPG error: https://repos.influxdata.com/debian bullseye InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY D8FF8E1F7DF8B07E
E: The repository 'https://repos.influxdata.com/debian bullseye InRelease' is not signed.
N: Updating from such a repository can't be done securely, and is therefore disabled by default.
N: See apt-secure(8) manpage for repository creation and user configuration details.
```

A solution is available at [Configuring Linux hosts to use the new signing key](https://www.influxdata.com/blog/linux-package-signing-key-rotation/).

Step 1 - Obtain and verify the new key

```
$ wget -q https://repos.influxdata.com/influxdata-archive_compat.key
$ gpg --with-fingerprint --show-keys ./influxdata-archive_compat.key
```

Step 2 - Install the new key

```
$ cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
```

Step 3 - Update your APT sources to use the new key

```
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
```

Step 4 - Cleanup the old key

```
sudo rm -f /etc/apt/trusted.gpg.d/influxdb.gpg
```

Step 5 - check that no errors on update and then install influxdb

```
sudo apt update && sudo apt install -y influxdb
```

### Troubleshooting - Missing locale during influxdb installation

If during the influxdb installation you get:

```
$ sudo apt update && sudo apt install -y influxdb
...
Get:1 https://repos.influxdata.com/debian stable/main armhf influxdb armhf 1.8.10-1 [50.7 MB]
Fetched 50.7 MB in 23s (2188 kB/s)
apt-listchanges: Can't set locale; make sure $LC_* and $LANG are correct!
perl: warning: Setting locale failed.
perl: warning: Please check that your locale settings:
        LANGUAGE = (unset),
        LC_ALL = (unset),
        LANG = "en_GB.UTF-8"
    are supported and installed on your system.
perl: warning: Falling back to the standard locale ("C").
locale: Cannot set LC_CTYPE to default locale: No such file or directory
locale: Cannot set LC_MESSAGES to default locale: No such file or directory
locale: Cannot set LC_ALL to default locale: No such file or directory
...
```

You can fix this issue by:

Step 1 - export variables

```
$ export LANGUAGE=en_GB.UTF-8
$ export LC_ALL=en_GB.UTF-8
```

Step 2- Check that the default settings are uncommented

```
$ sudo nano /etc/locale.gen
```

Step 3 - Generate again the locale

```
$ sudo locale-gen
```

