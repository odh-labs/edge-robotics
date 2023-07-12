MicroShift managed by ACM
-- status: WIP
Quickest Setup: 
- Provision ACM Hub cluster via Red Hat Demo System
- Setup MicroShift on AWS.EC2.
- Instance type - t2.medium or larger (MicroShift needs 2vCPUs 2 GB RAM and 10GB storage
- AMI: MicroShift needs LVM (Logical Volume Manager) hence best to search for AMI via 'Red Hat 8 LVM'
- example AMI: aws-marketplace/ProComputers RHEL-8.7-x86_64-LVM-10GiB-HVM-20221220_052520-3686aad7-f1c3-4f97-9872-a6f8176d0f60
- use security group with SSH (your IP) and HTTP/TCP traffic - inbound traffic source IP depends on your use case
- then follow instructions at: https://access.redhat.com/documentation/en-us/red_hat_build_of_microshift/4.12/html/installing/microshift-install-rpm
- or use microshift_setup.sh


--current issues:
MicroShift bare metal install riddle solved!
3 issues: 
1st issue:was no config in /etc/cni/net.d directory. I observed that each time I tried to install MicroShift, the Wifi lost connection at step 19 of the post install script. You experienced the same last Wednesday while installing on my notebook. And you had no problem installing it on your NUC using wired connection. Using a Ethernet connection without Wifi, I noticed that when MicroShift was first started after installation, it created 10-ovn-kubernets.conf in /etc/cni/net.d. It got passed the no network config issue.
Lesson, can't use Wifi connection to install MicroShift. Use only Wired connection.

2nd issue: VG has no spare. When using the Rhel isntaller, I could not find any option to reserve space in the VG. It always uses up all space. I have to create an additional partition and add it to the VG to get the free space.


3rd issue: MicroShift expect the VG name: rhel. The default VG name in the Rhel Installer is rhel-hostname. Couldn't find VG rhel. Renamed it to rhel and MicroShift was up and running. Deployed apps and everything worked. Unfortunately, on reboot, Rhel did not come up because the root partition (/) was expecting the VG name rhel-hostname. There may be ways to get around this but I wanted it to be a clean install so I re-sintalled Rhel and took into account the observations and everything worked.
Resolution: call VG rhel during inital install.
