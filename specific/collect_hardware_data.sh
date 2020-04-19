#!/bin/sh
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2019-2020 Nicolas Iooss
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Collect data related to the hardware
#
# This creates files and directory in a new directory named "collected_hwdata"

# Abort if any command failed
set -x -e

# Compute the path to the programs from home-files
HOME_FILES_BIN="$(realpath "$(dirname -- "$0")/../bin")"

if [ -z "$HOME_FILES_BIN" ] || ! [ -d "$HOME_FILES_BIN" ] ; then
    echo >&2 "Unable to find home-files/bin directory (${HOME_FILES_BIN})"
    exit 1
fi
echo "Using programs from ${HOME_FILES_BIN}"

# Create the output directory
mkdir collected_hwdata
cd collected_hwdata

# Create a directory for files that are likely to change everyday
# (for example when a device is plugged/unplugged)
HW_TODAY="hw_$(date -I)"

# Create directories
mkdir -p "${HW_TODAY}" acpi_tables dmi efivars fwupd wmi_bus

# Run usual commands to collect information about connected hardware devices
if command -v lspci > /dev/null 2>&1 ; then
    lspci -nnvvxxx > "${HW_TODAY}/lspci-nnvvxxx.txt"
    lspci -t > "${HW_TODAY}/lspci-t.txt"
fi
if command -v lsusb > /dev/null 2>&1 ; then
    lsusb -v > "${HW_TODAY}/lsusb-v.txt" || true
    lsusb -t > "${HW_TODAY}/lsusb-t.txt" || true
fi
cat /proc/cpuinfo > "${HW_TODAY}/proc_cpuinfo.txt"
cat /proc/self/mountinfo > "${HW_TODAY}/proc_mountinfo.txt"
mount > "${HW_TODAY}/mount.txt"

# Run custom commands
"${HOME_FILES_BIN}/config-summary" > "${HW_TODAY}/config-summary.rst"
"${HOME_FILES_BIN}/graph-hw" --json -o "${HW_TODAY}/graph-hw.json"
if command -v dot > /dev/null 2>&1 ; then
    "${HOME_FILES_BIN}/graph-hw" -i "${HW_TODAY}/graph-hw.json" -o "${HW_TODAY}/graph-hw.svg"
    "${HOME_FILES_BIN}/graph-hw" -i "${HW_TODAY}/graph-hw.json" -o "${HW_TODAY}/graph-hw_tree.svg" --tree
    "${HOME_FILES_BIN}/graph-hw" -i "${HW_TODAY}/graph-hw.json" -o "${HW_TODAY}/graph-hw_pci.svg" --pci
    "${HOME_FILES_BIN}/graph-hw" -i "${HW_TODAY}/graph-hw.json" -o "${HW_TODAY}/graph-hw_tree_pci.svg" --tree --pci
fi

# Collect DMI tables
# dmidecode.bin is a copy /sys/firmware/dmi/tables/DMI with a 32-byte prefix
# from /sys/firmware/dmi/tables/smbios_entry_point, adjusted to reference
# the DMI tables locally.
if [ -e /sys/firmware/dmi/tables/smbios_entry_point ] ; then
    cat /sys/firmware/dmi/tables/smbios_entry_point > dmi/dmi_tables_smbios_entry_point.bin || true
fi
if [ -e /sys/firmware/dmi/tables/DMI ] ; then
    cat /sys/firmware/dmi/tables/DMI > dmi/dmi_tables_dmi.bin || true
fi
if command -v dmidecode > /dev/null 2>&1 ; then
    dmidecode > "dmi/dmidecode.txt" || true
    # This file is intended for "dmidecode --from-dump=dmidecode.bin"
    dmidecode --dump --dump-bin "dmi/dmidecode.bin" || true
fi

# Collect I/OMMU tables
"${HOME_FILES_BIN}/iommu-show" -d > "${HW_TODAY}/iommu-show-d.txt"
if command -v chipsec_util > /dev/null 2>&1 ; then
    if chipsec_util iommu config > "${HW_TODAY}/chipsec_util_iommu_config.txt" ; then
        # The kernel module has successfully been inserted
        chipsec_util iommu list > "${HW_TODAY}/chipsec_util_iommu_list.txt"
        chipsec_util iommu status > "${HW_TODAY}/chipsec_util_iommu_status.txt"
        chipsec_util iommu pt > "${HW_TODAY}/chipsec_util_iommu_pt.txt"

        # Custom command that makes the output readable
        iommu-chipsec -p "${HW_TODAY}/lspci-nnvvxxx.txt" -o "${HW_TODAY}/iommu-chipsec.json" "${HW_TODAY}/chipsec_util_iommu_pt.txt"
    fi
fi

# Collect ACPI tables, with acpica package
if command -v acpidump > /dev/null 2>&1 ; then
    (cd acpi_tables && acpidump -b) || true
    if (cd acpi_tables && iasl -d ./*.dat) ; then
        # Drop the date from the disassembled files
        sed -i -e '6,8s:^\( \* Disassembly of \./\S\+\), .*:\1:' acpi_tables/*.dsl
    fi
fi

# Collect EFI variables
if [ -d /sys/firmware/efi/efivars ] ; then
    cp -r /sys/firmware/efi/efivars/. efivars/
fi

# Collect Firmware information
if command -v fwupdmgr > /dev/null 2>&1 ; then
    fwupdmgr get-devices > fwupd/fwupdmgr_get-devices.txt
    fwupdmgr get-devices --show-all-devices > fwupd/fwupdmgr_all_devices.txt
fi

# Collect WMI description
# Match /sys/devices/platform/PNP0C14:00/wmi_bus/wmi_bus-PNP0C14:00/05901221-D566-11D1-B2F0-00A0C9062910/bmof
for BMOF_FILE in /sys/devices/platform/*/wmi_bus/wmi_bus-*/*/bmof ; do
    if [ -e "$BMOF_FILE" ] ; then
        # Decode this file using bmf2mof from https://github.com/pali/bmfdec
        #    bmf2mof < bmof.bin > bmof.txt
        OUTPUT_FILENAME="$(printf %s "${BMOF_FILE#/sys/devices/platform/}" | sed 's/[^a-zA-Z0-9_.-]/__/g')"
        cat "$BMOF_FILE" > "wmi_bus/${OUTPUT_FILENAME}.bin"
    fi
done

# Collect TPM registers
if [ -e /sys/class/tpm/tpm0/device/pcrs ] ; then
    cat /sys/class/tpm/tpm0/device/pcrs > "${HW_TODAY}/tpm1_pcrs.txt"
fi
if command -v tpm_version > /dev/null 2>&1 ; then
    tpm_version > "${HW_TODAY}/tpm1_version.txt" || true
fi
if command -v tpm2_pcrlist > /dev/null 2>&1 ; then
    tpm2_pcrlist > "${HW_TODAY}/tpm2_pcrlist.txt" || true
fi
if command -v tpm2_pcrread > /dev/null 2>&1 ; then
    tpm2_pcrread > "${HW_TODAY}/tpm2_pcrread.txt" || true
fi
if command -v tpm2_getcap > /dev/null 2>&1 ; then
    tpm2_getcap -l > "${HW_TODAY}/tpm2_getcap-l.txt" || true
    sed 's/^- //' < "${HW_TODAY}/tpm2_getcap-l.txt" | \
    while IFS= read -r CAPABILITY ; do
        tpm2_getcap "${CAPABILITY}" > "${HW_TODAY}/tpm2_getcap_${CAPABILITY}.txt" || true
    done
fi
for KERNEL_SEC_BIOS_MEASUREMENTS in /sys/kernel/security/tpm*/*_bios_measurements ; do
    if [ -e "$KERNEL_SEC_BIOS_MEASUREMENTS" ] ; then
        OUTPUT_FILENAME="tpm_securityfs__$(printf %s "${KERNEL_SEC_BIOS_MEASUREMENTS#/sys/kernel/security/}" | sed 's/[^a-zA-Z0-9_.-]/__/g')"
        cat "$KERNEL_SEC_BIOS_MEASUREMENTS" > "${HW_TODAY}/${OUTPUT_FILENAME}.bin"
        (xxd < "${HW_TODAY}/${OUTPUT_FILENAME}.bin" > "${HW_TODAY}/${OUTPUT_FILENAME}.hex") || true
    fi
done
"${HOME_FILES_BIN}/tpm-show" --quiet-if-not-found > "${HW_TODAY}/tpm-show.txt"

# Remove empty files and directory
find . -type f -empty -delete
find . -type d -empty -delete
