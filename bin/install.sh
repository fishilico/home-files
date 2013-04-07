#!/bin/sh
# Install scripts in ~/bin

INSTALL_DIR="$HOME/bin"

RETURN_VAL=0

# Go into source directory
cd `dirname $0`
SOURCE_DIR=`pwd -P`

# Create bin directory
echo "Installing files in $INSTALL_DIR"
[ -d "$INSTALL_DIR" ] || mkdir -v "$INSTALL_DIR" || exit 1

# Symlink files
for SOURCE_FILE in "$SOURCE_DIR"/*
do
    FILENAME=`basename "$SOURCE_FILE"`
    DEST_FILE="$INSTALL_DIR/$FILENAME"
    # Ignore temporary files
    if [ "x$FILENAME" = "x" -o "x$FILENAME" = "x`basename $0`" ] || \
        (echo $FILENAME |grep -q '^\.') || \
        (echo $FILENAME |grep -q '~$')
    then
        continue
    fi

    # Build symlink
    # Note: if symlink is broken, [ -e ... ] returns false and this fix it
    [ -e "$DEST_FILE" ] || ln -svf "$SOURCE_FILE" "$DEST_FILE"
    if ! [ -L "$DEST_FILE" ]
    then
        echo >&2 "Error: file is not a symlink ($DEST_FILE)"
        RETURN_VAL=1
    elif [ x`readlink "$DEST_FILE"` != x"$SOURCE_FILE" ]
    then
        echo >&2 "Error: wrong target for symlink ($DEST_FILE)"
        echo >&2 "  Expected: $SOURCE_FILE"
        echo >&2 "  Got: `readlink "$DEST_FILE"`"
        RETURN_VAL=1
    fi
done
exit $RETURN_VAL
