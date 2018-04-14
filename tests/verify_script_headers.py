#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
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
"""Verify the header of script files

@author: Nicolas Iooss
@license: MIT
"""
import io
import re
import os
import os.path


# Text file extensions
TEXT_EXT = (
    'asc',
    'conf',
    'desktop',
    'ini',
    'json',
    'lang',
    'lua',
    'pa',
    'properties',
    'rst',
    'theme',
    'txt',
    'xml',
    'yml',
)


# MIT license prefixes with hashes
MIT_LICENSE_HASHES = """#
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
"""

# Known license texts
KNOWN_LICENSES = (
    MIT_LICENSE_HASHES,
)
KNOWN_LICENSES_SPDX = (
    '# SPDX-License-Identifier: MIT',
)


class CheckError(Exception):
    """A checker function has failed"""

    def __init__(self, msg):
        super(CheckError, self).__init__(msg)
        self.msg = msg


def check_copyline(copyline):
    """Check that a Copyright line is correctly formatted"""
    matches = re.match(r'Copyright \(c\) ([-0-9]+) (.*)$', copyline)
    if matches is None:
        raise CheckError("Copyright line is wrongly formatted")
    year = matches.group(1)
    try:
        if len(year) == 4:
            if not 2013 <= int(year) < 2142:  # Random upper bound to avoid typo
                raise CheckError("Copyright year out of range")
        elif len(year) == 9 and year[4] == '-':
            if not 2013 <= int(year[:4]) < int(year[5:]) < 2142:
                raise CheckError("Copyright years out of range")
        else:
            raise CheckError("Copyright year in an unknown format")
    except ValueError:
        raise CheckError("Copyright year is not an integer")


def check_copyright_license(copytext):
    """Check that a copyright text matches a known license

    Return what's after on success
    """
    for lic in KNOWN_LICENSES:
        if copytext.startswith(lic):
            return copytext[len(lic):]
    raise CheckError("the license is not known")


def check_copyright_lines(lines):
    """Chech the content of a file copyright

    Return what's after the license on success
    """
    if lines[0].startswith('# '):
        check_copyline(lines[0][2:])
        if lines[1] != '#\n':
            raise CheckError("missing blank line between author and license")
    else:
        raise CheckError("Copyright without hash-prefix")
    return check_copyright_license(''.join(lines[1:]))


def verify_pl(filepath):
    """Verify the header of a perl file"""
    with io.open(filepath, 'r', encoding='utf-8') as curfile:
        firstline = curfile.readline().rstrip()
        if not re.match(r'#!(/usr/bin/| )perl( -w)?$', firstline):
            raise CheckError("bad perl shebang: {}".format(firstline))


def verify_py(filepath):
    """Verify the header of a python file"""
    with io.open(filepath, 'r', encoding='utf-8') as curfile:
        firstline = curfile.readline().rstrip()
        if not re.match(r'#!/usr/bin/env python[23]?$', firstline):
            raise CheckError("bad python shebang: {}".format(firstline))

        # While at it, verify coding:utf8
        secondline = curfile.readline().rstrip()
        if secondline != '# -*- coding: utf-8 -*-':
            raise CheckError("bad python second line in: {}".format(secondline))

        # Verify the SPDX license ID
        line = curfile.readline()
        if not line.startswith('# SPDX-License-Identifier:'):
            raise CheckError(
                "missing SPDX license identifier in Python script")
        if line.rstrip('\n') not in KNOWN_LICENSES_SPDX:
            raise CheckError(
                "unknown SPDX license identifier in Python script: {}".format(
                    line))

        # Verify the copyright information, which begins with hashes
        line = curfile.readline()
        copyright_lines = []
        while line.startswith('#'):
            copyright_lines.append(line)
            line = curfile.readline()
        if not copyright_lines:
            raise CheckError("no Copyright information in Python script")
        afterlicense = check_copyright_lines(copyright_lines)
        if afterlicense:
            raise CheckError("trailing comments after the license")

        # After the copyright information, there should be the module docstring
        if not line.startswith(('"""', 'r"""')):
            raise CheckError("no docstring after copyright")


def verify_sh(filepath):
    """Verify the header of a shell file"""
    with io.open(filepath, 'r', encoding='utf-8') as curfile:
        # The first line should be a shell shebang
        firstline = curfile.readline().rstrip()
        if not re.match(r'#!/bin/(ba|z)?sh$', firstline):
            raise CheckError("bad shell shebang: {}".format(firstline))

        # Then there should be a comment, either copyright or description
        line = curfile.readline()
        if not line.startswith('#'):
            raise CheckError("no comment after shebang")

        # Gather all the comment lines
        comment_lines = []
        while line.startswith('#'):
            comment_lines.append(line)
            line = curfile.readline()

        # Verify copyright, if any
        if not any('copyright' in l.lower() for l in comment_lines):
            # Well... short program don't have to hold a copyright information
            numlines = len(curfile.readlines())
            if numlines > 10:
                raise CheckError("missing copyright information")
            return

        if not comment_lines[0].startswith('# SPDX-License-Identifier:'):
            raise CheckError(
                "missing SPDX license identifier in shell script")
        if comment_lines[0].rstrip('\n') not in KNOWN_LICENSES_SPDX:
            raise CheckError(
                "unknown SPDX license identifier in shell script: {}".format(
                    comment_lines[0]))
        if comment_lines[1] != '#\n':
            raise CheckError(
                "missing blank comment between shebang and copyright")
        afterlicense = check_copyright_lines(comment_lines[2:])
        if not afterlicense.startswith('#\n# '):
            raise CheckError("missing script description after license")


def verify_bin(filepath):
    """Verify the header of an executable file with no extension"""
    # Use io.open, so that UTF-8 are correctly decoded on systems where LANG
    # is empty and locales are not configured
    with io.open(filepath, 'r', encoding='utf-8') as curfile:
        firstline = curfile.readline().rstrip()

    # Use the shebang to find out the type of the file
    if 'python' in firstline:
        return verify_py(filepath)
    if 'sh' in firstline:
        return verify_sh(filepath)
    raise CheckError("unmatched first line of bin: {}".format(firstline))


def test():
    # pylint: disable=too-many-branches
    retval = True
    basedir = os.path.join(os.path.dirname(__file__), os.path.pardir)
    for dirpath, _, files in os.walk(basedir):
        # Ignore files in .git directory
        if '/.git' in dirpath:
            continue

        for filename in sorted(files):
            filepath = os.path.join(dirpath, filename)
            ext = filename.rsplit('.', 1)[1] if '.' in filename else ''
            try:
                if ext in TEXT_EXT:
                    # Skip text files
                    pass
                elif filename in ('.gitignore', 'ignored_files'):
                    # Skip special files
                    pass
                elif ext == 'swp':
                    # Skip ViM swap filed
                    pass
                elif dirpath.endswith('/specific/irssi'):
                    # irssi config are text files
                    pass
                elif dirpath.endswith('/specific/irssi/scripts/autorun'):
                    # Irssi scripts are perl scripts without shebang
                    pass
                elif ext == 'pl':
                    verify_pl(filepath)
                elif ext == 'py':
                    verify_py(filepath)
                elif ext == 'sh':
                    verify_sh(filepath)
                elif dirpath.endswith('/bin') and not ext:
                    # binary files can be of several types
                    verify_bin(filepath)
                elif dirpath.endswith('/dotfiles'):
                    # dotfiles contains text files
                    pass
                elif dirpath.endswith('/dotfiles/shell'):
                    # shell config files are shell files
                    verify_sh(filepath)
                elif dirpath.endswith('/dotfiles/urxvt/ext'):
                    # urxvt extensions are perl files
                    verify_pl(filepath)
                else:
                    raise CheckError("unable to categorise file")
            except CheckError as exc:
                print("{}: {}".format(os.path.relpath(filepath), exc.msg))
                retval = False
    return retval


if __name__ == '__main__':
    import sys
    sys.exit(0 if test() else 1)
