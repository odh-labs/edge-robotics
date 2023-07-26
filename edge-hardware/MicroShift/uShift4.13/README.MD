This is to setup a KVM based virtual machine with MicroShift 4.13 installed.
The setup for the Red Pill is different as it runs a PXE based bootstrap environment https://gitlab.consulting.redhat.com/RedPill/

In order to create your own local MicroShift 4.13 qcow2 image to run via virsh or Virtual Machine Manager do the following:
Pre-requs:
- Have an DVD iso image availabe at /var/lib/libvirt/images/rhel-9.2-$(uname -m)-dvd.iso
- Internet access to acces kickstart file.
- Copy your OpenShift pull-secret into this (the uShift4.13) directory
- git clone https://github.com/odh-labs/edge-robotics/new/main/edge-hardware/MicroShift/uShift4.13
- rename openshift-pull-secret.sample to openshift-pull-secret add your pull secret to openshift-pull-secret
- update secrets.yaml (after renaming secrets.yaml.sample to secrets.yaml)
- add your public key to the authorized_keys file on the nucs, eg: ssh-copy-id -i ~/.ssh/id_rsa.pub <username>@<NUC_IP>

Option a: Steps to create a KVM image from scratch
- run bootStrapMicroShift.sh
- add the nuc(s) to the hosts file

Option b: Steps for the RedPill
- PXE boot Red Pill Nuc into MicroShift (creates an empty RHEL 9.2 image)

Steps:
- run ansible-playbook -i ./hosts ./microshift.yaml -vv
 






