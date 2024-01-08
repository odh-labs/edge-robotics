TODAY=$(date +%F_%H-%M-%S)
VMNAME=EdgeServer9.2-$TODAY
DVDISO=/var/lib/libvirt/images/rhel-9.2-$(uname -m)-dvd.iso
KICKSTART=https://raw.githubusercontent.com/odh-labs/edge-robotics/main/edge-hardware/EdgeServer/edgeServer.ks


#sudo -b bash -c " \
sudo -s \
cd /var/lib/libvirt/images && \
virt-install \
    --name ${VMNAME} \
    --vcpus 4 \
    --memory 16348 \
    --disk path=./${VMNAME}.qcow2,size=100 \
    --network network=default,model=virtio \
    --network  \
    --events on_reboot=restart \
    --location ${DVDISO} \
    --extra-args \"inst.ks=${KICKSTART}\" \
    --noautoconsole \
    --graphic=vnc \
    --debug \
    --wait #\
#"
