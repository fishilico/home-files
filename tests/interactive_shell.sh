#!/bin/sh
#
# Copyright (c) 2015-2017 Nicolas Iooss
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
# Test some tools which are useful in an interactive shell session (functions,
# aliases...) with several shells (bash, zsh, busybox sh...).

ROOTDIR="$(dirname -- "$0")/.."

# By default, run the tests with the available shells
if [ $# -eq 0 ]
then
    RETVAL=0
    for TESTED_SHELL in ash bash busybox dash zsh
    do
        if [ -x "/usr/bin/$TESTED_SHELL" ] || which "$TESTED_SHELL" > /dev/null 2>&1 ; then
            # Re-execute this script with the given shell
            set -- "$0" run "$TESTED_SHELL"
            if [ "$TESTED_SHELL" = "busybox" ]
            then
                # Use "busybox sh"
                set -- sh "$@"
            fi
            if env -i "$TESTED_SHELL" "$@"
            then
                echo "[ OK ] $0 $TESTED_SHELL"
            else
                echo "[FAIL] $0 $TESTED_SHELL"
                RETVAL=1
            fi
        else
            # Skip test if $TESTED_SHELL is not installed
            echo "[SKIP] $0 $TESTED_SHELL"
        fi
    done
    exit $RETVAL
fi

# Check that the first argument is "run", to assert the recursion
if [ $# -ne 2 ] || [ "$1" != "run" ]
then
    echo >&2 "$0: invalid parameters, expected 'run' followed by the chosen shell"
    exit 1
fi

# Print a message and exit with an error status
die() {
    echo >&2 "$0: $*"
    exit 1
}

# Build a temporary HOME
TMPHOME="$(mktemp -d "${TMPDIR:-/tmp}/test-interactive-shell-home-XXXXXX")"
trap 'rm -r "$TMPHOME"' EXIT HUP INT QUIT TERM
if ! (
    cd "$ROOTDIR/dotfiles" &&
    find [0-9a-zA-Z]*/ -type d -exec mkdir -p "$TMPHOME/.{}" ';' &&
    find [0-9a-zA-Z]* -type f -exec ln -s "$(pwd)/{}" "$TMPHOME/.{}" ';' &&
    cd .. &&
    mkdir -p "$TMPHOME/bin" &&
    find bin -type f -exec ln -s "$(pwd)/{}" "$TMPHOME/{}" ';'
)
then
    echo >&2 "$0: Unable to create a temporary HOME"
    exit 1
fi
export HOME="$TMPHOME"

# Define variables which simulate an interactive session from the configuration
# point of view
export PS1='$ '

# Source the configuration
case "$2" in
    bash)
        [ -n "$BASH_VERSION" ] || die "running bash without \$BASH_VERSION. This is not sane!"
        # shellcheck disable=SC2039
        shopt -s expand_aliases
        # shellcheck source=/dev/null
        source "$ROOTDIR/dotfiles/bashrc"
        ;;
    zsh)
        [ -n "$ZSH_VERSION" ] || die "running zsh without \$ZSH_VERSION. This is not sane!"
        # shellcheck source=/dev/null
        . "$ROOTDIR/dotfiles/zshrc"
        ;;
    *)
        # shellcheck source=/dev/null
        . "$ROOTDIR/dotfiles/profile"
esac

# Unalias rm so that the cleaning of the temporary HOME is quiet
# shellcheck disable=SC2039
if type alias > /dev/null 2>&1 ; then
    alias rm=rm
fi

# Check basic environment variables
[ -n "$HOME" ] || die "\$HOME is no longer set"
[ "$HOME" = "$TMPHOME" ] || die "\$HOME is no longer $TMPHOME"
[ -n "$PATH" ] || die "\$PATH is not set"
[ "$PATH" != "${PATH#$HOME/bin:}" ] || die "\$PATH does not begin with $HOME/bin"
[ -n "$PS1" ] || die "\$PS1 is not set"

# Test aliases
# shellcheck disable=2039
if type alias > /dev/null 2>&1 ; then
    ll ~ > /dev/null || die 'alias ll failed'

    # busybox grep does not have -P
    if grep --help 2>&1 |grep -q '[-]P' ; then
        (printf ' \342\231\245\n' | grep-noasc > /dev/null) || die 'alias grep-noasc failed on UTF-8'
        (printf ' \251\n' | grep-noasc > /dev/null) || die 'alias grep-noasc failed on ISO-8859'
        ! (echo abc | grep-noasc) || die 'alias grep-noasc succeeded instead of failing'
    fi
fi

# Test functions
# "whichpkg grep" is great because it tests the distribution support,
# the non-expansion of an alias, etc.
PKGGREP="$(LANG=C whichpkg grep)"
if [ $? = 0 ] ; then
    case "$PKGGREP" in
        # Alpine Linux with busybox (Docker image)
        /bin/grep\ symlink\ target\ is\ owned\ by\ busybox-*)
            ;;
        # Arch Linux
        */bin/grep\ is\ owned\ by\ grep\ *)
            ;;
        # Debian
        grep:\ /bin/grep)
            ;;
        # Gentoo
        sys-apps/grep\ \(/bin/grep\))
            ;;
        # Mac OS X
        /usr/bin/grep)
            ;;
        # Redhat
        grep-*$(uname -m))
            ;;
        *)
            die "whichpkg grep returned an unknown result: $PKGGREP"
            ;;
    esac
else
    # On Debian, busybox dpkg does not support --search, so ignore this failure
    [ "$2" = "busybox" ] || die "function whichpkg failed"
fi
