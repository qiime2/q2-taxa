# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd
import pandas.util.testing as pdt

from q2_taxa import collapse


class CollapseTests(unittest.TestCase):

    def assert_index_equal(self, a, b):
        # this method is derived from scikit-bio 0.5.1
        pdt.assert_index_equal(a, b,
                               exact=True,
                               check_names=True,
                               check_exact=True)

    def assert_data_frame_almost_equal(self, left, right):
        # this method is derived from scikit-bio 0.5.1
        pdt.assert_frame_equal(left, right,
                               check_dtype=True,
                               check_index_type=True,
                               check_column_type=True,
                               check_frame_type=True,
                               check_less_precise=False,
                               check_names=True,
                               by_blocks=False,
                               check_exact=False)
        self.assert_index_equal(left.index, right.index)

    def test_collapse(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = pd.Series(['a; b; c', 'a; b; d'],
                             index=['feat1', 'feat2'])

        actual = collapse(table, taxonomy, 1)
        expected = pd.DataFrame([[4.0], [2.0], [17.0], [4.0]],
                                index=['A', 'B', 'C', 'D'],
                                columns=['a'])
        self.assert_data_frame_almost_equal(actual, expected)

        actual = collapse(table, taxonomy, 2)
        expected = pd.DataFrame([[4.0], [2.0], [17.0], [4.0]],
                                index=['A', 'B', 'C', 'D'],
                                columns=['a;b'])
        self.assert_data_frame_almost_equal(actual, expected)

        actual = collapse(table, taxonomy, 3)
        expected = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0],
                                 [0.0, 4.0]],
                                index=['A', 'B', 'C', 'D'],
                                columns=['a;b;c', 'a;b;d'])
        self.assert_data_frame_almost_equal(actual, expected)

    def test_collapse_missing_level(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = pd.Series(['a; b', 'a; b; d'],
                             index=['feat1', 'feat2'])

        actual = collapse(table, taxonomy, 1)
        expected = pd.DataFrame([[4.0], [2.0], [17.0], [4.0]],
                                index=['A', 'B', 'C', 'D'],
                                columns=['a'])
        self.assert_data_frame_almost_equal(actual, expected)

        actual = collapse(table, taxonomy, 2)
        expected = pd.DataFrame([[4.0], [2.0], [17.0], [4.0]],
                                index=['A', 'B', 'C', 'D'],
                                columns=['a;b'])
        self.assert_data_frame_almost_equal(actual, expected)

        actual = collapse(table, taxonomy, 3)
        expected = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0],
                                 [0.0, 4.0]],
                                index=['A', 'B', 'C', 'D'],
                                columns=['a;b;__', 'a;b;d'])
        self.assert_data_frame_almost_equal(actual, expected)

    def test_collapse_bad_level(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = pd.Series(['a; b; c', 'a; b; d'],
                             index=['feat1', 'feat2'])
        with self.assertRaisesRegex(ValueError, 'of 42 is larger'):
            collapse(table, taxonomy, 42)

        with self.assertRaisesRegex(ValueError, 'of 0 is too low'):
            collapse(table, taxonomy, 0)
