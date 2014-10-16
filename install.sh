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
        FILENAME="`basename "$SRC_FILE"`"
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

        if [ -d $SRC_FILE ]
        then
            # Make directory
            mkdir -pv "$DST_FILE"
            if ! [ -d "$DST_FILE" ]
            then
                echo >&2 "Error: file is not a directory ($DST_FILE)"
                RETURN_VAL=1
            else
                # Clean-up broken symlinks
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
                echo >&2 "Error: file is not a symlink ($DST_FILE)"
                RETURN_VAL=1
            elif [ "x`readlink "$DST_FILE"`" != "x$SRC_FILE" ]
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
cd "`dirname $0`"
SOURCE_DIR="`pwd -P`"
RETURN_VAL=0

# Remove broken hidden symlinks in $INSTALL_DIR and install home dotfiles
echo "Installing dotfiles in $INSTALL_DIR"
find "$INSTALL_DIR/" -maxdepth 1 -name '.*' -xtype l -exec rm -v {} \;
install_rec "$SOURCE_DIR/dotfiles" "$INSTALL_DIR/." || RETURN_VAL=1

# Remove broken symlinks in bin/ and install custom programs
BIN_INSTALL_DIR="$INSTALL_DIR/bin"
echo "Installing bin in $INSTALL_DIR"
mkdir -pv "$BIN_INSTALL_DIR" || exit 1
find "$BIN_INSTALL_DIR/" -maxdepth 1 -xtype l -exec rm -v {} \;
install_rec "$SOURCE_DIR/bin" "$BIN_INSTALL_DIR/" || RETURN_VAL=1
unset BIN_INSTALL_DIR

exit $RETURN_VAL
