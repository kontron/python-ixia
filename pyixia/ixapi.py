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


"""
IxTclHalApi - API of the Ixia TCL HAL server
--------------------------------------------

There are several layers of indirections:

- The hardware itself.
- The IxHal API which controls the hardware, there seems to be a ixhal.dll
  which is used on windows to access this API directly.
- The IxTclHal API which is provided by a TclServer, which in turn uses the
  IxHal API.
- The TCL script which uses the IxTclHal API.

The TclServer provides an ASCII interface (port 4555) where you can use the TCL
commands. See :mod:`pyixia.tclproto` for more information on the protocol. This
server also serves as a temporary storage for the properties you set. There are
different commands to set properties and transfer them between the layers.

The `config` and `cget` commands are used to store and retrieve values from the
temporary storage within the TclServer. The `set` and `get` commands are used
to transfer this values between the TclServer and the IxHal layer. `set` writes
data from the TclServer to the IxHal layer and `get` fetches data from the
IxHal to the temporary storage of the TclServer. And last, `write` actually
commits the data from IxHal to the hardware. `refresh` moves the data from the
hardware to IxHal.

For example, if you like to set the port speed:

- port config -speed 10
- port set <chassis ID> <card ID> <port ID>
- port write <chassis ID> <card ID> <port ID>

Note that there is only one temporary storage for each command.

"""

FLAG_RDONLY = 1

def two_chars(s):
    for i in range(len(s)-1):
        yield (s[i], s[i+1])

def translate_ix_member_name(name):
    if len(name) == 1:
        return name.lower()
    else:
        _new_name = list()
        seperator = ''
        for cc in two_chars(name):
            if cc[0].isupper(): # CC, Cc
                if cc[1].islower(): # Cc
                    seperator = '_'
                _new_name.extend((seperator, cc[0].lower()))
                seperator = ''
            else: # cc, cC
                _new_name.append(cc[0].lower())
                if cc[1].isupper(): # cC
                    seperator = '_'
        _new_name.extend((seperator, cc[1].lower())) # append last character
        if _new_name[0] == '_': # delete leading underscore
            del _new_name[0]
    return ''.join(_new_name)


class TclMember(object):
    def __init__(self, name, type=str, attrname=None, flags=0, doc=None):
        self.name = name
        self.type = type
        self.attrname = attrname
        self.flags = flags
        self.doc = doc


class IxTclHalError(Exception):
    def __init__(self, rc):
        self.rc = rc
    def __repr__(self):
        return '%s(rc="%s")' % (self.__class__.__name__, self.rc)
    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.rc)


class IxTclHalApi(object):
    def __init__(self, tcl_handler):
        self._tcl_handler = tcl_handler

    def call(self, cmd, *args):
        return self._tcl_handler.call(cmd, *args)

    def call_rc(self, cmd, *args):
        rc = self.call(cmd, *args)[0]
        if int(rc) != 0:
            raise IxTclHalError(rc)


class _MetaIxTclApi(type):
    """Dynamically creates properties, which wraps the IxTclHAL API.

    The `__tcl_members__` attribute is a list of tuples of one of the following
    forms: TBD

    If no attribute name is given, it is derived from the tclMemberName by
    replacing every uppercase letter with the lowercase variant prepended with
    a '_', eg. 'portMode' will be translated to 'port_mode'.

    The generated methods assume that the class provides a method called '_ix_get'
    which fetches the properties and stores them into the IxTclHal object. Eg.
    for the 'port' command this would be 'port get <ch> <card> <port>'.
    """
    def __new__(cls, clsname, clsbases, clsdict):
        members = clsdict.get('__tcl_members__', list())
        command = clsdict.get('__tcl_command__', None)
        for (n,m) in enumerate(members):
            if not isinstance(m, TclMember):
                raise RuntimeError('Element #%d of __tcl_members__ is not a '
                        'TclMember' % (n+1,))
            def fget(self, cmd=command, m=m):
                self._ix_get(m)
                val = self._api.call('%s cget -%s' % (cmd,m.name))[0]
                return m.type(val)

            def fset(self, value, cmd=command, m=m):
                val = self._api.call('%s config -%s %s' % (cmd,m.name,value))
                self._ix_set(m)

            attrname = m.attrname
            if m.attrname is None:
                attrname = translate_ix_member_name(m.name)

            if m.doc is not None:
                fget.__doc__ = m.doc

            fget.__name__ = '_get_%s' % attrname
            clsdict[fget.__name__] = fget
            if not m.flags & FLAG_RDONLY:
                fset.__name__ = '_set_%s' % attrname
                clsdict[fset.__name__] = fset
                p = property(fget=fget, fset=fset)
            else:
                p = property(fget=fget)

            clsdict[attrname] = p
        t = type.__new__(cls, clsname, clsbases, clsdict)
        return t


