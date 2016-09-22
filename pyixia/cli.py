#!/usr/bin/env python

import logging
import sys
import argparse
import socket

from pyixia import Ixia

ALLOWED_COMMANDS='take_ownership clear_ownership \
        start_transmit stop_transmit step_transmit pause_transmit \
        start_capture stop_capture reset_statistics'.split()

ALLOWED_STATISTICS='bytes_received bytes_sent \
        bits_received bits_sent \
        frames_received frames_sent \
        fcs_errors framer_fcs_errors fragments'.split()

ALLOWED_SETTINGS='factory_defaults mode_defaults'.split()

def add_ports(i, pg, ports_list):
    print "ports: ", ports_list

    ports_list = map(lambda x: (int(x[0])-1, int(x[1])-1), ports_list)

    for (card_id, port_id) in ports_list:
        pg.add_port(i.chassis.cards[card_id].ports[port_id])
    
    return ports_list

def exec_commands(pg, commands_list):
    logging.info('port_group objects:\n %s \n', dir(pg))
    for command in commands_list:
        print command
        method = getattr(pg, command)
        method()

def get_statistics(i, ports_list, statistics_list):
    logging.info('stats objects: \n %s \n', 
            dir(i.chassis.cards[0].ports[0].stats))
    print '    Port | ',
    for statistics in statistics_list:
        print '%18s |' % statistics,
    print

    for (card_id, port_id) in ports_list:
        port = i.chassis.cards[card_id].ports[port_id]
        print '%8s | ' % port,
        for statistic in statistics_list:
            method = getattr(port.stats, statistic)
            print '%18d |' % method,
        print

def set_settings(i, ports_list, settings_list):
    for (card_id, port_id) in ports_list:
        port = i.chassis.cards[card_id].ports[port_id]
        for setting in settings_list:
            print 'port: %s, setting: %s' % (port, setting)
            method = getattr(port, setting)
            print "methods of port: " 
            print dir(port)
            method(port)

def main():
    usage = 'usage: %(prog)s <host> [options]'
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('host', help='be more verbose')
    parser.add_argument('-v', action='store_true', dest='verbose',
            help='be more verbose')
    parser.add_argument('-d', action='store_true', dest='debug',
            help='enable debug mode')
    parser.add_argument('-o', '--ownership', dest='ownership', default='pyixia',
            help='use ownership', metavar='OWNER')
    parser.add_argument('-p', '--ports', dest='ports_list', type=int,
            help='connect to card port',
            metavar='card port',
            action='append', nargs=2)
    parser.add_argument('-c', '--commands', dest='commands_string',
            help='execute commands', metavar='command',
            choices=ALLOWED_COMMANDS, action='append')
    parser.add_argument('-s', '--statistics', dest='statistics_list',
            help='show statistics', metavar='statistic_counter',
            choices=ALLOWED_STATISTICS, action='append')
    parser.add_argument('-g', '--Settings', dest='settings_list',
            help='set port settings', metavar='port_setting_argument',
            choices=ALLOWED_SETTINGS, action='append')

    args = parser.parse_args()

    logging.basicConfig()
    if args.verbose:
        logging.getLogger('').setLevel(logging.INFO)
    if args.debug:
        logging.getLogger('').setLevel(logging.DEBUG)

    try:
        i = Ixia(args.host)
        i.connect()
        i.discover()

        i.session.login(args.ownership)
        pg = i.new_port_group()
        pg.create()

        ports_list = add_ports(i, pg, args.ports_list)
        if args.commands_string:
            exec_commands(pg, args.commands_string)

        if args.statistics_list:
            get_statistics(i, ports_list, args.statistics_list)

        if args.settings_list:
            set_settings(i, ports_list, args.settings_list)

        pg.destroy()
        i.disconnect()
    except socket.error as e:
        print e.strerror

if __name__ == '__main__':
    main()
