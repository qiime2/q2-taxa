# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd
from q2_taxa._util import _get_padding_ranks


class PaddingTests(unittest.TestCase):

    def test_padding(self):
        # ideal case, no conflict at all ranks
        # -> ranks inferred
        taxonomy = pd.Series([
            'k__a; p__b; o__c',
            'k__a; p__b; o__c',
            'k__a'
        ], index=['feat1', 'feat2', 'feat3'])
        observed = _get_padding_ranks(taxonomy)
        expected = ['k__', 'p__', 'o__']
        self.assertEqual(observed, expected)

        # no conflict at all ranks and the rank
        # inferred only from before the first "_" 
        taxonomy = pd.Series([
            'k__a__1__x; p__b; o__c',
            'k__a; p__b; o__c',
            'k__a'
        ], index=['feat1', 'feat2', 'feat3'])
        observed = _get_padding_ranks(taxonomy)
        expected = ['k__', 'p__', 'o__']
        self.assertEqual(observed, expected)

        # conflict at rank 2 (p1 and p2)
        # -> no rank inferred
        taxonomy = pd.Series([
            'k__a; p1__b; o__c',
            'k__a; p2__b; o__c',
            'k__a'
        ], index=['feat1', 'feat2', 'feat3'])
        observed = _get_padding_ranks(taxonomy)
        expected = None
        self.assertEqual(observed, expected)

        # current situation, before PR, no rank
        # to start with -> no rank inferred
        taxonomy = pd.Series([
            'a; b; c',
            'a',
        ], index=['feat1', 'feat2'])
        observed = _get_padding_ranks(taxonomy)
        expected = None
        self.assertEqual(observed, expected)
