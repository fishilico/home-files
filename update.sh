#!/bin/sh
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
    KEYFP="$(sed -n 's/^[ \t]*signingkey[ ]*=[ ]*//p' dotfiles/gitconfig | \
        head -n1 | tr -d ' ')"
    if ! gpg --list-key "$KEYFP" > /dev/null
    then
        echo >&2 "[-] Error: GPG key $KEYFP is not installed."
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
            echo >&2 "[-] Error: some commits are not signed."
            exit 1
        fi

        # Check that the last commit is signed with the good GPG key
        KEYID="$(LANG=C git log --max-count=1 --show-signature origin/master 2>&1 | \
            sed -n 's/gpg: Signature .* key ID \([0-9A-F]\+\)/\1/p' | head -n1)"
        if [ -z "$KEYID" ]
        then
            echo >&2 "[-] Error: unable to parse the output of 'git log --show-signature HEAD'."
            exit 1
        fi
        if ! (gpg --list-key "$KEYFP" | grep -q "^sub .*/$KEYID ")
        then
            echo >&2 "[-] Error: the last commit has been signed with key $KEYID not in $KEYFP."
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
