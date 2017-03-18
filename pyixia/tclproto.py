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

import sys
import socket
import logging
import paramiko

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)


class TclError(Exception):

    def __init__(self, result):
        self.result = result

    def __repr__(self):
        return '%s(result="%s")' % (self.__class__.__name__, self.result)

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.result)


class TclClient:

    def __init__(self, host, port=4555, rsa_id=None):
        self.host = host
        self.port = port
        self.rsa_id = rsa_id
        self.fd = None
        self.buffersize = 10240

    def socket_call(self, string, *args):
        if self.fd is None:
            raise RuntimeError('TclClient is not connected')

        string += '\r\n'
        data = string % args
        log.debug('sending %s (%s)', data.rstrip(), data.encode('hex'))
        self.fd.send(data)

        # reply format is
        #  [<io output>\r]<result><tcl return code>\r\n
        # where tcl_return code is exactly one byte
        data = self.fd.recv(self.buffersize)
        log.debug('received %s (%s)', data.rstrip(), data.encode('hex'))
        # print 'data=(%s) (%s)' % (data, data.encode('hex'))
        assert data[-2:] == '\r\n'

        tcl_result = int(data[-3])

        data = data[:-3].rsplit('\r', 1)
        if len(data) == 2:
            io_output, result = data
        else:
            result = data[0]
            io_output = None

        if tcl_result == 1:
            assert not io_output
            raise TclError(result)

        log.debug('result=%s io_output=%s', result, io_output)
        return result, io_output

    def ssh_call(self, string, *args):
        data = 'puts [{}]\n\r'.format(string % args)
        log.debug('sending %s (%s)', data.rstrip(), data.encode('hex'))
        self.stdin.write(data)
        self.stdin.flush()
        l = len(self.stdout.channel.in_buffer)
        while not l:
            l = len(self.stdout.channel.in_buffer)
        data = self.stdout.read(l)
        log.debug('received %s (%s)', data.rstrip(), data.encode('hex'))
        return data

    def call(self, string, *args):
        if self.windows_server:
            return self.socket_call(string, *args)
        else:
            return self.ssh_call(string, *args)

    def _tcl_hal_version(self):
        rsp = self.call('version cget -ixTclHALVersion')
        return rsp[0].split('.')

    def connect(self):
        log.debug('Opening connection to %s:%d', self.host, self.port)

        if self.port == 8022:
            self.windows_server = False
            key = paramiko.RSAKey.from_private_key_file(self.rsa_id)
            self.fd = paramiko.SSHClient()
            self.fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.fd.connect(hostname=self.host, port=self.port, username='ixtcl', pkey=key)
            self.stdin, self.stdout, _ = self.fd.exec_command('')
            self.call('source /opt/ixia/ixos/current/IxiaWish.tcl')
        else:
            self.windows_server = True
            fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            fd.connect((self.host, self.port))
            self.fd = fd

        self.call('package req IxTclHal')

    def close(self):
        log.debug('Closing connection')
        self.fd.close()
        self.fd = None

    def hal_version(self):
        """Returns a tuple (major,minor) of the TCL HAL version."""
        return tuple(self._tcl_hal_version()[0:2])
