#!/bin/sh
# Install configuration in home directory

INSTALL_DIR="$HOME"

RETURN_VAL=0

# Go into source directory
cd `dirname $0`
SOURCE_DIR=`pwd -P`

# Create bin directory
echo "Installing files in $INSTALL_DIR"

for SOURCE_FILE in "$SOURCE_DIR"/*
do
    # Add a dot in file names
    FILENAME=`basename "$SOURCE_FILE"`
    DEST_FILE="$INSTALL_DIR/.$FILENAME"
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
