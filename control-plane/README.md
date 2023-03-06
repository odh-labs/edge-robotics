MicroShift managed by ACM
-- status: WIP
Quickest Setup: 
- Provision ACM Hub cluster via Red Hat Demo System
- Setup MicroShift on AWS.EC2.
- Instance type - t2.large (MicroShift needs 2vCPUs 2 GB RAM and 10GB storage
- AMI: MicroShift needs LVM (Logical Volume Manager) hence best to search for AMI via 'Red Hat 8 LVM'
- example AMI: aws-marketplace/ProComputers RHEL-8.7-x86_64-LVM-10GiB-HVM-20221220_052520-3686aad7-f1c3-4f97-9872-a6f8176d0f60
- use security group with SSH (your IP) and HTTP/TCP traffic - inbound traffic source IP depends on your use case
- then follow instructions at: https://access.redhat.com/documentation/en-us/red_hat_build_of_microshift/4.12/html/installing/microshift-install-rpm
- or use microshift_setup.sh


