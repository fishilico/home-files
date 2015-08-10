#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Nicolas Iooss
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
"""Run shellcheck on all shell files

@author: Nicolas Iooss
@license: MIT
"""
import errno
import os
import os.path
import re
import subprocess


# Warnings excluded for every file
SHELLCHECK_EXCLUDED_WARNS = (
    'SC2018',  # Use '[:lower:]' to support accents and foreign alphabets.
    'SC2019',  # Use '[:upper:]' to support accents and foreign alphabets.
    'SC2086',  # Some scripts use the fact that expanded variables change newline to space
)

# Warnings excluded for specific files
# Format: (regexp on the path, warning to be excluded)
SHELLCHECK_SPECIFIC_EXCL_WARNS = (
    # asciitable uses printf without format string to print character from code
    (r'/bin/asciitable$', 'SC2017,SC2059'),

    # Shebang is missing in .bashrc, .zshrc...
    (r'/dotfiles/[^/]+$', 'SC2148'),

    # shellcheck does not like the zsh shebang
    (r'/dotfiles/shell/zsh[^/]+$', 'SC1071'),

    # .shell/aliases and .shell/functions use:
    # * \grep to avoid using the alias
    # * "ls |grep" structure to detect features
    # * expanded variables in trap to automatically remove temporary files
    (r'/dotfiles/shell/(aliases|functions)$', 'SC1001,SC2010,SC2064'),

    # Shell aliases uses variables which expands when defined,
    # and their support is detected through non-POSIX-sh "type alias"
    (r'/bin/polyproxy$', 'SC2039,SC2139'),
    (r'/dotfiles/shell/(aliases|environment|functions)$', 'SC2039,SC2139'),

    # .shell/prompt uses $'\e' in a zsh-specific blob
    (r'/dotfiles/shell/prompt$', 'SC2039'),

    # install.sh and bin/rm-temp use {} in find command, which is not POSIX
    (r'/bin/rm-temp$', 'SC2039'),
    (r'/install\.sh$', 'SC2039'),

    # shellcheck does not known that SAVEHIST and RPROMPT are internal zsh variables
    (r'/dotfiles/(shell/prompt|zshrc)$', 'SC2034'),

    # shellcheck yells a lot about valid zsh syntax
    (r'/dotfiles/shell/zshcompletion$', 'SC2128,SC2016'),

    # bin/config-summary outputs ReStructuredText format, with double backticks
    (r'/bin/config-summary$', 'SC2016'),
)


def get_excluded_warnings(filepath):
    """Get the list of excluded warnings for the specified filepath"""
    exclwarns = list(SHELLCHECK_EXCLUDED_WARNS)
    for pattern, warn in SHELLCHECK_SPECIFIC_EXCL_WARNS:
        if re.match(pattern, filepath):
            exclwarns.append(warn)

    # Reorder the warnings
    joined_exclwarns = ','.join(exclwarns)
    return sorted(joined_exclwarns.split(','))


def test():
    """Run shellcheck on all shell files

    Returns:
        0 on success
        1 on failure
        2 if shellcheck is not installed
    """
    try:
        subprocess.check_output(['shellcheck', '--version'])
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            print("shellcheck not found, aborting test.")
            return 2
        raise
    except subprocess.CalledProcessError:
        print("shellcheck on an simple stream exited with error")
        return 1

    retval = 0
    basedir = os.path.join(os.path.dirname(__file__), os.path.pardir)
    for dirpath, _, files in os.walk(basedir):
        # Ignore files in .git directory
        if '/.git' in dirpath:
            continue

        for filename in sorted(files):
            filepath = os.path.join(dirpath, filename)

            # If there is no extension and the file is known not to be a
            # shell script, the first line is used to find shell scripts
            if '.' not in filename:
                is_shellconfig = (
                    dirpath.endswith('/dotfiles/shell') or
                    '/dotfiles/bash' in filepath or
                    '/dotfiles/profile' in filepath or
                    '/dotfiles/zsh' in filepath)
                if not is_shellconfig:
                    with open(filepath, 'r') as cur_file:
                        firstline = cur_file.readline().rstrip()
                    if 'sh' not in firstline:
                        continue
            elif not filename.lower().endswith('.sh'):
                continue

            exclwarns = get_excluded_warnings(filepath[len(basedir):])
            exitcode = subprocess.call(
                ['shellcheck', '-e', ','.join(exclwarns), filepath])
            if exitcode != 0:
                retval = 1
    return retval


if __name__ == '__main__':
    import sys
    sys.exit(test())
