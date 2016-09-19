# Copyright (c) 2015  Kontron Europe GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import logging
from tclproto import TclClient
from ixapi import _MetaIxTclApi, TclMember, FLAG_RDONLY
from ixapi import IxTclHalApi, IxTclHalError

log = logging.getLogger(__name__)

class PortGroup(object):
    START_TRANSMIT = 7
    STOP_TRANSMIT = 8
    START_CAPTURE = 9
    STOP_CAPTURE = 10
    RESET_STATISTICS = 13
    PAUSE_TRANSMIT = 15
    STEP_TRANSMIT = 16
    TRANSMIT_PING = 17
    TAKE_OWNERSHIP = 40
    TAKE_OWNERSHIP_FORCED = 41
    CLEAR_OWNERSHIP = 42
    CLEAR_OWNERSHIP_FORCED = 43

    __metaclass__ = _MetaIxTclApi
    __tcl_command__ = 'portGroup'
    __tcl_members__ = [
            TclMember('lastTimeStamp', type=int, flags=FLAG_RDONLY),
    ]

    next_free_id = 1

    def __init__(self, api, id=None):
        self._api = api
        if id is None:
            self.id = self.next_free_id
            self.next_free_id += 1
        else:
            self.id = id

    def _ix_get(self):
        pass

    def create(self):
        self._api.call_rc('portGroup create %s', self.id)

    def destroy(self):
        self._api.call_rc('portGroup destroy %s', self.id)

    def add_port(self, port):
        self._api.call_rc('portGroup add %s %d %d %d',
                self.id, *port._port_id())

    def del_port(self, port):
        self._api.call_rc('portGroup del %s %d %d %d',
                self.id, *port._port_id())

    def _set_command(self, cmd):
        self._api.call_rc('portGroup setCommand %s %d', self.id, cmd)

    def start_transmit(self):
        self._set_command(self.START_TRANSMIT)

    def stop_transmit(self):
        self._set_command(self.STOP_TRANSMIT)

    def start_capture(self):
        self._set_command(self.START_CAPTURE)

    def stop_capture(self):
        self._set_command(self.STOP_CAPTURE)

    def reset_statistics(self):
        self._set_command(self.RESET_STATISTICS)

    def pause_transmit(self):
        self._set_command(self.PAUSE_TRANSMIT)

    def step_transmit(self):
        self._set_command(self.STEP_TRANSMIT)

    def transmit_ping(self):
        self._set_command(self.TRANSMIT_PING)

    def take_ownership(self, force=False):
        if not force:
            self._set_command(self.TAKE_OWNERSHIP)
        else:
            self._set_command(self.TAKE_OWNERSHIP_FORCED)

    def clear_ownership(self, force=False):
        if not force:
            self._set_command(self.CLEAR_OWNERSHIP)
        else:
            self._set_command(self.CLEAR_OWNERSHIP_FORCED)


class Statistics(object):
    """Per port statistics."""
    __metaclass__ = _MetaIxTclApi
    __tcl_command__ = 'stat'
    __tcl_members__ = [
            TclMember('bytesReceived', type=int, flags=FLAG_RDONLY),
            TclMember('bytesSent', type=int, flags=FLAG_RDONLY),
            TclMember('bitsReceived', type=int, flags=FLAG_RDONLY),
            TclMember('bitsSent', type=int, flags=FLAG_RDONLY),
            TclMember('framesReceived', type=int, flags=FLAG_RDONLY),
            TclMember('framesSent', type=int, flags=FLAG_RDONLY),
            TclMember('fcsErrors', type=int, flags=FLAG_RDONLY),
            TclMember('framerFCSErrors', type=int, flags=FLAG_RDONLY),
            TclMember('fragments', type=int, flags=FLAG_RDONLY),
    ]

    def __init__(self, api, port):
        self._api = api
        self.port = port

    def _ix_get(self, member):
        self._api.call('stat get %s %d %d %d',
                member.name, *self.port._port_id())

    def _ix_set(self, member):
        self._api.call('stat set %s %d %d %d',
                member.name, *self.port._port_id())


class Port(object):
    __metaclass__ = _MetaIxTclApi
    __tcl_command__ = 'port'
    __tcl_members__ = [
            TclMember('name'),
            TclMember('owner', flags=FLAG_RDONLY),
            TclMember('type', type=int, flags=FLAG_RDONLY),
            TclMember('loopback'),
            TclMember('flowControl'),
            TclMember('linkState', type=int, flags=FLAG_RDONLY),
            TclMember('portMode', type=int),
            TclMember('transmitMode'),
    ]

    LINK_STATE_DOWN = 0
    LINK_STATE_UP = 1
    LINK_STATE_LOOPBACK = 2
    LINK_STATE_MII_WRITE = 3
    LINK_STATE_RESTART_AUTO = 4
    LINK_STATE_AUTO_NEGOTIATING = 5
    LINK_STATE_MII_FAIL = 6
    LINK_STATE_NO_TRANSCEIVER = 7
    LINK_STATE_INVALID_ADDRESS = 8
    LINK_STATE_READ_LINK_PARTNER = 9
    LINK_STATE_NO_LINK_PARTNER = 10
    LINK_STATE_RESTART_AUTO_END = 11
    LINK_STATE_FPGA_DOWNLOAD_FAILED = 12
    LINK_STATE_LOSS_OF_FRAME = 24
    LINK_STATE_LOSS_OF_SIGNAL = 25

    def __init__(self, tcl, parent, id):
        self.card = parent
        self.id = id
        self._api = tcl
        self.stats = Statistics(tcl, self)

    def _ix_get(self, member):
        self._api.call_rc('port get %d %d %d', *self._port_id())

    def _ix_set(self, member):
        self._api.call_rc('port set %d %d %d', *self._port_id())

    def _port_id(self):
        return self.card._card_id() + (self.id,)

    def __str__(self):
        return '%d/%d/%d' % self._port_id()

    def factory_defaults(self, port):
        self._api.call('port setFactoryDefaults %d %d %d',
                *port._port_id())
        self._api.call('port write %d %d %d', *port._port_id())

    def mode_defaults(self, port):
        self._api.call('port setFactoryDefaults %d %d %d',
                *port._port_id())
        self._api.call('port write %d %d %d', *port._port_id())


class Card(object):
    __metaclass__ = _MetaIxTclApi
    __tcl_command__ = 'card'
    __tcl_members__ = [
            TclMember('cardOperationMode', type=int, flags=FLAG_RDONLY),
            TclMember('clockRxRisingEdge', type=int),
            TclMember('clockSelect', type=int),
            TclMember('clockTxRisingEdge', type=int),
            TclMember('fpgaVersion', type=int, flags=FLAG_RDONLY),
            TclMember('hwVersion', type=int, flags=FLAG_RDONLY),
            TclMember('portCount', type=int, flags=FLAG_RDONLY),
            TclMember('serialNumber', type=int, flags=FLAG_RDONLY),
            TclMember('txFrequencyDeviation', type=int),
            TclMember('type', type=int, flags=FLAG_RDONLY),
            TclMember('typeName'),
    ]

    TYPE_NONE = 0

    def __init__(self, api, parent, id):
        self.chassis = parent
        self.id = id
        self.ports = []
        self._api = api

    def _ix_get(self, member):
        self._api.call_rc('card get %d %d', *self._card_id())

    def _ix_set(self, member):
        self._api.call_rc('card set %d %d', *self._card_id())

    def discover(self):
        for pid in xrange(self.port_count):
            pid += 1 # one-based
            port = Port(self._api, self, pid)
            log.info('Adding port %s', port)
            self.ports.append(port)

    def _card_id(self):
        return (self.chassis.id, self.id)

    def __str__(self):
        return '%d/%d' % self._card_id()


class Chassis(object):
    __metaclass__ = _MetaIxTclApi
    __tcl_command__ = 'chassis'
    __tcl_members__ = [
            TclMember('baseIpAddress'),
            TclMember('cableLength', type=int),
            TclMember('hostname', flags=FLAG_RDONLY),
            TclMember('id', type=int),
            TclMember('ipAddress', flags=FLAG_RDONLY),
            TclMember('ixServerVersion', flags=FLAG_RDONLY),
            TclMember('master', flags=FLAG_RDONLY),
            TclMember('maxCardCount', type=int, flags=FLAG_RDONLY),
            TclMember('name'),
            TclMember('operatingSystem', type=int, flags=FLAG_RDONLY),
            TclMember('sequence', type=int),
            TclMember('type', type=int, flags=FLAG_RDONLY),
            TclMember('typeName', flags=FLAG_RDONLY),
    ]

    TYPE_1600 = 2
    TYPE_200 = 3
    TYPE_400 = 4
    TYPE_100 = 5
    TYPE_400C = 6
    TYPE_1600T = 7
    TYPE_DEMO = 9
    TYPE_OPTIXIA = 10
    TYPE_OPIXJR = 11
    TYPE_400T = 14
    TYPE_250 = 17
    TYPE_400TF = 18
    TYPE_OPTIXIAX16 = 19
    TYPE_OPTIXIAXL10 = 20
    TYPE_OPTIXIAXM12 = 22

    OS_UNKNOWN = 0
    OS_WIN95 = 1
    OS_WINNT = 2
    OS_WIN2000 = 3
    OS_WINXP = 4

    def __init__(self, api, host):
        self.host = host
        self.cards = []
        self._api = api

    def _ix_add(self):
        self._api.call_rc('chassis add %s', self.host)

    def _ix_del(self):
        self._api.call_rc('chassis del %s', self.host)

    def _ix_get(self, member):
        self._api.call_rc('chassis get %s', self.host)

    def _ix_set(self, member):
        self._api.call_rc('chassis set %s', self.host)

    def connect(self, chassis_id=1):
        self._ix_add()
        self.id = chassis_id

    def disconnect(self):
        self._ix_del()

    def discover(self):
        log.info('Discover chassis %d (%s)', self.id, self.type_name)
        for cid in xrange(self.max_card_count):
            # unfortunately there is no config option which cards are used. So
            # we have to iterate over all possible card ids and check if we are
            # able to get a handle.
            cid += 1 # one-based
            try:
                card = Card(self._api, self, cid)
                log.info('Adding card %s (%s)', card, card.type_name)
                card.discover()
                self.cards.append(card)
            except IxTclHalError:
                # keep in sync with card ids
                self.cards.append(None)

class Session(object):
    __metaclass__ = _MetaIxTclApi
    __tcl_command__ = 'session'
    __tcl_members__ = [
            TclMember('userName', flags=FLAG_RDONLY),
            TclMember('captureBufferSegmentSize', type=int),
    ]

    def __init__(self, api):
        self._api = api

    def _ix_get(self, member):
        self._api.call_rc('session get')

    def _ix_set(self, member):
        self._api.call_rc('session set')

    def login(self, username):
        self._api.call_rc('session login %s', username)

    def logout(self):
        self._api.call_rc('session logout')


class Ixia(object):
    """This class supports only one chassis atm."""
    def __init__(self, host):
        self.host = host
        self._tcl = TclClient(host)
        self._api = IxTclHalApi(self._tcl)
        self.chassis = Chassis(self._api, host)
        self.session = Session(self._api)

    def connect(self):
        self._tcl.connect()
        self.chassis.connect()

    def disconnect(self):
        self.chassis.disconnect()
        self._tcl.close()

    def new_port_group(self, id=None):
        return PortGroup(self._api, id)

    def discover(self):
        return self.chassis.discover()
