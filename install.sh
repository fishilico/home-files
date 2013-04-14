#!/bin/sh
# Install files in home directory

INSTALL_DIR="$HOME"

# Recursive installation
# Second parameter if a prefix with a dot for hidden directories
install_rec() {
    local SRC_DIR="$1"
    local DST_PREFIX="$2"
    local RETURN_VAL=0

    for SRC_FILE in "$SRC_DIR"/*
    do
        FILENAME=`basename "$SRC_FILE"`
        DST_FILE="$DST_PREFIX$FILENAME"

        # Ignore temporary files
        if [ -z "$FILENAME" ] || \
            (echo $FILENAME |grep -q '^\.') || \
            (echo $FILENAME |grep -q '~$')
        then
            continue
        fi

        if [ -d $SRC_FILE ]
        then
            # Make directory
            [ -d "$DST_FILE" ] || mkdir -v "$DST_FILE"
            if ! [ -d "$DST_FILE" ]
            then
                echo >&2 "Error: file is not a directory ($DST_FILE)"
                RETURN_VAL=1
            else
                # Recursive call into directories
                install_rec "$SRC_FILE" "$DST_FILE/" || RETURN_VAL=1
            fi
        else
            # Build symlink
            # Note: if symlink is broken, [ -e ... ] returns false and this fix it
            [ -e "$DST_FILE" ] || ln -svf "$SRC_FILE" "$DST_FILE"
            if ! [ -L "$DST_FILE" ]
            then
                echo >&2 "Error: file is not a symlink ($DST_FILE)"
                RETURN_VAL=1
            elif [ x`readlink "$DST_FILE"` != x"$SRC_FILE" ]
            then
                echo >&2 "Error: wrong target for symlink ($DST_FILE)"
                echo >&2 "  Expected: $SRC_FILE"
                echo >&2 "  Got: `readlink "$DST_FILE"`"
                RETURN_VAL=1
            fi
        fi
    done
    return $RETURN_VAL
}

# Find our location
cd `dirname $0`
SOURCE_DIR=`pwd -P`
RETURN_VAL=0

# Install home dotfiles
echo "Installing dotfiles in $INSTALL_DIR"
install_rec "$SOURCE_DIR/dotfiles" "$INSTALL_DIR/." || RETURN_VAL=1

# Install custom binaries
BIN_INSTALL_DIR="$INSTALL_DIR/bin"
echo "Installing bin in $INSTALL_DIR"
[ -d "$BIN_INSTALL_DIR" ] || mkdir -v "$BIN_INSTALL_DIR" || exit 1
install_rec "$SOURCE_DIR/bin" "$BIN_INSTALL_DIR/" || RETURN_VAL=1
unset BIN_INSTALL_DIR

exit $RETURN_VAL
