# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import biom
import numpy as np
import pandas as pd
import pandas.testing as pdt

from q2_taxa import collapse, ids_to_taxonomy


class TestIdsToTaxonomy(unittest.TestCase):
    def _make_table(self, feature_ids: list[str]):
        data = np.arange(1, len(feature_ids) + 1).reshape(len(feature_ids), 1)
        return biom.Table(data, feature_ids, ['sample-1'])

    def test_strict(self):
        '''
        Ensure that with strict=True a non-default delimiter parsing works
        as expected.
        '''
        feature_ids = ['k|p|c', 'k2|p2|c2']
        table = self._make_table(feature_ids)

        obs = ids_to_taxonomy(table, delimiter='|', strict=True)
        exp = pd.DataFrame(
            {'Taxon': ['k;p;c', 'k2;p2;c2']},
            index=pd.Index(feature_ids, name='Feature ID')
        )
        pdt.assert_frame_equal(obs, exp)

    def test_strict_semicolon_present_errors(self):
        '''
        Ensure that with strict=True an error is raised when a semicolon
        is present in a feature ID.
        '''
        table = self._make_table(['k|p;g|c', 'k|p|c'])

        with self.assertRaisesRegex(
            ValueError, 'already contain ";".*1 feature IDs'
        ):
            ids_to_taxonomy(table, delimiter='|')

    def test_strict_some_missing_delimiter_allowed(self):
        '''
        Ensure that with strict=True we allow single-level taxonomy strings
        that do not contain the delimiter, as long as at least one feature
        ID contains the delimiter.
        '''
        feature_ids = ['k|p|c', 'k']
        table = self._make_table(feature_ids)

        obs = ids_to_taxonomy(table, delimiter='|', strict=True)
        exp = pd.DataFrame(
            {'Taxon': ['k;p;c', 'k']},
            index=pd.Index(feature_ids, name='Feature ID')
        )
        pdt.assert_frame_equal(obs, exp)

    def test_strict_all_ids_missing_delimiter_errors(self):
        '''
        Ensure that with strict=True an error is raised when no feature ID
        contains the delimiter.
        '''
        table = self._make_table(['k', 'p'])

        with self.assertRaisesRegex(
            ValueError,
            r'requires at least one feature ID to contain the delimiter \|'
        ):
            ids_to_taxonomy(table, delimiter='|')

    def test_strict_empty_level_errors(self):
        '''
        Ensure that with strict=True an error is raised when a feature ID
        parses in such a way that an empty level is created.
        '''
        table = self._make_table(['k||c', 'k|p|c'])

        with self.assertRaisesRegex(
                ValueError, 'empty taxonomic levels.*1 feature IDs'
        ):
            ids_to_taxonomy(table, delimiter='|')

    def test_non_strict(self):
        '''
        Tests a non-strict parsing with semicolons present, empty levels,
        and missing delimiters by ensuring we:
            - replace the semicolon with the proper replacement
            - collapse away empty levels
            - retain delimiter-missing labels
        '''
        feature_ids = ['k|p;g|c', '|a||b|', 'k2']
        table = self._make_table(feature_ids)

        obs = ids_to_taxonomy(
            table, delimiter='|', strict=False, semicolon_replacement=':'
        )
        exp = pd.DataFrame(
            {'Taxon': ['k;p:g;c', 'a;b', 'k2']},
            index=pd.Index(feature_ids, name='Feature ID')
        )

        pdt.assert_frame_equal(obs, exp)

    def test_non_strict_id_with_only_delimiters_errors(self):
        '''
        Ensures that in non-strict mode we error when a feature ID containing
        only delimiters parses into an empty taxonomic string.
        '''
        table = self._make_table(['||', 'k|p|c'])

        with self.assertRaisesRegex(
            ValueError,
            'Unable to construct non-empty taxonomy strings.*1 feature IDs'
        ):
            ids_to_taxonomy(table, delimiter='|', strict=False)

    def test_non_strict_empty_id_errors(self):
        '''
        Ensures that in non-strict mode we error when an empty feature ID
        only parses into an empty taxonomic string.

        (Note: we need coverage of this because biom.Table does not disallow
        empty strings as feature IDs, only uniqueness among IDs.)
        '''
        table = self._make_table(['', 'k|p|c'])

        with self.assertRaisesRegex(
                ValueError,
                'Unable to construct non-empty taxonomy strings.*1 feature IDs'
        ):
            ids_to_taxonomy(table, delimiter='|', strict=False)

    def test_ids_to_taxonomy_allows_collapse(self):
        '''
        Proves that we can use `ids_to_taxonomy` on a feature table where
        we only have the taxonomy encoded in the feature ID labels to get a
        taxonomy, and then use that taxonomy to collapse, which would not be
        possible otherwise.
        '''
        table = biom.Table(
            np.array([[1.0, 2.0], [3.0, 4.0]]),
            ['k|p|c', 'k|p|g'],
            ['s1', 's2']
        )

        taxonomy = ids_to_taxonomy(table, delimiter='|')
        obs = collapse(table, taxonomy['Taxon'], level=2)
        obs.del_metadata()

        exp = biom.Table(np.array([[4.0, 6.0]]), ['k;p'], ['s1', 's2'])
        self.assertEqual(obs, exp)
