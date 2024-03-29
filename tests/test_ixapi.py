# SPDX-License-Identifier: LGPL-2.0-or-later
#
# Copyright (c) 2015 Kontron Europe GmbH
#

from pyixia.ixapi import translate_ix_member_name
from nose.tools import eq_


def test_translate_ix_member_name():
    eq_(translate_ix_member_name('A'), 'a')
    eq_(translate_ix_member_name('AA'), 'aa')
    eq_(translate_ix_member_name('Ab'), 'ab')
    eq_(translate_ix_member_name('bA'), 'b_a')
    eq_(translate_ix_member_name('AAA'), 'aaa')
    eq_(translate_ix_member_name('bAA'), 'b_aa')
    eq_(translate_ix_member_name('Abb'), 'abb')
    eq_(translate_ix_member_name('bbA'), 'bb_a')
    eq_(translate_ix_member_name('AAb'), 'a_ab')
    eq_(translate_ix_member_name('AbA'), 'ab_a')
    eq_(translate_ix_member_name('bAb'), 'b_ab')
    eq_(translate_ix_member_name('AAAA'), 'aaaa')
    eq_(translate_ix_member_name('Abbb'), 'abbb')
    eq_(translate_ix_member_name('bAAA'), 'b_aaa')
    eq_(translate_ix_member_name('AAbb'), 'a_abb')
    eq_(translate_ix_member_name('bbAA'), 'bb_aa')
    eq_(translate_ix_member_name('AAAb'), 'aa_ab')
    eq_(translate_ix_member_name('bbbA'), 'bbb_a')
    eq_(translate_ix_member_name('AbAb'), 'ab_ab')
    eq_(translate_ix_member_name('bAbA'), 'b_ab_a')
    eq_(translate_ix_member_name('AbAA'), 'ab_aa')
    eq_(translate_ix_member_name('AAbA'), 'a_ab_a')
    eq_(translate_ix_member_name('bbAb'), 'bb_ab')
    eq_(translate_ix_member_name('bAbb'), 'b_abb')
    eq_(translate_ix_member_name('AbbA'), 'abb_a')
    eq_(translate_ix_member_name('bAAb'), 'b_a_ab')
    eq_(translate_ix_member_name('framerFCSErrors'), 'framer_fcs_errors')
    eq_(translate_ix_member_name('ID'), 'id')
