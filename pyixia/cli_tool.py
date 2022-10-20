# SPDX-License-Identifier: LGPL-2.0-or-later
#
# Copyright (c) 2015 Kontron Europe GmbH
#

import logging
import argparse

from . import Ixia
from .helper import obj_match_attribute_value

ALLOWED_COMMANDS = 'take_ownership clear_ownership \
        start_transmit stop_transmit step_transmit pause_transmit \
        start_capture stop_capture reset_statistics'.split()

ALLOWED_STATISTICS = 'bytes_received bytes_sent \
        bits_received bits_sent \
        frames_received frames_sent \
        fcs_errors framer_fcs_errors fragments'.split()


def exec_commands(pg, commands_list):
    for command in commands_list:
        getattr(pg, command)()


def get_statistics(i, ports, stats):
    fmt = '{!s:>8} ' + ' | {:<18}' * len(stats)
    for port in ports:
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
    parser.add_argument('-c', '--commands', dest='commands',
                        choices=ALLOWED_COMMANDS, action='append',
                        help='execute commands', metavar='CMD')
    parser.add_argument('-s', '--statistics', dest='statistics',
                        choices=ALLOWED_STATISTICS, action='append',
                        help='show statistics', metavar='STAT')

    args = parser.parse_args()

    logging.basicConfig()
    if args.verbose:
        logging.getLogger('').setLevel(logging.INFO)
    if args.debug:
        logging.getLogger('').setLevel(logging.DEBUG)

    i = Ixia(args.url)
    i.connect()
    i.discover()

    if args.commands or args.statistics:
        i.session.login(args.user)
        pg = i.new_port_group()
        pg.create()
        for port in args.ports:
            pg.add_port(i.get_port(port))

        if args.commands:
            exec_commands(pg, args.commands)

        if args.statistics:
            get_statistics(i, pg.ports, args.statistics)

        pg.destroy()
    else:
        print_ports(i)

    i.disconnect()


if __name__ == '__main__':
    main()
