lang en_US.UTF-8
keyboard us
timezone Australia/Sydney
text
reboot

# Partition disk with a 1GB boot XFS partition and a 10GB LVM volume containing system root
# The remainder of the volume will be used by the CSI driver for storing data
zerombr
clearpart --all --initlabel
autopart

#part /boot/efi --fstype=efi --size=200
#part /boot --fstype=xfs --asprimary --size=800
#part pv.01 --grow
#volgroup rhel pv.01
#logvol / --vgname=rhel --fstype=xfs --size=50000 --name=root
#logvol swap --fstype="swap" --name=swap --vgname=rhel --hibernation

# Configure network to use DHCP and activate on boot
network --bootproto=dhcp --device=link --activate --onboot=on
network --device=enp1s0 --hostname=workshop-edge-utils --bootproto=dhcp
network --device=enp0s31f6 --bootproto=static --ip=192.168.40.1 --netmask=255.255.255.0
firstboot --disable
selinux --enforcing
#firewall --enabled

# Configure users
#rootpw $2b$10$C0ecnR5cPoWFuJiMv4O6duYr01t8qdkF6pG2t5b.6BKiEtpSekC22 --iscrypted
rootpw --lock
user --plaintext --name=redhat --password=redhat
user --name=ansible --groups=wheel --password=$2b$10$C0ecnR5cPoWFuJiMv4O6duYr01t8qdkF6pG2t5b.6BKiEtpSekC22 --iscrypted

# Minimal package setup
cdrom
%packages
@^minimal-environment
#@^graphical-server-environment
wpa_supplicant
#tigervnc-server
%end

# Post install configuration
%post --log=/var/log/anaconda/post-install.log --erroronfail

# Allow the default user to run sudo commands without password
echo -e 'redhat\tALL=(ALL)\tNOPASSWD: ALL' > /etc/sudoers.d/microshift

# Import Red Hat public keys to allow RPM GPG check (not necessary if a system is registered)
if ! subscription-manager status >& /dev/null ; then
   rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-*
fi

# Make the KUBECONFIG from MicroShift directly available for the root user
echo -e 'export KUBECONFIG=/var/lib/microshift/resources/kubeadmin/kubeconfig' >> /root/.bash_profile

# Configure systemd journal service to persist logs between boots and limit their size to 1G
sudo mkdir -p /etc/systemd/journald.conf.d
cat > /etc/systemd/journald.conf.d/microshift.conf <<EOF
[Journal]
Storage=persistent
SystemMaxUse=1G
RuntimeMaxUse=1G
EOF

# Make sure all the Ethernet network interfaces are connected automatically
for uuid in $(nmcli -f uuid,type,autoconnect connection | awk '$2 == "ethernet" && $3 == "no" {print $1}') ; do
    # Remove autoconnect option from the configuration file to keep it enabled after reboot
    file=$(nmcli -f uuid,filename connection | awk -v uuid=${uuid} '$1 == uuid' | sed "s/${uuid}//g" | xargs)
    sed -i '/autoconnect=.*/d' "${file}"
done

%end

