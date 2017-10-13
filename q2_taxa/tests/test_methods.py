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
import qiime2

from q2_taxa import collapse, filter_table


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

class FilterTable(unittest.TestCase):

    def test_filter_table_include_contains(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
            pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
            index=['feat1', 'feat2'], columns=['Taxon']))

        # keep both features
        obs = filter_table(table, taxonomy, include_contains='bb')
        pdt.assert_frame_equal(obs, table, check_like=True)

        # keep feat1 only
        obs = filter_table(table, taxonomy, include_contains='cc')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, include_contains='aa; bb; cc')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep feat2 only
        obs = filter_table(table, taxonomy, include_contains='dd')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, include_contains='ee')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, include_contains='dd ee')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, include_contains='aa; bb; dd ee')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep no features
        with self.assertRaisesRegex(ValueError, expected_regex='empty table'):
            obs = filter_table(table, taxonomy, include_contains='peanut!')
