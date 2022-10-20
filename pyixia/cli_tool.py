# SPDX-License-Identifier: LGPL-2.0-or-later
#
# Copyright (c) 2015 Kontron Europe GmbH
#

import logging
import sys
import argparse

from . import Ixia
from .ixapi import IxTclHalError
from .helper import obj_match_attribute_value

ALLOWED_PG_CMDS = 'take_ownership clear_ownership \
        start_transmit stop_transmit step_transmit pause_transmit \
        start_capture stop_capture reset_statistics'.split()
ALLOWED_PORT_CMDS = 'factory_defaults mode_defaults'.split()
ALLOWED_STATS = 'bytes_received bytes_sent \
        bits_received bits_sent \
        frames_received frames_sent \
        fcs_errors framer_fcs_errors fragments'.split()


def run_port_cmds(i, ports, cmds):
    for pid in ports:
        port = i.get_port(pid)
        for cmd in cmds:
            getattr(port, cmd)()


def run_pg_cmds(pg, cmds):
    for cmd in cmds:
        getattr(pg, cmd)()


def print_stats(i, ports, stats):
    fmt = '{!s:>8} ' + ' | {:<18}' * len(stats)
    for pid in ports:
        port = i.get_port(pid)
        print(fmt.format(port, *map(lambda s: getattr(port.stats, s), stats)))


def print_ports(i):
    print('%8s | %6s | %s' % ('Port', 'Link', 'Owner'))
    print('---------+--------+-----------------')
    for card in i.chassis.cards:
        if card is None:
            continue
        for port in card.ports:
            state = obj_match_attribute_value(port, 'LINK_STATE_',
                                              port.link_state)
            print('%8s | %6s | %s' % (port, state.lower(), port.owner))


def main():
    parser = argparse.ArgumentParser(prog="ixcli")
    parser.add_argument('url',
                        help='URL to connect to', metavar='URL')
    parser.add_argument('ports', nargs='*',
                        help='operate on these ports', metavar='PORTS')
    parser.add_argument('-v', action='store_true', dest='verbose',
                        help='be more verbose')
    parser.add_argument('-d', action='store_true', dest='debug',
                        help='enable debug mode')
    parser.add_argument('-u', '--user', dest='user', default='pyixia',
                        help='user login', metavar='OWNER')
    parser.add_argument('-c', '--pg-command', dest='pg_cmds',
                        choices=ALLOWED_PG_CMDS, action='append',
                        help='run port group commands', metavar='CMD')
    parser.add_argument('-C', '--port-command', dest='port_cmds',
                        choices=ALLOWED_PORT_CMDS, action='append',
                        help='run port commands', metavar='CMD')
    parser.add_argument('-s', '--stats', dest='stats',
                        choices=ALLOWED_STATS, action='append',
                        help='show statistics', metavar='STAT')

    args = parser.parse_args()

    logging.basicConfig()
    if args.verbose:
        logging.getLogger('').setLevel(logging.INFO)
    if args.debug:
        logging.getLogger('').setLevel(logging.DEBUG)

    try:
        i = Ixia(args.url)
        i.connect()
        i.discover()

        if not args.port_cmds and not args.pg_cmds and not args.stats:
            print_ports(i)
            i.disconnect()
            sys.exit(0)

        i.session.login(args.user)

        if args.port_cmds:
            run_port_cmds(i, args.ports, args.port_cmds)

        if args.pg_cmds:
            pg = i.new_port_group()
            pg.create()
            for port in args.ports:
                pg.add_port(i.get_port(port))

            run_pg_cmds(pg, args.pg_cmds)

            pg.destroy()

        if args.stats:
            print_stats(i, args.ports, args.stats)

        i.disconnect()
    except IxTclHalError as e:
        print('ERROR: {!s}'.format(e))


if __name__ == '__main__':
    main()
