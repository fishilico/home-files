#!/bin/sh
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2015-2023 Nicolas Iooss
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
# Update all podman containers which are used in bin/podman-...

# Compute the path to the programs from home-files
HOME_FILES_BIN="$(realpath "$(dirname -- "$0")/../bin")"

if [ -z "$HOME_FILES_BIN" ] || ! [ -d "$HOME_FILES_BIN" ] ; then
    echo >&2 "Unable to find home-files/bin directory (${HOME_FILES_BIN})"
    exit 1
fi
echo "Using programs from ${HOME_FILES_BIN}"

set -eux

if podman image exists localhost/podman-bpytop ; then
    "${HOME_FILES_BIN}/podman-bpytop" --update --no-start
fi
if podman image exists localhost/podman-codespell ; then
    "${HOME_FILES_BIN}/podman-codespell" --update /dev/null
fi
if podman image exists localhost/podman-ghidra ; then
    "${HOME_FILES_BIN}/podman-ghidra" --update java --version
fi
if podman image exists localhost/podman-infer ; then
    "${HOME_FILES_BIN}/podman-infer" --update --version
fi
if podman image exists localhost/podman-markdownlint ; then
    "${HOME_FILES_BIN}/podman-markdownlint" --update /dev/null
fi
if podman image exists localhost/podman-vscodium ; then
    "${HOME_FILES_BIN}/podman-vscodium" --update codium --version
fi

# After these updates, update all the other standard images
"${HOME_FILES_BIN}/podman-update"
