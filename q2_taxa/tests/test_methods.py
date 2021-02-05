# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd
import pandas.util.testing as pdt
import qiime2

from q2_taxa import collapse, filter_table, filter_seqs


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

    def test_collapse_missing_table_ids_in_taxonomy(self):
        table = pd.DataFrame([[2.0, 2.0],
                              [1.0, 1.0],
                              [9.0, 8.0],
                              [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = pd.Series(['a; b; c', 'a; b; d'],
                             index=['feat1', 'feat3'])
        with self.assertRaisesRegex(ValueError, 'missing.*feat2'):
            collapse(table, taxonomy, 1)


class FilterTable(unittest.TestCase):

    def test_filter_no_filters(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        with self.assertRaisesRegex(ValueError, 'At least one'):
            filter_table(table, taxonomy)

    def test_alt_delimiter(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # include with delimiter
        obs = filter_table(table, taxonomy, include='cc@peanut@ee',
                           query_delimiter='@peanut@')
        pdt.assert_frame_equal(obs, table, check_like=True)

        # exclude with delimiter
        obs = filter_table(table, taxonomy, exclude='ww@peanut@ee',
                           query_delimiter='@peanut@')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

    def test_filter_table_unknown_mode(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        with self.assertRaisesRegex(ValueError, 'Unknown mode'):
            filter_table(table, taxonomy, include='bb', mode='not-a-mode')

    def test_filter_table_include(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_table(table, taxonomy, include='bb')
        pdt.assert_frame_equal(obs, table, check_like=True)

        obs = filter_table(table, taxonomy, include='cc,ee')
        pdt.assert_frame_equal(obs, table, check_like=True)

        # keep feat1 only
        obs = filter_table(table, taxonomy, include='cc')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, include='aa; bb; cc')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep feat2 only
        obs = filter_table(table, taxonomy, include='dd')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, include='ee')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, include='dd ee')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, include='aa; bb; dd ee')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep no features
        with self.assertRaisesRegex(ValueError, expected_regex='empty table'):
            obs = filter_table(table, taxonomy, include='peanut!')

    def test_filter_table_include_exact_match(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_table(table, taxonomy, include='aa; bb; cc,aa; bb; dd ee',
                           mode='exact')
        pdt.assert_frame_equal(obs, table, check_like=True)

        # keep feat1 only
        obs = filter_table(table, taxonomy, include='aa; bb; cc',
                           mode='exact')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep feat2 only
        obs = filter_table(table, taxonomy, include='aa; bb; dd ee',
                           mode='exact')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep no features
        with self.assertRaisesRegex(ValueError, expected_regex='empty table'):
            obs = filter_table(table, taxonomy, include='bb', mode='exact')

    def test_filter_table_exclude(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_table(table, taxonomy, exclude='ab')
        pdt.assert_frame_equal(obs, table, check_like=True)

        obs = filter_table(table, taxonomy, exclude='xx')
        pdt.assert_frame_equal(obs, table, check_like=True)

        # keep feat1 only
        obs = filter_table(table, taxonomy, exclude='dd')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, exclude='dd ee')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, exclude='aa; bb; dd ee')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep feat2 only
        obs = filter_table(table, taxonomy, exclude='cc')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, exclude='aa; bb; cc')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep no features
        with self.assertRaisesRegex(ValueError, expected_regex='empty table'):
            obs = filter_table(table, taxonomy, exclude='aa')

        with self.assertRaisesRegex(ValueError, expected_regex='empty table'):
            obs = filter_table(table, taxonomy, exclude='aa; bb')

    def test_filter_table_exclude_exact_match(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_table(table, taxonomy, exclude='peanut!',
                           mode='exact')
        pdt.assert_frame_equal(obs, table, check_like=True)

        # keep feat1 only
        obs = filter_table(table, taxonomy, exclude='aa; bb; dd ee',
                           mode='exact')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, exclude='aa; bb; dd ee,aa',
                           mode='exact')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep feat2 only
        obs = filter_table(table, taxonomy, exclude='aa; bb; cc',
                           mode='exact')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        obs = filter_table(table, taxonomy, exclude='aa; bb; cc,aa',
                           mode='exact')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep no features
        with self.assertRaisesRegex(ValueError, expected_regex='empty table'):
            obs = filter_table(table, taxonomy,
                               exclude='aa; bb; cc,aa; bb; dd ee',
                               mode='exact')

    def test_filter_table_include_exclude(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_table(table, taxonomy, include='aa', exclude='peanut!')
        pdt.assert_frame_equal(obs, table, check_like=True)

        # keep feat1 only - feat2 dropped at exclusion step
        obs = filter_table(table, taxonomy, include='aa', exclude='ee')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep feat1 only - feat2 dropped at inclusion step
        obs = filter_table(table, taxonomy, include='cc', exclude='ee')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep feat2 only - feat1 dropped at exclusion step
        obs = filter_table(table, taxonomy, include='aa', exclude='cc')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep feat2 only - feat1 dropped at inclusion step
        obs = filter_table(table, taxonomy, include='ee', exclude='cc')
        exp = pd.DataFrame([[2.0], [1.0], [8.0], [4.0]],
                           index=['A', 'B', 'C', 'D'],
                           columns=['feat2'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep no features - all dropped at exclusion
        with self.assertRaisesRegex(ValueError, expected_regex='empty table'):
            obs = filter_table(table, taxonomy,
                               include='aa',
                               exclude='bb',
                               mode='exact')

        # keep no features - one dropped at inclusion, one dropped at exclusion
        with self.assertRaisesRegex(ValueError, expected_regex='empty table'):
            obs = filter_table(table, taxonomy,
                               include='cc',
                               exclude='cc',
                               mode='exact')

        # keep no features - all dropped at inclusion
        with self.assertRaisesRegex(ValueError, expected_regex='empty table'):
            obs = filter_table(table, taxonomy,
                               include='peanut',
                               exclude='bb',
                               mode='exact')

    def test_filter_table_underscores_escaped(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep feat1 only - underscore not treated as a wild card
        obs = filter_table(table, taxonomy, include='cc,d_')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

        # keep feat1 only - underscore in query matches underscore in
        # taxonomy annotation
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; c_', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))
        obs = filter_table(table, taxonomy, include='c_')
        exp = pd.DataFrame([[2.0], [1.0], [9.0]],
                           index=['A', 'B', 'C'],
                           columns=['feat1'])
        pdt.assert_frame_equal(obs, exp, check_like=True)

    def test_all_features_with_frequency_greater_than_zero_get_filtered(self):
        table = pd.DataFrame([[2.0, 0.0], [1.0, 0.0], [9.0, 0.0], [1.0, 0.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # empty - feat2, which is matched by the include term, has a frequency
        # of zero in all samples, so all samples end up dropped from the table
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='greater than zero'):
            filter_table(table, taxonomy, include='dd')

    def test_extra_taxon_ignored(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee', 'aa; bb; cc'],
                             index=pd.Index(['feat1', 'feat2', 'feat3'],
                                            name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_table(table, taxonomy, include='bb')
        pdt.assert_frame_equal(obs, table, check_like=True)

    def test_missing_taxon_errors(self):
        table = pd.DataFrame([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]],
                             index=['A', 'B', 'C', 'D'],
                             columns=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc'],
                             index=pd.Index(['feat1'], name='id'),
                             columns=['Taxon']))

        with self.assertRaisesRegex(ValueError, expected_regex='All.*feat2'):
            filter_table(table, taxonomy, include='bb')


class FilterSeqs(unittest.TestCase):

    def test_filter_no_filters(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        with self.assertRaisesRegex(ValueError, 'At least one'):
            filter_seqs(seqs, taxonomy)

    def test_alt_delimiter(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # include with delimiter
        obs = filter_seqs(seqs, taxonomy, include='cc@peanut@ee',
                          query_delimiter='@peanut@')
        exp = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # exclude with delimiter
        obs = filter_seqs(seqs, taxonomy, exclude='ww@peanut@ee',
                          query_delimiter='@peanut@')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

    def test_filter_seqs_unknown_mode(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        with self.assertRaisesRegex(ValueError, 'Unknown mode'):
            filter_seqs(seqs, taxonomy, include='bb', mode='not-a-mode')

    def test_filter_seqs_include(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_seqs(seqs, taxonomy, include='bb')
        exp = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, include='cc,ee')
        exp = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat1 only
        obs = filter_seqs(seqs, taxonomy, include='cc')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, include='aa; bb; cc')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat2 only
        obs = filter_seqs(seqs, taxonomy, include='dd')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, include='ee')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, include='dd ee')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, include='aa; bb; dd ee')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep no features
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='empty collection'):
            obs = filter_seqs(seqs, taxonomy, include='peanut!')

    def test_filter_seqs_include_exact_match(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_seqs(seqs, taxonomy, include='aa; bb; cc,aa; bb; dd ee',
                          mode='exact')
        exp = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat1 only
        obs = filter_seqs(seqs, taxonomy, include='aa; bb; cc',
                          mode='exact')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat2 only
        obs = filter_seqs(seqs, taxonomy, include='aa; bb; dd ee',
                          mode='exact')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep no features
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='empty collection'):
            obs = filter_seqs(seqs, taxonomy, include='bb', mode='exact')

    def test_filter_seqs_exclude(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_seqs(seqs, taxonomy, exclude='ab')
        exp = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, exclude='xx')
        exp = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat1 only
        obs = filter_seqs(seqs, taxonomy, exclude='dd')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, exclude='dd ee')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, exclude='aa; bb; dd ee')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat2 only
        obs = filter_seqs(seqs, taxonomy, exclude='cc')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, exclude='aa; bb; cc')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep no features
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='empty collection'):
            obs = filter_seqs(seqs, taxonomy, exclude='aa')

        with self.assertRaisesRegex(ValueError,
                                    expected_regex='empty collection'):
            obs = filter_seqs(seqs, taxonomy, exclude='aa; bb')

    def test_filter_seqs_exclude_exact_match(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_seqs(seqs, taxonomy, exclude='peanut!',
                          mode='exact')
        exp = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat1 only
        obs = filter_seqs(seqs, taxonomy, exclude='aa; bb; dd ee',
                          mode='exact')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, exclude='aa; bb; dd ee,aa',
                          mode='exact')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat2 only
        obs = filter_seqs(seqs, taxonomy, exclude='aa; bb; cc',
                          mode='exact')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        obs = filter_seqs(seqs, taxonomy, exclude='aa; bb; cc,aa',
                          mode='exact')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep no features
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='empty collection'):
            obs = filter_seqs(seqs, taxonomy,
                              exclude='aa; bb; cc,aa; bb; dd ee',
                              mode='exact')

    def test_filter_seqs_include_exclude(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_seqs(seqs, taxonomy, include='aa', exclude='peanut!')
        exp = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat1 only - feat2 dropped at exclusion step
        obs = filter_seqs(seqs, taxonomy, include='aa', exclude='ee')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat1 only - feat2 dropped at inclusion step
        obs = filter_seqs(seqs, taxonomy, include='cc', exclude='ee')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat2 only - feat1 dropped at exclusion step
        obs = filter_seqs(seqs, taxonomy, include='aa', exclude='cc')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat2 only - feat1 dropped at inclusion step
        obs = filter_seqs(seqs, taxonomy, include='ee', exclude='cc')
        exp = pd.Series(['ACCC'], index=['feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep no features - all dropped at exclusion
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='empty collection'):
            obs = filter_seqs(seqs, taxonomy,
                              include='aa',
                              exclude='bb',
                              mode='exact')

        # keep no features - one dropped at inclusion, one dropped at exclusion
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='empty collection'):
            obs = filter_seqs(seqs, taxonomy,
                              include='cc',
                              exclude='cc',
                              mode='exact')

        # keep no features - all dropped at inclusion
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='empty collection'):
            obs = filter_seqs(seqs, taxonomy,
                              include='peanut',
                              exclude='bb',
                              mode='exact')

    def test_filter_seqs_underscores_escaped(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))

        # keep feat1 only - underscore not treated as a wild card
        obs = filter_seqs(seqs, taxonomy, include='cc,d_')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

        # keep feat1 only - underscore in query matches underscore in
        # taxonomy annotation
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; c_', 'aa; bb; dd ee'],
                             index=pd.Index(['feat1', 'feat2'], name='id'),
                             columns=['Taxon']))
        obs = filter_seqs(seqs, taxonomy, include='c_')
        exp = pd.Series(['ACGT'], index=['feat1'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

    def test_extra_taxon_ignored(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc', 'aa; bb; dd ee', 'aa; bb; cc'],
                             index=pd.Index(['feat1', 'feat2', 'feat3'],
                                            name='id'),
                             columns=['Taxon']))

        # keep both features
        obs = filter_seqs(seqs, taxonomy, include='bb')
        exp = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        obs.sort_values(inplace=True)
        exp.sort_values(inplace=True)
        pdt.assert_series_equal(obs, exp)

    def test_missing_taxon_errors(self):
        seqs = pd.Series(['ACGT', 'ACCC'], index=['feat1', 'feat2'])
        taxonomy = qiime2.Metadata(
                pd.DataFrame(['aa; bb; cc'],
                             index=pd.Index(['feat1'], name='id'),
                             columns=['Taxon']))

        with self.assertRaisesRegex(ValueError, expected_regex='All.*feat2'):
            filter_seqs(seqs, taxonomy, include='bb')
