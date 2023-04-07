#!/bin/bash

aav2_ip=3.91.70.252


echo "## Checking if some useful tools are installed"
sudo yum list installed netcat &>/dev/null && echo "    netcat installed" || { echo '    netcat not installed, install it with "sudo yum install netcat -y"'; exit 1; }
echo
echo "## Check if passwordless ssh is setup to aav2 server"
ssh -oBatchMode=yes -o StrictHostKeyChecking=no ${aav2_ip} echo > /dev/null 2>&1 && echo "   passwordless ssh is setup" || { echo '    passwordless ssh not setup'; exit 1; }
echo
echo
echo "## Checking CPU architecture"
sudo lscpu | grep -E Architecture
echo
echo "## Checking CPU speed"
sudo lscpu | grep -E "CPU|Hz"
echo
echo
echo "## Checking the number of CPU cores - `nproc --all`"
num=`nproc --all`
if [ $num -ge 20 ]
  then
    echo "  * Excellent for Enterprise Level setup"
elif [ $num -ge 16 ]
  then
    echo "  * Great for Midrange setup"
elif [ "$num" -ge 8 ]
  then
    echo "  * Good for Baseline or POC setup"
else
    echo " * CPU resources too low"
fi
echo
echo
echo "## Checking RAM amount - `free --giga | awk '/^Mem:/{print $2}'`"
ram=`free --giga | awk '/^Mem:/{print $2}'`
if (( "$ram" > "64" ))
  then
    echo " * Excellent for Enterprise and Midrange level setup"
elif (( "$ram" > "32" ))
  then
    echo " * Great for Baseline and POC"
else
  echo " * RAM too low"
fi
echo
echo
echo "## Checking Root file system"
echo " * Device: ` df -h / |awk '{ print $1 }'|tail -1`"
echo " * Aavailable: ` df -h / |awk '{ print $4 }'|tail -1`"
echo " * Type: ` df -T / |awk '{ print $2 }'|tail -1`"
echo "## Checking data file system"
echo " * Device: ` df -h /data |awk '{ print $1 }'|tail -1`"
echo " * Available: `df -h /data |awk '{ print $4 }'|tail -1`"
echo " * Type: ` df -T /data |awk '{ print $2 }'|tail -1`"
echo "## Checking backup file system"
echo " * Device: ` df -h /backup |awk '{ print $1 }'|tail -1`"
echo " * Available: `df -h /backup |awk '{ print $4 }'|tail -1`"
echo " * Type: ` df -T /backup |awk '{ print $2 }'|tail -1`"

echo
echo "## checking mount settings, makesure nosuid and noexec is not used"
cat /etc/fstab

echo
echo "## OS version"
cat /etc/redhat-release

echo
echo
echo "## Checking firewall is on"
sudo systemctl status firewalld
sudo iptables -L

echo
echo
echo "## alation cloud access check"
nc -zv 52.4.59.229 443
echo
