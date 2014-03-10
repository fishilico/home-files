#!/bin/sh
# Detect which Linux distribution is running

# Only Linux is supported
[ "$(uname -s)" = "Linux" ] || exit

# Use LSB release
LSB_ID=$(lsb_release --id --short 2> /dev/null)
if [ -n "$LSB_ID" ]
then
    echo "$LSB_ID" | tr '[A-Z]' '[a-z]'
    exit
fi

# Use OS release
if [ -r /etc/os-release ]
then
    OS_ID=$(sed -n 's/^ID\s*=\s*\(.*\)$/\1/p' /etc/os-release)
    if [ -n "$OS_ID" ]
    then
        echo "$OS_ID"
        exit
    fi
fi

# Use files
if [ -r /etc/arch-release ]
then
    echo "arch"
elif [ -r /etc/debian_version ]
then
    echo "debian"
elif [ -r /etc/gentoo-release ]
then
    echo "gentoo"
elif [ -r /etc/redhat-release ]
then
    echo "redhat"
elif [ -r /etc/SuSE-release ]
then
    echo "suse"
fi
