#!/usr/bin/env python3

import logging
import sys

from pyixia import Ixia, Port

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

    i = Ixia('ssh://ixia')
    i.connect()
    i.discover()

    print('%8s | %8s | %s' % ('Port', 'Owner', 'Link State'))
    print('---------+----------+-----------------')
    for card in i.chassis.cards:
        if card is None:
            continue
        for port in card.ports:
            print('%8s | %8s | %s' % (port, port.owner,
                    link_state_str(port.link_state)))

    i.disconnect()

if __name__ == '__main__':
    main()
