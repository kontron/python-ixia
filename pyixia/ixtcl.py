# SPDX-License-Identifier: LGPL-2.0-or-later
#
# Copyright (c) 2015 Kontron Europe GmbH
#

import sys
import logging
import readline
from urllib.parse import urlparse
from optparse import OptionParser

from .tclproto import TclSSHClient, TclSocketClient, TclError


def main():
    usage = 'usage: %prog [options] <host/url>'
    parser = OptionParser(usage=usage)
    parser.add_option('-a', action='store_true', dest='autoconnect',
                      help='autoconnect to chassis')
    parser.add_option('-v', action='store_true', dest='verbose',
                      help='be more verbose')

    (options, args) = parser.parse_args()

    logging.basicConfig()
    if options.verbose:
        logging.getLogger('pyixia.tclproto').setLevel(logging.DEBUG)

    if len(args) < 1:
        print(parser.format_help())
        sys.exit(1)

    o = urlparse(args[0], scheme='socket')
    host = o.netloc or o.path
    if o.scheme == 'socket':
        tcl = TclSocketClient(host)
    elif o.scheme == 'ssh':
        tcl = TclSSHClient(host)
    else:
        print('Unknown URL scheme "%s"' % o.scheme)
        sys.exit(1)

    tcl.connect()
    if options.autoconnect:
        print(tcl.call('ixConnectToChassis %s', host)[1])

    print("Enter command to send. Quit with 'q'.")
    try:
        while True:
            cmd = input('=> ')
            if cmd == 'q':
                break
            if len(cmd) > 0:
                try:
                    (res, io) = tcl.call(cmd)
                    print(res)
                    if io is not None:
                        print("output: %s" % io)
                except TclError as e:
                    print('ERROR: %s' % e.result)
    except EOFError:
        print('exitting..')


if __name__ == '__main__':
    main()
