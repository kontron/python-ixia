#!/usr/bin/env python

import logging
import sys
import time

from pyixia import Ixia, Port

vChassis = '192.168.42.174'
# For Linux servers use 8022
tcp_port = 8022
# Required only for Linux servers
rsa_id = 'C:/Program Files (x86)/Ixia/IxOS/8.20-EA/TclScripts/lib/ixTcl1.0/id_rsa'

vModule = '10.10.10.3'
mac = '00:00:00:00:00:00'

def main():
    logging.basicConfig()
    if len(sys.argv) == 2 and sys.argv[1] == '-v':
        logging.getLogger().setLevel(logging.INFO)
    if len(sys.argv) == 2 and sys.argv[1] == '-d':
        logging.getLogger().setLevel(logging.DEBUG)

    ixia = Ixia(vChassis, tcp_port, rsa_id)
    ixia.connect()
    
    card = ixia.chassis.add_vm_card(vModule, 2)
    port1 = card.add_vm_port(1, 'eth1', mac)
    port2 = card.add_vm_port(2, 'eth2', mac)
    

if __name__ == '__main__':
    main()
