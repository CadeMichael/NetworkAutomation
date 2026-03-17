#!/bin/sh
sudo ip tuntap add dev tap0 mode tap
sudo ip link set dev tap0 up
sudo ip addr add 198.51.100.2/24 dev tap0
