# SPDX-License-Identifier: LGPL-2.0-or-later
#
# Copyright (c) 2022 Kontron Europe GmbH
#

def obj_match_attribute_value(obj, prefix, value):
    for attr in dir(obj):
        if attr.startswith(prefix):
            if value == getattr(obj, attr):
                return attr[len(prefix):]
    return value
