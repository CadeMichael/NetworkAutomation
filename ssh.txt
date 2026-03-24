#!/bin/sh
ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 \
               -oHostKeyAlgorithms=+ssh-rsa \
               -oCiphers=+aes128-cbc \
               -s cade@198.51.100.1 netconf
