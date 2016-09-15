#!/usr/bin/env python
import sys
import logging
import readline
from optparse import OptionParser

from pyixia.tclproto import TclClient, TclError

def main():
    usage = 'usage: %prog [options] <host>'
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
        print parser.format_help()
        sys.exit(1)

    host = args[0]

    tcl = TclClient(host)
    tcl.connect()
    if options.autoconnect:
        print tcl.call('ixConnectToChassis %s', host)[1]

    print "Enter command to send. Quit with 'q'."
    try:
        while True:
            cmd = raw_input('=> ')
            if cmd == 'q':
                break
            if len(cmd) > 0:
                try:
                    (res, io) = tcl.call(cmd)
                    print res
                    if io is not None:
                        print io
                except TclError, e:
                    print 'ERROR: %s' % e.result
    except EOFError:
        print 'exitting..'

if __name__ == '__main__':
    main()
