VMNAME=microshift-starter4.13
DVDISO=/var/lib/libvirt/images/rhel-9.2-$(uname -m)-dvd.iso
KICKSTART=https://raw.githubusercontent.com/odh-labs/edge-robotics/main/edge-hardware/MicroShift/uShift4.13/MicroShift4.13-start.ks

sudo -b bash -c " \
cd /var/lib/libvirt/images && \
virt-install \
    --name ${VMNAME} \
    --vcpus 2 \
    --memory 8128 \
    --disk path=./${VMNAME}.qcow2,size=20 \
    --network network=default,model=virtio \
    --events on_reboot=restart \
    --location ${DVDISO} \
    --extra-args \"inst.ks=${KICKSTART}\" \
    --noautoconsole \
    --wait \
"
