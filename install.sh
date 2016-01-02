#!/bin/sh
#
# Copyright (c) 2015-2016 Nicolas Iooss
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
# Install files in home directory

INSTALL_DIR="$HOME"

# Find our location
cd "$(dirname -- "$0")" || exit $?
SOURCE_DIR="$(pwd -P)"

# Recursive installation
# Second parameter if a prefix with a dot for hidden directories
install_rec() {
    local DST_FILE FILENAME IGNPAT_REF IGNPAT_TEST SRC_FILE
    local SRC_DIR="$1"
    local DST_PREFIX="$2"
    local RETURN_VAL=0

    for SRC_FILE in "$SRC_DIR"/*
    do
        FILENAME="${SRC_FILE##*/}"
        DST_FILE="$DST_PREFIX$FILENAME"
        [ -n "$FILENAME" ] || continue

        # Ignore some patterns using built-in functions
        IGNPAT_TEST="${FILENAME#.} ${FILENAME%\~}"
        IGNPAT_REF="$FILENAME $FILENAME"
        for EXT in backup bak orig pyc pyo rej swp tmp
        do
            IGNPAT_TEST="$IGNPAT_TEST ${FILENAME%.$EXT}"
            IGNPAT_REF="$IGNPAT_REF $FILENAME"
        done
        [ "$IGNPAT_TEST" = "$IGNPAT_REF" ] || continue

        if [ -d "$SRC_FILE" ]
        then
            # Make directory
            mkdir -pv "$DST_FILE"
            if ! [ -d "$DST_FILE" ]
            then
                echo >&2 "[!] Error: file is not a directory ($DST_FILE)"
                RETURN_VAL=1
            else
                # Clean-up broken symlinks
                # shellcheck disable=SC2039
                find "$DST_FILE/" -maxdepth 1 -xtype l -exec rm -v {} \;
                # Recursive call into directories
                install_rec "$SRC_FILE" "$DST_FILE/" || RETURN_VAL=1
            fi
        else
            # Build symlink
            # Note: if symlink is broken, [ -e ... ] returns false and this fix it
            [ -e "$DST_FILE" ] || ln -svf "$SRC_FILE" "$DST_FILE"
            if ! [ -L "$DST_FILE" ]
            then
                echo >&2 "[!] Error: file is not a symlink ($DST_FILE)"
                RETURN_VAL=1
            elif [ "x$(readlink "$DST_FILE")" != "x$SRC_FILE" ]
            then
                echo >&2 "[!] Error: wrong target for symlink ($DST_FILE)"
                echo >&2 "[!]   Expected: $SRC_FILE"
                echo >&2 "[!]   Got: $(readlink "$DST_FILE")"
                RETURN_VAL=1
            fi
        fi
    done
    return $RETURN_VAL
}

# Check that the git history contains GPG-signed commits
validate_gpg_gitlog() {
    local DST_FILE GPGMATCH KEYFP KEYID SRC_FILE

    # Check that gpg is installed
    if ! gpg --version > /dev/null
    then
        echo '[-] gnupg is not installed. Skipping signature validation.'
        return 0
    fi

    # Setup our own configuration file if there is none
    SRC_FILE="$SOURCE_DIR/dotfiles/gnupg/gpg.conf"
    DST_FILE="$INSTALL_DIR/.gnupg/gpg.conf"
    if ! [ -e "$DST_FILE" ]
    then
        mkdir -pv -m 700 "$INSTALL_DIR/.gnupg" && ln -svf "$SRC_FILE" "$DST_FILE"
        if ! [ -e "$DST_FILE" ]
        then
            echo >&2 "[!] Error: unable to create $DST_FILE"
            return 1
        fi
    fi

    # Retrieve key fingerprint
    KEYFP="$(sed -n 's/^[ \t]*signingkey[ ]*=[ ]*//p' dotfiles/gitconfig | \
        head -n1 | tr -d ' ')"

    # Import the key if it is not found
    if ! gpg --list-key "$KEYFP" > /dev/null
    then
        echo "[ ] Importing key $KEYFP..."
        gpg --import dotfiles/gnupg/mygpgpubkey.asc || return $?
        gpg --list-key "$KEYFP" > /dev/null || return $?
    fi

    # git log --show-signature is only available with git>=1.7.9
    if [ "$(git log --format='=%G?' --max-count=1)" = '=%G?' ]
    then
        echo '[-] git log does not support GPG signature. Skipping validation.'
        return 0
    fi

    # Check that the 10 last commits are GPG-signed (with good or untrusted)
    if git --no-pager log --format='%H=%G?' --max-count=10 | grep -v '=[GU]$'
    then
        # This may occur with git 1.7.10, which replaces %G? with nothing
        # In such a case, check --show-signature for the last commit only
        GPGMATCH="$(LANG=C git log --max-count=1 --show-signature HEAD 2>&1 | \
            grep '^gpg: Signature ')"
        if [ -z "$GPGMATCH" ]
        then
            echo >&2 '[!] Error: some commits are not signed.'
            return 1
        else
            echo '[-] git log does not support %G? format. Only validate the last commit.'
        fi
    fi

    # Check that the last commit is signed with the good GPG key
    # To do this, grab the key ID which was used and find it among the subkeys
    # Use "git log" instead of "git verify-commit" (git>=2.1.0)
    KEYID="$(LANG=C git log --max-count=1 --show-signature HEAD 2>&1 | \
        sed -n 's/^gpg: Signature .* key ID \([0-9A-F]\+\)$/\1/p' | head -n1)"
    if [ -z "$KEYID" ]
    then
        echo >&2 "[!] Error: unable to parse the output of 'git log --show-signature HEAD'"
        return 1
    fi
    if ! (gpg --list-key "$KEYFP" | grep -q "^sub .*/$KEYID ")
    then
        echo >&2 "[!] Error: the last commit has been signed with key $KEYID not in $KEYFP"
        return 1
    fi

    echo '[+] GPG validation of git history succeeded.'
}

RETURN_VAL=0

# Validate the history
validate_gpg_gitlog || exit $?

# Remove broken hidden symlinks in $INSTALL_DIR and install home dotfiles
echo "[ ] Installing dotfiles in $INSTALL_DIR"
# shellcheck disable=SC2039
find "$INSTALL_DIR/" -maxdepth 1 -name '.*' -xtype l -exec rm -v {} \;
install_rec "$SOURCE_DIR/dotfiles" "$INSTALL_DIR/." || RETURN_VAL=1

# Remove broken symlinks in bin/ and install custom programs
BIN_INSTALL_DIR="$INSTALL_DIR/bin"
echo "[ ] Installing bin in $INSTALL_DIR"
mkdir -pv "$BIN_INSTALL_DIR" || exit 1
# shellcheck disable=SC2039
find "$BIN_INSTALL_DIR/" -maxdepth 1 -xtype l -exec rm -v {} \;
install_rec "$SOURCE_DIR/bin" "$BIN_INSTALL_DIR/" || RETURN_VAL=1
unset BIN_INSTALL_DIR

exit $RETURN_VAL
