This is to setup a KVM based virtual machine with MicroShift 4.13 installed.
The setup is based on the Red Pill PXE based bootstrap environment https://gitlab.consulting.redhat.com/RedPill/

Pre-requs:
- Have an DVD iso image availabe at /var/lib/libvirt/images/rhel-9.2-$(uname -m)-dvd.iso
- Internet access to acces kickstart file.

Steps:
- PXE boot Red Pill Nuc into MicroShift (creates an empty RHEL 9.2 image)
- git clone https://github.com/odh-labs/edge-robotics/new/main/edge-hardware/MicroShift/uShift4.13 
- add the nuc(s) to the hosts file
- rename openshift-pull-secret.sampel to openshift-pull-secret add your pull secret to openshift-pull-secret
- update secrets.yaml (after renaming secrets.yaml.sample to secrets.yaml)
- run bootStrapMicroShift.sh
- run ansible-playbook -i ./hosts ./microshift.yaml -vv

