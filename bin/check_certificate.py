#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check OpenSSL certificates for date validity

To retrieve a certificate from an HTTPS webserver, you may use a command like:
    openssl s_client -showcerts -servername www.example.com \
        -connect www.example.com:443 < /dev/null | \
        sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p'
"""

import datetime
import optparse
import ssl
import subprocess
import sys


OPENSSL_CMD = 'openssl'

# Verbosity levels
VERBLVL_QUIET = -1
VERBLVL_DEFAULT = 0
VERBLVL_VERBOSE = 1
VERBLVL_DEBUG = 2


def get_notafter(filename, verbose):
    """Get the notAfter field in the specified file"""
    cmdline = [OPENSSL_CMD, 'x509', '-noout', '-dates', '-in', filename]
    # Guess wether it is PEM or DER by reading the first byte
    with open(filename, 'rb') as certfile:
        beginning = certfile.read(1)
        if beginning == b'-':
            cmdline += ['-inform', 'PEM']
        elif beginning == b'0':
            cmdline += ['-inform', 'DER']
    if verbose >= VERBLVL_DEBUG:
        print("[ ] running: {}".format(' '.join(cmdline)))
    output = subprocess.check_output(cmdline)
    output = output.decode('utf8', errors='ignore')
    for line in output.split('\n'):
        if line.startswith('notAfter='):
            return ssl.cert_time_to_seconds(line[9:])
    raise Exception("No notAfter field found in {}".format(filename))


def check_certificate(filename, verbose=None):
    """Check the validity of the specified certificate"""
    verbose = verbose or VERBLVL_DEFAULT
    notafter = datetime.datetime.fromtimestamp(get_notafter(filename, verbose))
    now = datetime.datetime.now()
    if verbose >= VERBLVL_VERBOSE:
        print("[ ] {}: not after {}".format(filename, notafter))
    if now < notafter:
        diff = notafter - now
        if diff.days > 2:
            diff = "{} days".format(diff.days)
        if verbose >= VERBLVL_DEFAULT:
            print("[+] {} will expire in {}".format(filename, diff))
        return True
    else:
        print("[-] {} has expired since {}".format(filename, notafter))
        return False


def main(argv=None):
    """Parse arguments and run specified actions"""

    parser = optparse.OptionParser(
        usage="usage: %prog [options] CERTFILES")
    parser.add_option(
        '-q', '--quiet', action='store_const', const=VERBLVL_QUIET,
        dest='verbose', help="only show expired certificates")
    parser.add_option(
        '-v', '--verbose', action='store_const', const=VERBLVL_VERBOSE,
        dest='verbose', help="enable verbose mode")
    parser.add_option(
        '-d', '--debug', action='store_const', const=VERBLVL_DEBUG,
        dest='verbose', help="enable debug mode, which implies -v")

    opts, files = parser.parse_args(argv)

    all_ok = True

    for filename in files:
        try:
            if not check_certificate(filename, verbose=opts.verbose):
                all_ok = False
        except subprocess.CalledProcessError as exc:
            print(exc)
            all_ok = False
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())