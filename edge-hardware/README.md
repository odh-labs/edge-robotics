Intel NUC 11 Compute Element EBTGLMIV - BIOS Version 0700 - 08/24/2022

Comes preimaged with Ubuntu. Entering BIOS or boot menu during boot with F2 doesn't work.
You need to press the power button for 3 seconds (not shorter and not 4s) until the power light is blinking.
It's to disable secure boot and/or fast boot. More info here: https://www.intel.com/content/www/us/en/support/articles/000005847/intel-nuc.html

PXE boot RHEL
Follow these instructions - be aware that there different instructions for BIOS vs UEFI
https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/performing_an_advanced_rhel_8_installation/preparing-for-a-network-install_installing-rhel-as-an-experienced-user
