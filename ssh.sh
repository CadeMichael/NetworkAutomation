#!/bin/sh
ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 \
               -oHostKeyAlgorithms=+ssh-rsa \
               -oCiphers=+aes128-cbc \
               lab@198.51.100.12
