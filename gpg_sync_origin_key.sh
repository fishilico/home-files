#!/bin/sh
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2016-2021 Nicolas Iooss
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
# Update the GPG key to the one which is in origin/master branch

GITBRANCH=origin/master
MYGPGKEY=dotfiles/gnupg/mygpgpubkey.asc

cd "$(dirname -- "$0")" || exit $?

# Get the exported key file
git checkout "$GITBRANCH" "$MYGPGKEY" || exit $?
git reset --quiet "$MYGPGKEY" || exit $?

# Grab its fingerprint and compare it with the one used by git
KEYFP="$(LANG=C gpg --dry-run --keyid-format 0xlong --with-fingerprint "$MYGPGKEY" | \
    sed 's/.*=//' | sed -n 2p | tr -cd 0-9A-F)"
GITKEYFP="$(sed -n 's/^[ \t]*signingkey[ ]*=[ ]*//p' dotfiles/gitconfig | \
    head -n1 | tr -d ' ')"
if [ -z "$KEYFP" ] || [ "$KEYFP" != "$GITKEYFP" ]
then
    echo >&2 "[!] Error: $MYGPGKEY has an unexpected key fingerprint."
    exit 1
fi

echo "[+] $MYGPGKEY from $GITBRANCH has the right fingerprint. Importing it."

gpg --import "$MYGPGKEY" || exit $?

echo "[+] Import was successful. Restoring $MYGPGKEY"
git checkout HEAD "$MYGPGKEY" || exit $?
