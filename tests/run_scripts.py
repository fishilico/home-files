#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2022 Nicolas Iooss
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
"""Run some scripts in bin/ which does not modify anything on the system

@author: Nicolas Iooss
@license: MIT
"""
import logging
import optparse
import os
import os.path
import re
import subprocess
import sys


logger = logging.getLogger(__name__)


# Tell for every script how it is executed:
# * direct: without any special arguments
# * help: run "script --help", useful for programs requiring user interaction
# * args[arguments]: run "script arguments"
# * never: never run the script
#
# Some programs requires other commands to exist, in which case these commands
# are written in a comma-separated list in parentheses before the actual type.
BIN_SCRIPTS = {
    'acpi-bat': '(acpi)args[--one-shot]',
    'afl-sysctl-config': 'never',
    'aplaytest': 'never',
    'asciitable': 'direct',
    'capabilities': '(/proc)direct',
    'captive-portal': '(python3)help',
    'check-certificate': 'help',
    'chromium-incognito': '(chromium)never',
    'clang-format-meld': '(clang-format)direct',
    'clean-pdf': 'never',
    'colortable': 'direct',
    'compile-netbpf': '(tcpdump,/proc)direct',
    'config-summary': 'direct',
    'crc32': 'args[Hello, world!]',
    'data-dir': 'help',
    'dconf-dump': '(dconf)direct',
    'debian-purge-packages': 'never',
    'decode-jwt': 'help',
    'denastify-ssh': 'args[-h]',
    'detect-distro': '(/usr/include/linux)direct',
    'disable-net-services': 'never',
    'display-proc-maps': '(/proc)direct',
    'docker-purge': 'never',
    'docker-update': 'never',
    'dump-arch': 'direct',
    'dxrandr': 'never',
    'enter-container': 'never',
    'errno': 'args[42]',
    'escat': 'help',
    'eth-disable-offload': 'never',
    'find-broken-libdep': '(python3)help',
    'firefox-private': '(firefox)help',
    'flatpak-steam-valve': 'never',
    'floatenc': 'args[0x42280000]',
    'gcore_everything': 'never',
    'getaddr': 'args[localhost]',
    'get-power-rights': '(dbus-send|gdbus)direct',
    'git-single-fixup': 'args[-h]',
    'graph-hw': 'direct',
    'gsettings-dump': '(gsettings)direct',
    'ical-decode': 'help',
    'iommu-chipsec': 'help',
    'iommu-show': 'direct',
    'iptables-rev': 'args[-A INPUT -j DROP]',
    'iptables-stats': '(iptables,ip6tables)direct',
    'launch-gpg-ssh-agent': 'never',
    'list-https-ciphers': 'never',
    'list-ipc': '(/proc)direct',
    'list-namespaces': '(/proc)direct',
    'lsofdel': '(lsof)direct',
    'luksfile': 'args[-h]',
    'makecleanpkg': 'never',
    'mount-tree': '(/proc)direct',
    'musickbd': 'never',
    'nft-dump': '(nft)direct',
    'nonet': 'never',
    'noproxy': 'args[true]',
    'ntpd-stats': '(ntpdc)direct',
    'pacman-disowned': 'never',
    'ping6-local': 'args[-h]',
    'ping-box': 'never',
    'podman-bpytop': 'never',
    'podman-codespell': 'never',
    'podman-ghidra': 'never',
    'podman-infer': 'never',
    'podman-markdownlint': 'never',
    'podman-purge': 'never',
    'podman-update': 'never',
    'podman-vscodium': 'never',
    'rm-temp': 'never',
    'ruby-gem-home': '(ruby)args[ruby --version]',
    'scan-ip4priv': 'never',
    'selinux-audit-log': '(python>=3.6)help',
    'sensors-temp': '(sensors)direct',
    'set-title': 'direct',
    'setup-dumpcap': 'never',
    'shred-dir': 'never',
    'smtp-send': 'help',
    'suid-list': 'args[-p]',
    'syscall': '(/usr/include/asm|/usr/include/linux|/usr/src/linux)args[-l]',
    'systemd-analyze-plot': 'never',
    'tab2space': 'never',
    'tpm-show': '(python>=3.7)help',
    'update-packages': 'never',
    'useful-selinux-modules': '(python>=3.6)help',
    'vagrant-wireshark': 'args[-h]',
    'vlc': 'never',
    'who-is-here': 'direct',
    'xscreen-resolution': 'never',
    'xfconf-dump': '(xfconf-query)direct',
}

# Path to bin/ directory
BIN_DIR = os.path.join(os.path.dirname(__file__), os.pardir, 'bin')


class CheckError(Exception):
    """A checker function has failed"""

    def __init__(self, msg):
        super(CheckError, self).__init__(msg)
        self.msg = msg


def is_installed(program):
    """Check whether the specified program is accessible in the PATH

    If program is an absolute PATH, check that is path exists
    """
    # If there is a dependency on Python, compare the version with the current
    matches = re.match(r'^python>=([23])\.([0-9]+)$', program)
    if matches:
        matching_version = (int(matches.group(1)), int(matches.group(2)))
        return sys.version_info >= matching_version

    if program.startswith('/'):
        return os.path.exists(program)
    for pathdir in os.environ.get('PATH', '').split(os.pathsep):
        if os.path.exists(os.path.join(pathdir, program)):
            return True
    return False


def build_cmdline_from_spec(prog, spec):
    """Build a command-line argument list from a BIN_SCRIPTS specification

    Return None if the command is not to be run
    """
    if spec.startswith('('):
        # Check for dependencies
        closing_paren = spec.index(')')
        deps = spec[1:closing_paren].split(',')
        for ordep in deps:
            choices = ordep.split('|')
            if not all(is_installed(dep) for dep in choices):
                logger.debug("skip %s because %s is missing", prog,
                             " or ".join(choices))
                return None
        spec = spec[closing_paren + 1:]

    if spec == 'never':
        return None
    if spec == 'direct':
        return [prog]
    if spec == 'help':
        return [prog, '--help']
    if spec.startswith('args[') and spec.endswith(']'):
        return [prog] + spec[5:-1].split(' ')
    raise CheckError("unknown specification %r" % spec)


def run_program(filepath, cmdline, show_output, show_error):
    """Run the specified program with the given command line"""
    logger.info("running: %s", ' '.join(cmdline))
    if show_output:
        print("%s:" % ' '.join(cmdline))

    with open(os.devnull, 'r+') as devnull:
        process = subprocess.Popen(
            cmdline,
            executable=filepath,
            stdin=devnull,
            stdout=None if show_output else devnull,
            stderr=None if show_error else devnull)

    exitcode = process.wait()
    if exitcode != 0:
        raise CheckError("program exited with code %d" % exitcode)


def test(argv=None):
    """Run some scripts in bin/"""
    parser = optparse.OptionParser(
        usage="usage: %prog [options]")
    parser.add_option(
        '-d', '--debug', action='store_true', dest='debug',
        help="display debug messages")
    parser.add_option(
        '-o', '--show-output', action='store_true', dest='show_output',
        help="show the output of programs")
    parser.add_option(
        '-v', '--verbose', action='store_true', dest='verbose',
        help="be verose")
    opts = parser.parse_args(argv)[0]

    logging.basicConfig(
        format='[%(levelname)5s] %(message)s',
        level=logging.DEBUG if opts.debug else (
            logging.INFO if opts.verbose else logging.WARN))

    retval = True
    bin_files = sorted(os.listdir(BIN_DIR))
    for prog in bin_files:
        try:
            spec = BIN_SCRIPTS.get(prog)
            if spec is None:
                # No spec, it needs to be added to BIN_SCRIPTS
                raise CheckError("unknown program, not in BIN_SCRIPTS")

            cmdline = build_cmdline_from_spec(prog, spec)
            if cmdline is None:
                logger.debug("skip %s", prog)
                continue

            filepath = os.path.join(BIN_DIR, prog)
            run_program(filepath, cmdline,
                        show_output=opts.show_output,
                        show_error=opts.debug or opts.verbose)
        except CheckError as exc:
            logger.error("%s: %s", prog, exc.msg)
            retval = False

    # Test that all files in BIN_SCRIPTS were used
    unused_files = set(BIN_SCRIPTS) - set(bin_files)
    if unused_files:
        logger.error("The following programs were declared but not found:")
        for entry in unused_files:
            logger.error("* %s", entry)
        retval = False

    return retval


if __name__ == '__main__':
    sys.exit(0 if test() else 1)
