#!/bin/sh
# Build linux-grsec package for ArchLinux
#
# Patch the AUR package to disable sysfs protection because many Desktop
# application needs it (network interface enumeration, audio card settings, ...)
#
# PolicyKit needs full access to /proc to be able to find process owner from a
# PID. To do that, users dbus and polkitd should belong to group "proc-trusted"
# (maybe only one of these users... This needs more testing).
# This configuration is achieved by following commands:
#     gpasswd proc-trusted -a dbus
#     gpasswd proc-trusted -a polkitd
#
# NTPd needs to read /proc/net/if_inet6 to work in IPv6
# (see http://support.ntp.org/bin/view/Support/KnownOsIssues#Section_9.2.4.2.5.1.)
#     gpasswd proc-trusted -a ntp
#
# To grant an user the right to execute its own executables, he must belong to
# group "tpe-trusted". Also, to do administrative actions without being root,
# being member of group "adm" is a good idea.
#
# Use linux-pax-flags (from linux-pax-flags package) to apply PAX configuration
# to the most common applications of your system, then use paxctl with other
# binaries if needed. For example:
#     paxctl -cPSmXER /usr/bin/truecrypt
# You may edit files in /etc/pax-flags/ to modify linux-pax-flags targets.

# Download Archive from AUR and extract it in a temporary folder
ARCHIVE=linux-grsec.tar.gz
AUR_URL='https://aur.archlinux.org/packages/li/linux-grsec/linux-grsec.tar.gz'
TEMP_DIR=/tmp/linux-grsec-build

# Work in temporary directory
[ -d "$TEMP_DIR" ] || mkdir -p "$TEMP_DIR"
if ! cd "$TEMP_DIR"
then
    echo >&2 "Failed to go into $TEMP_DIR"
    exit 1
fi

# If ARCHIVE is recent enougth, don't download it again
if ! (find "$ARCHIVE" -type f -mtime -1 2> /dev/null |grep -q "$ARCHIVE")
then
    echo "Download $ARCHIVE"
    ! [ -e "$ARCHIVE" ] || mv "$ARCHIVE" "OLD-$ARCHIVE"
    ! [ -e linux-grsec ] || mv linux-grsec OLD-linux-grsec
    wget -O "$ARCHIVE" "$AUR_URL"
    touch "$ARCHIVE"
fi

# Patches to source code fail if they were already applied
rm -rf linux-grsec/src

# Extract AUR package
if [ ! -d linux-grsec ] && ! tar -xzf "$ARCHIVE"
then
    echo >&2 "Failed to extract $ARCHIVE"
    exit 1
fi

if ! cd linux-grsec
then
    echo >&2 "Failed to go into linux-grsec"
    exit 1
fi

# Patch default config:
#   Location: 
#     -> Security options
#       -> Grsecurity
#         -> Grsecurity (GRKERNSEC [=y])
#           -> Customize Configuration
#             -> Filesystem Protections
#               [ ] Sysfs/debugfs restriction
#-CONFIG_GRKERNSEC_SYSFS_RESTRICT=y
#+# CONFIG_GRKERNSEC_SYSFS_RESTRICT is not set
for CONFIG_FILE in config.i686 config.x86_64
do
    OLD_SIG=$(sha256sum $CONFIG_FILE |cut -d\  -f1)
    sed 's/CONFIG_GRKERNSEC_SYSFS_RESTRICT=y/# CONFIG_GRKERNSEC_SYSFS_RESTRICT is not set/' -i $CONFIG_FILE
    NEW_SIG=$(sha256sum $CONFIG_FILE |cut -d\  -f1)
    if [ "$OLD_SIG" != "$NEW_SIG" ]
    then
        echo >&2 "File $CONFIG_FILE was updated"
        sed "s/$OLD_SIG/$NEW_SIG/" -i PKGBUILD
    fi
done


# From now, every line must succeed
set -e
set -x
MENUCONFIG=2 MAKEFLAGS='-j3' makepkg
yaourt -U linux-grsec*.pkg.tar.xz

# Remove Old things
cd ..
! [ -e OLD-linux-grsec ] || rm -rf OLD-linux-grsec
! [ -e "OLD-$ARCHIVE" ] || rm -rf "OLD-$ARCHIVE"
set +x

echo "You may now save $TEMP_DIR/linux-grsec/src/linux-*/.config and remove $TEMP_DIR"
