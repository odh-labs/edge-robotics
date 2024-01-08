#%pre
#nmcli dev wifi connect Not-your-wifi password pleaseletmein
#%end
lang en_US
keyboard us
timezone Australia/Sydney 
rootpw $2b$10$C0ecnR5cPoWFuJiMv4O6duYr01t8qdkF6pG2t5b.6BKiEtpSekC22 --iscrypted
user --name=ansible --groups=wheel --password=$2b$10$C0ecnR5cPoWFuJiMv4O6duYr01t8qdkF6pG2t5b.6BKiEtpSekC22 --iscrypted
user --plaintext --name=redhat --password=redhat
reboot
cdrom
bootloader --append="rhgb quiet crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M"
zerombr
clearpart --all --initlabel
autopart
network --device=enp1s0 --hostname=workshop-edge-utils --bootproto=dhcp
network --device=enp0s31f6 --bootproto=static --ip=192.168.40.1 --netmask=255.255.255.0
firstboot --disable
selinux --enforcing
firewall --enabled
%packages
#@^graphical-server-environment
wpa_supplicant
#tigervnc-server
%end
