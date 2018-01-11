#!/bin/sh
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2015-2018 Nicolas Iooss
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
# Update local copy of home-files repository

# Find our location
cd "$(dirname -- "$0")" || exit $?

# Download updates
echo "[ ] Fetching $(git config remote.origin.url)..."
git fetch origin || exit $?

# Check that the git history contains GPG-signed commits
if ! gpg --version > /dev/null
then
    echo "[-] Warning: gnupg is not installed. Skipping signature validation."
else
    # Retrieve the key fingerprint from git config and check it is installed
    KEYFP="$(sed -n 's/^[[:space:]]*signingkey[ ]*=[ ]*//p' dotfiles/gitconfig | \
        head -n1 | tr -d ' ')"
    if ! gpg --list-key "$KEYFP" > /dev/null
    then
        echo >&2 "[!] Error: GPG key $KEYFP is not installed."
        exit 1
    fi

    # git log --show-signature is only available with git>=1.7.9
    if [ "$(git log --format='=%G?' --max-count=1)" = '=%G?' ]
    then
        echo "[-] git log does not support GPG signature. Skipping validation."
    else
        # Check that the new commits are GPG-signed (with good or untrusted)
        if git --no-pager log --format='%H=%G?' master..origin/master | grep -v '=[GU]$'
        then
            # This may occur with git 1.7.10, which replaces %G? with nothing
            # In such a case, check --show-signature for the last commit only
            GPGMATCH="$(LANG=C git log --max-count=1 --show-signature origin/master 2>&1 | \
                grep '^gpg: Signature ')"
            if [ -z "$GPGMATCH" ]
            then
                echo >&2 "[!] Error: some commits are not signed."
                exit 1
            else
                echo "[-] git log does not support %G? format. Only validate the last commit."
            fi
        fi

        # Check that the last commit is signed with the good GPG key
        KEYID="$(LANG=C git log --max-count=1 --show-signature origin/master 2>&1 | \
            sed -n -e 's/^gpg: Signature .* key ID \([x0-9A-F]*\)$/\1/p' \
                -e 's/^gpg:[[:space:]]*using RSA key \([x0-9A-F]*\)$/\1/p' | \
            head -n1)"
        if [ -z "$KEYID" ]
        then
            echo >&2 "[!] Error: unable to parse the output of 'git log --show-signature origin/master'."
            exit 1
        fi
        KEYFP_FROMID="$(LANG=C gpg --fingerprint "$KEYID" | sed 's/.*=//' | sed -n 2p | tr -cd 0-9A-F)"
        if [ "$KEYFP_FROMID" != "$KEYFP" ]
        then
            echo >&2 "[!] Error: the last commit has been signed with key $KEYID not in $KEYFP."
            exit 1
        fi
        echo "[+] GPG validation of git history succeeded."
    fi
fi

# Rebase the master branch on origin/master
CURBRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURBRANCH" != master ]
then
    echo "[ ] Checking out master (was on $CURBRANCH)..."
    git checkout master || exit $?
fi
echo "[ ] Updating master by rebasing on top of origin/master..."
git --no-pager diff --stat master..origin/master
git rebase origin/master || exit $?
echo "[+] Branch master has been successfully updated."

if [ "$CURBRANCH" != master ]
then
    echo "[ ] Checking out $CURBRANCH..."
    git checkout "$CURBRANCH" || exit $?
else
    # When using branch master, run the installation script
    echo "[ ] Running install.sh..."
    exec ./install.sh
fi
