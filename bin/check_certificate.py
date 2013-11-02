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


def get_notafter(filename):
    """Get the notAfter field in the specified file"""
    # Certificate request are special
    cmdline = [OPENSSL_CMD, 'x509', '-noout', '-dates', '-in', filename]
    output = subprocess.check_output(cmdline)
    output = output.decode('utf8', errors='ignore')
    for line in output.split('\n'):
        if line.startswith('notAfter='):
            return ssl.cert_time_to_seconds(line[9:])
    raise Exception("No notAfter field found in {}".format(filename))


def check_certificate(filename, verbose=False):
    """Check the validity of the specified certificate"""
    notafter = datetime.datetime.fromtimestamp(get_notafter(filename))
    now = datetime.datetime.now()
    if verbose:
        print("[ ] {}: not after {}".format(filename, notafter))
    if now < notafter:
        diff = notafter - now
        if diff.days > 2:
            diff = "{} days".format(diff.days)
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
        '-v', '--verbose', action='store_true', dest='verbose',
        help="enable verbose mode", default=False)

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
