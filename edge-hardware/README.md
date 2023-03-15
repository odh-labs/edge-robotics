Intel NUC 11 Compute Element EBTGLMIV - BIOS Version 0700 - 08/24/2022

Comes preimaged with Ubuntu. Entering BIOS or boot menu during boot with F2 doesn't work.
You need to press the power button for 3 seconds (not shorter and not 4s) until the power light is blinking.
It's to disable secure boot and/or fast boot. More info here: https://www.intel.com/content/www/us/en/support/articles/000005847/intel-nuc.html

PXE boot RHEL
Follow these instructions - be aware that there different instructions for BIOS vs UEFI
https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/performing_an_advanced_rhel_8_installation/preparing-for-a-network-install_installing-rhel-as-an-experienced-user

DEBUGGING
Tools:
- tcpdump, example: 
sudo tcpdump -i enp0s13f0u3u1 src 192.168.1.4 and dst 192.168.1.4 (capture, output in terminal)
sudo tcpdump  -i enp0s13f0u3u1 -w dhcp.tftp.pcap (catpure, output written to file, file to load into wireshark)
- wireshark

Step 1 - DHCP
- Disable router DHCP, so that DHCP lease comes from your PXE boot server

- What you are looking for with 'systemctl status dhcpd.service' is:
Mar 14 00:07:32 y1 dhcpd[303431]: DHCPDISCOVER from 88:ae:dd:06:18:2e via enp0s13f0u3u1
Mar 14 00:07:33 y1 dhcpd[303431]: DHCPOFFER on 192.168.1.3 to 88:ae:dd:06:18:2e via enp0s13f0u3u1
Mar 14 00:07:33 y1 dhcpd[303431]: DHCPREQUEST for 192.168.1.3 (192.168.1.2) from 88:ae:dd:06:18:2e via enp0s13f0u3u1
Mar 14 00:07:33 y1 dhcpd[303431]: DHCPACK on 192.168.1.3 to 88:ae:dd:06:18:2e via enp0s13f0u3u1

Step 2 - TFTP

systemctl status tftp.service

Step 3 - Boot NUC, get boot menu from PXE Server, reference installation repository and off you go
