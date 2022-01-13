# Set up ProtonVPN

## Steps
- Got ProtonMail Account first
- Log into ProtonVPN with the ProtonMail account
- Install packages
- OS Setup
```
sudo apt install openvpn dialog python3-pip python3-setuptools
sudo pip3 install protonvpn-cli
sudo protonvpn init
# See some of the config
# cat ~/.pvpn-cli/pvpn-cli.cfg
# Disable IPV6
sudo emacs /etc/sysctl.conf
# Add the following
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
net.ipv6.conf.tun0.disable_ipv6 = 1
# Record your connection user/pw (which are not the same as your ProtonVPN account credentials)
xdg-open https://account.protonvpn.com/account#openvpn
# If necessary, check the credentials in the above URL vs this file
sudo cat /home/pwyoung/.pvpn-cli/pvpnpass
# Connect to the fastest server in the US
sudo protonvpn connect --cc US


## Fetch data
https://stockcharts.com/login/index.php
xdg-open ./downloads/test-websites/StockCharts.com/Log\ In\ \|\ StockCharts.com.html
```