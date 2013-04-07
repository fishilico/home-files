#!/bin/sh
# Format sensors output to have all temperatures in one line
# This script is intended to be used with a generic monitor widget which
# updates temperatures periodically


sensors | sed -n 's/^\([^:]\+\):\s*+\?\(-\?[0-9.]\+.C\).*$/\1:\2/p' |
(
# Make an horizontal array
TITLES=""
TEMPS=""
while read line
do
    TITLE=${line%:*}
    TEMP=${line#*:}
    TITLE=`echo $TITLE | sed 's/^temp/pci/;s/^Physical id /phyid/'`
    TITLE=`printf %-$(echo -n $TEMP |wc -m)s "$TITLE"`
    TITLES=`echo "$TITLES $TITLE"`
    TEMPS=`echo "$TEMPS $TEMP"`
done
echo "$TEMPS"
echo "$TITLES"
) 2>&1 | sed 's/^ \+//'
