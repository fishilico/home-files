#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Merge a dconf dump file to current configuration"""

import logging
import subprocess
import sys


if sys.version_info < (3,):
    from ConfigParser import SafeConfigParser as ConfigParser
else:
    from configparser import ConfigParser


DCONF_CMD = 'dconf'
DUMP_FILE = 'dconf-dump.ini'

logger = logging.getLogger(__name__)


class DconfError(Exception):
    """Error message from dconf command"""

    def __init__(self, message, code=None):
        self.code = code
        self.message = message
        if code is not None:
            message = "error {}: {}".format(code, message)
        super(DconfError, self).__init__(message)


def _run_command(cmdline):
    """Run a command which outputs something and yield its lines in UTF-8"""
    logger.debug("Run {0}".format(' '.join(cmdline)))
    p = subprocess.Popen(cmdline,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in p.stdout:
        yield line.decode('utf8', errors='ignore').strip()
    retval = p.wait()
    if retval:
        err = p.communicate()[1].decode('utf8', errors='ignore').strip()
        raise DconfError(err, code=retval)


class Dconf(object):
    """Interface to dconf"""

    @staticmethod
    def list(directory=None):
        """List the contents of a dconf directory"""
        # A directory must end with a /
        if directory is None:
            directory = '/'
        elif directory[-1] != '/':
            directory = directory + '/'
        return list(_run_command([DCONF_CMD, 'list', directory]))

    @staticmethod
    def read(key):
        """Read a dconf value"""
        return '\n'.join(_run_command([DCONF_CMD, 'read', key]))

    @staticmethod
    def write(key, value, onlyprint=False):
        """Write a dconf value"""
        logger.info("write: {} = {}".format(key, value))
        if not onlyprint:
            return '\n'.join(_run_command([DCONF_CMD, 'write', key, value]))

    @staticmethod
    def write_if_needed(key, value, onlyprint=False):
        """Write a dconf value if it is changed"""
        old_value = Dconf.read(key)
        if old_value != value:
            logger.info("delete: {} was {}".format(key, old_value))
            Dconf.write(key, value, onlyprint)


def merge_dumpfile(filename, onlyprint=False):
    """Merge a file in the "dconf dump" format"""
    config = ConfigParser()
    config.read(filename)
    for section in config.sections():
        directory = '/' + section + '/'
        for key in config.options(section):
            value = config.get(section, key)
            Dconf.write_if_needed(directory + key, value, onlyprint)


if __name__ == '__main__':
    import os.path
    logging.basicConfig(level=logging.INFO,
                        format='[%(levelname)s] %(message)s')
    filepath = os.path.join(os.path.dirname(__file__), DUMP_FILE)
    logger.info("merge configuration with {}".format(filepath))
    merge_dumpfile(filepath)
