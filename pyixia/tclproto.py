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

#
# Protocol parser for IXIA's underlying TclServer
#

import socket
import logging
import paramiko
import os.path

log = logging.getLogger(__name__)

class TclError(Exception):
    def __init__(self, result):
        self.result = result
    def __repr__(self):
        return '%s(result="%s")' % (self.__class__.__name__, self.result)
    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.result)

class TclClient:
    def _tcl_hal_version(self):
        rsp = self.call('version cget -ixTclHALVersion')
        return rsp[0].split('.')

    def hal_version(self):
        """Returns a tuple (major,minor) of the TCL HAL version."""
        return tuple(self._tcl_hal_version()[0:2])

class TclSocketClient(TclClient):
    def __init__(self, host, port=4555):
        self.host = host
        self.port = port
        self.fd = None
        self.buffersize = 10240

    def call(self, string, *args):
        if self.fd is None:
            raise RuntimeError('TclClient is not connected')

        string += '\r\n'
        data = string % args
        log.debug('sending %s (%s)', data.rstrip(), data.encode('utf-8').hex())
        self.fd.send(data)

        # reply format is
        #  [<io output>\r]<result><tcl return code>\r\n
        # where tcl_return code is exactly one byte
        data = self.fd.recv(self.buffersize)
        log.debug('received %s (%s)', data.rstrip(), data.hex())
        assert data[-2:] == b'\r\n'

        tcl_result = int(data[-3])

        data = data[:-3].rsplit('\r', 1)
        if len(data) == 2:
            io_output, result = data
        else:
            result = data[0]
            io_output = None

        if tcl_result == 1:
            assert io_output == None
            raise TclError(result)

        log.debug('result=%s io_output=%s', result, io_output)
        return result, io_output

    def connect(self):
        log.debug('Opening connection to %s:%d', self.host, self.port)
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.connect((self.host, self.port))
        self.fd = fd
        self.call('package req IxTclHal')

    def close(self):
        log.debug('Closing connection')
        self.fd.close()
        self.fd = None

class TclSSHClient(TclClient):
    def __init__(self, host, username="ixtcl", key_filename=None, port=22):
        self.host = host
        self.port = port
        self.username = username
        self.key_filename = key_filename
        if not self.key_filename:
            self.key_filename = os.path.join(os.path.expanduser('~'), ".ssh", "id_ixia")
        self.fd = None
        self.buffersize = 10240

    def call(self, string, *args):
        if self.fd is None:
            raise RuntimeError('TclClient is not connected')

        data = string % args
        log.debug('sending %s (%s)', data.rstrip(), data.encode('utf-8').hex())

        # We've spawned a non-interactive tclsh on the peer and we can control
        # the output format ourselves. But keep it simple and use a similar
        # format to the old socket protocol.
        #  [<io output>]\r<result><tcl return code>\a
        # where tcl_return code is exactly one byte
        data = 'set ret [catch {%s} result];puts -nonewline stdout "\\r${result}${ret}\\a";flush stdout\r\n' % data
        log.debug('sending %s (%s)', data.rstrip(), data.encode('utf-8').hex())
        self.fd.send(data)

        data = b''
        while not data.endswith(b'\a'):
            data += self.fd.recv(self.buffersize)
        log.debug('received %s (%s)', data.rstrip(), data.hex())

        tcl_result = int(data[-2:-1])
        io_output, result = data[:-2].rsplit(b'\r', 1)

        if len(io_output) == 0:
            io_output = None

        if tcl_result == 1:
            assert io_output == None
            raise TclError(result)

        log.debug('result=%s io_output=%s', result, io_output)
        return result, io_output

    def connect(self):
        log.debug('Opening SSH connection to %s', self.host)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, username=self.username,
                key_filename=self.key_filename)
        transport = ssh.get_transport()
        chan = transport.open_session()
        chan.exec_command("/bin/tclsh")
        self.fd = chan

        self.fd.send('fconfigure stdout -buffering full\n')
        self.call('source /opt/ixia/ixos/current/IxiaWish.tcl')
        self.call('package req IxTclHal')
        self.call('logOff')

    def close(self):
        log.debug('Closing SSH connection')
        self.fd.close()
        self.fd = None
