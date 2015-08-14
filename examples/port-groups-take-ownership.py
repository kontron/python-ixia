#!/usr/bin/env python

import logging
import sys

from pyixia import Ixia

def main():
    logging.basicConfig()
    if len(sys.argv) == 2 and sys.argv[1] == '-v':
        logging.getLogger().setLevel(logging.INFO)
    if len(sys.argv) == 2 and sys.argv[1] == '-d':
        logging.getLogger().setLevel(logging.DEBUG)

    i = Ixia('ixia01')
    i.connect()
    i.discover()

    i.session.login('mw')
    pg = i.new_port_group()
    pg.create()
    pg.add_port(i.chassis.cards[0].ports[2])
    pg.add_port(i.chassis.cards[0].ports[3])
    pg.take_ownership()
    pg.destroy()

    i.disconnect()

if __name__ == '__main__':
    main()
