#!/usr/bin/env python

import logging
import sys

from pyixia import Ixia, Port

host = '192.168.42.61'
# For Linux servers use 8022
tcp_port = 4555
# Required only for Linux servers
rsa_id = 'C:/Program Files (x86)/Ixia/IxOS/8.20-EA/TclScripts/lib/ixTcl1.0/id_rsa'

def link_state_str(link_state):
    prefix = 'LINK_STATE_'
    for attr in dir(Port):
        if attr.startswith(prefix):
            val = getattr(Port, attr)
            if val == link_state:
                return attr[len(prefix):]
    return link_state

def main():
    logging.basicConfig()
    if len(sys.argv) == 2 and sys.argv[1] == '-v':
        logging.getLogger().setLevel(logging.INFO)
    if len(sys.argv) == 2 and sys.argv[1] == '-d':
        logging.getLogger().setLevel(logging.DEBUG)

    i = Ixia(host, tcp_port, rsa_id)
    i.connect()
    i.discover()

    print i.chassis.type_name

    print '%8s | %8s | %10s | %s' % ('Port', 'Owner', 'Link State', 'Speeds')
    print '---------+----------+------------+-------------------------------'
    for card in i.chassis.cards:
        if card is None:
            continue
        for port in card.ports:
            print '%8s | %8s | %10s | %s' % (port, port.owner.strip(), link_state_str(port.link_state),
                                             port.supported_speeds())

    i.disconnect()

if __name__ == '__main__':
    main()
