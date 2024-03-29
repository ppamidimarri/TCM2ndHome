# TCM2ndHome

This is an extension of my [TeslaCamMerge project](https://github.com/ppamidimarri/TeslaCamMerge) to support two home locations, with a main home and a weekend home. 

A Jetson Nano runs at the primary home and a Pi 4B runs at the second home. Both devices host an SMB share with the exact same credentials. When I park at the second home, the Pi Zero W in the car archives the clips, and then Jetson Nano at the primary home pulls those files from the second home's Pi 4B and merges them.

Update on October 18: This project now support multiple Tesla vehicles. See the TeslaCamMerge project for details on how to set it up.

## Prerequisites

* [TeslaCamMerge](https://github.com/ppamidimarri/TeslaCamMerge) installed and working at your primary home, using a Jetson Nano or Raspberry Pi 4B
* [teslausb](https://github.com/marcone/teslausb) installed in your car with SMB share archiving and working

## Additional Hardware Needed

* Raspberry Pi 3B+ or 4B
* Power supply for the Pi
* Micro-SD card for the Pi

## Network Requirements at Second Home

* Fixed LAN IP address for the Pi at the second home
* Dynamic DNS solution (e.g. [NoIP](https://www.noip.com/)) with a domain name for your second home (e.g. `second.home.com`)
* At the main router in your second home, forward port 22 to the Pi's fixed LAN IP address

## Instructions

**A. Setup the Pi at your second home**
1. Flash [the latest Raspbian Lite version](https://downloads.raspberrypi.org/raspbian_lite_latest) on the Micro-SD card
2. Put the card in the Pi, connect a monitor, keyboard and mouse to the Pi and power it up
3. Login with user `pi` and password `raspberry`
4. `sudo raspi-config` and change password, configure Wi-Fi, and change hostname to match that of the device at your primary home running TeslaCamMerge
5. `sudo apt update`
6. `sudo apt upgrade`
7. `sudo apt install git samba lsof`
8. Install and configure the dynamic update client for your dynamic DNS provider (e.g. [NoIP DUC](https://www.noip.com/support/knowledgebase/installing-the-linux-dynamic-update-client/))
9. Add the dynamic update client to your crontab or `/etc/rc.local` so it is started on boot (e.g. add `/usr/local/bin/noip2` before `exit 0` to `/etc/rc.local` if you are using NoIP)

**B. Set up the link between your two homes**

Read [this helpful guide](https://help.ubuntu.com/community/SSH/OpenSSH/Keys) on how to set up key-based SSH access. Then perform the following steps in this section while logged into the device that you are running TeslaCamMerge on at your primary home. 

1. `ping second.home.com` and check if you are able to reach your second home
2. `ssh pi@second.home.com` and login with your password, and then `exit` to get back to your primary device
3. `cd ~`
4. `ls .ssh` and check whether that directory exists; if it doesn't, `mkdir ~/.ssh` and `chmod 700 ~/.ssh`
5. `ssh-keygen -t rsa`, use the default location for the file, and do not enter a passphrase
6. `ssh-copy-id pi@second.home.com` and enter your password when prompted 
7. `ssh pi@second.home.com` and this time it should directly log you in without asking for a password

If step 1 fails, you need to check your dynamic DNS setup. If step 1 works but step 2 fails, you need to check the forwarding of port 22 on the router of your second home. 

**C. Secure the Pi at your second home**

Identify all computer(s) from which you want to SSH into the Pi at your second home. Repeat the steps in Section B from each of those computers, but enter a passphrase under step 5 and make sure you remember that passphrase. When you do step 7 above, you need to enter the passphrase to get into the Pi. 

Perform the following steps only after you confirm on all the computers you identifed that you are able to get into the Pi at your second home without entering the user password. 

1. Login to the Pi at your second home (e.g. SSH in from your primary home device running TeslaCamMerge)
2. `cp /etc/ssh/sshd_config ~/sshd_config.default`
3. `sudo nano /etc/ssh/sshd_config` and find the line: `#PasswordAuthentication yes`
4. Change that line to: `PasswordAuthentication no` (i.e. remove the `#` at the beginning and change the word `yes` to `no`) and then save the file 
5. `sudo systemctl reload ssh`

After this, you will not be able to SSH into this Pi with the username and password. 

**D. Configure [samba](https://www.samba.org/) and set up the SMB share on the Pi at your second home**

In this section, make sure that `share-user-name` and the password you assign it are identical to the values you configured for the TeslaCamMerge installation at your primary home. Perform all these steps on the Pi at your second home.

1. `sudo cp /etc/samba/smb.conf{,.backup}`
2. `sudo nano /etc/samba/smb.conf`, uncomment (i.e. remove the `;` character at the beginning of) these lines:
```
	interfaces = 127.0.0.0/8 eth0
	bind interfaces only = yes
```
3. `sudo mkdir /samba`
4. `sudo chgrp sambashare /samba`
5. `sudo useradd -M -d /samba/<share-user-name> -G sambashare <share-user-name>`
6. `sudo mkdir /samba/<share-user-name>`
7. `sudo chown <share-user-name>:sambashare /samba/<share-user-name>`
8. `sudo chmod 2770 /samba/<share-user-name>`
9. `sudo smbpasswd -a <share-user-name>` and set your SMB share password
10. `sudo smbpasswd -e <share-user-name>`
11. `sudo nano /etc/samba/smb.conf`, scroll to the bottom of the file and add:
```
# Settings for TM3 dashcam footage
[fdrive]
   path = /samba/<share-user-name>
   browseable = no
   read only = no
   force create mode = 0660
   force directory mode = 2770
   valid users = <share-user-name> @sadmin
```
12. `sudo usermod -a -G sambashare pi`

**D. Install the python scripts and service files on the Pi at your second home**

Perform all these steps on the Pi at your second home.

1. `cd ~`
2. `mkdir Upload`
3. `mkdir log`
4. `git clone https://github.com/ppamidimarri/TCM2ndHome`
5. `cd TCM2ndHome`
6. `chmod +x *.py`
7. Check `TCConstants.py` to make sure the values match your environment
8. `sudo cp tcm2*.service /lib/systemd/system`
9. `sudo systemctl daemon-reload`
10. `sudo systemctl enable tcm2-removeOldSecond tcm2-stager tcm2`
11. `sudo reboot`
12. Once the Pi boots up, check `systemctl status tcm2-*` and verify that the services are shown as `active (running)`

You can stop or start the `tcm2-removeOldSecond` and `tcm2-stager` services together by stopping or starting `tcm2`. You can stop or start them separately as well.

**E. Install python script and service at your primary home**

Perform all these steps on the device running TeslaCamMerge at your primary home.

1. `sudo apt install rsync`
2. `cd ~/TeslaCamMerge`
3. `scp pi@second.home.com:/home/pi/TCM2ndHome/DownloadTC.py DownloadTC.py`
4. `scp pi@second.home.com:/home/pi/TCM2ndHome/tcm-downloadTC.service tcm-downloadTC.service`
5. `nano DownloadTC.py` and edit `SERVER_CREDENTIALS` and `SOURCE_PATH` to match second home setup
6. `nano tcm-downloadTC.service` and replace `PROJECT_USER` with your UNIX user ID and `PROJECT_PATH` with the user's home directory (alternatively, you can run `python3 CreateServiceFiles.py` to get these changes done automatically using a script from the `TeslaCamMerge` project)
7. `sudo cp tcm-downloadTC.service /lib/systemd/system`
8. `sudo systemctl daemon-reload`
9. `sudo systemctl enable tcm-downloadTC`
10. `sudo reboot`

The service `tcm-downloadTC` now becomes part of the service group `tcm` that you setup when you installed `TeslaCamMerge` at your primary home. You can start and stop it individually, or with the rest of the group. 

Now your setup is complete! 
