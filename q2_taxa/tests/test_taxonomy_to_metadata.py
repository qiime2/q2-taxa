# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd
import pandas.testing as pdt

import qiime2
from qiime2 import Artifact

from q2_taxa.plugin_setup import plugin


class TestTaxonomyToMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.taxonomy_to_metadata = plugin.methods['taxonomy_to_metadata']

    def _make_taxonomy(self, mapping):
        df = pd.DataFrame(
            {'Taxon': list(mapping.values())},
            index=pd.Index(list(mapping.keys()), name='Feature ID'),
        )
        return Artifact.import_data('FeatureData[Taxonomy]', df)

    def _to_dataframe(self, artifact):
        return artifact.view(qiime2.Metadata).to_dataframe()

    def test_cumulative_no_prefixes(self):
        '''
        With no rank prefixes, columns are named "Level N" and each column
        contains the cumulative taxonomy.
        '''
        taxonomy = self._make_taxonomy({'id1': 'A;B;C;D'})
        result, = self.taxonomy_to_metadata(taxonomy)
        obs = self._to_dataframe(result)

        exp = pd.DataFrame(
            {
                'Level 1': ['A'],
                'Level 2': ['A;B'],
                'Level 3': ['A;B;C'],
                'Level 4': ['A;B;C;D'],
            },
            index=pd.Index(['id1'], name='Feature ID', dtype=object),
        )
        pdt.assert_frame_equal(obs, exp)

    def test_non_cumulative_no_prefixes(self):
        '''
        With cumulative=False, each column contains only the label at that
        level.
        '''
        taxonomy = self._make_taxonomy({'id1': 'A;B;C;D'})
        result, = self.taxonomy_to_metadata(taxonomy, cumulative=False)
        obs = self._to_dataframe(result)

        exp = pd.DataFrame(
            {
                'Level 1': ['A'],
                'Level 2': ['B'],
                'Level 3': ['C'],
                'Level 4': ['D'],
            },
            index=pd.Index(['id1'], name='Feature ID', dtype=object),
        )
        pdt.assert_frame_equal(obs, exp)

    def test_cumulative_with_prefixes(self):
        '''
        Rank prefixes ("x__") are stripped from values and become column
        headers when consistent across a level.
        '''
        taxonomy = self._make_taxonomy({
            'id1': 'd__Bacteria;p__Firmicutes;c__Bacilli',
            'id2': 'd__Archaea;p__Euryarchaeota;c__Methanobacteria',
        })
        result, = self.taxonomy_to_metadata(taxonomy)
        obs = self._to_dataframe(result)

        exp = pd.DataFrame(
            {
                'd': ['Bacteria', 'Archaea'],
                'p': ['Bacteria;Firmicutes', 'Archaea;Euryarchaeota'],
                'c': [
                    'Bacteria;Firmicutes;Bacilli',
                    'Archaea;Euryarchaeota;Methanobacteria',
                ],
            },
            index=pd.Index(['id1', 'id2'], name='Feature ID', dtype=object),
        )
        pdt.assert_frame_equal(obs, exp)

    def test_non_cumulative_with_prefixes(self):
        taxonomy = self._make_taxonomy({
            'id1': 'd__Bacteria;p__Firmicutes;c__Bacilli',
            'id2': 'd__Archaea;p__Euryarchaeota;c__Methanobacteria',
        })
        result, = self.taxonomy_to_metadata(taxonomy, cumulative=False)
        obs = self._to_dataframe(result)

        exp = pd.DataFrame(
            {
                'd': ['Bacteria', 'Archaea'],
                'p': ['Firmicutes', 'Euryarchaeota'],
                'c': ['Bacilli', 'Methanobacteria'],
            },
            index=pd.Index(['id1', 'id2'], name='Feature ID', dtype=object),
        )
        pdt.assert_frame_equal(obs, exp)

    def test_uneven_levels_pad_with_empty_strings(self):
        '''
        Rows with fewer levels than `max_levels` are padded with empty
        strings; cumulative columns reflect the actual depth of each row.
        '''
        taxonomy = self._make_taxonomy({
            'id1': 'A;B;C',
            'id2': 'A;B',
        })
        result, = self.taxonomy_to_metadata(taxonomy)
        obs = self._to_dataframe(result)

        exp = pd.DataFrame(
            {
                'Level 1': ['A', 'A'],
                'Level 2': ['A;B', 'A;B'],
                'Level 3': ['A;B;C', 'A;B;'],
            },
            index=pd.Index(['id1', 'id2'], name='Feature ID', dtype=object),
        )
        pdt.assert_frame_equal(obs, exp)

    def test_whitespace_around_levels_is_stripped(self):
        '''
        Leading/trailing whitespace around each level is stripped.
        '''
        taxonomy = self._make_taxonomy({
            'id1': 'd__Bacteria; p__Firmicutes; c__Bacilli',
        })
        result, = self.taxonomy_to_metadata(taxonomy, cumulative=False)
        obs = self._to_dataframe(result)

        exp = pd.DataFrame(
            {
                'd': ['Bacteria'],
                'p': ['Firmicutes'],
                'c': ['Bacilli'],
            },
            index=pd.Index(['id1'], name='Feature ID', dtype=object),
        )
        pdt.assert_frame_equal(obs, exp)

    def test_custom_delimiter(self):
        '''
        A non-default delimiter is used both for splitting input and for
        joining cumulative columns.
        '''
        taxonomy = self._make_taxonomy({'id1': 'A|B|C'})
        result, = self.taxonomy_to_metadata(taxonomy, level_delimiter='|')
        obs = self._to_dataframe(result)

        exp = pd.DataFrame(
            {
                'Level 1': ['A'],
                'Level 2': ['A|B'],
                'Level 3': ['A|B|C'],
            },
            index=pd.Index(['id1'], name='Feature ID', dtype=object),
        )
        pdt.assert_frame_equal(obs, exp)

    def test_inconsistent_prefixes_fall_back_to_level_n(self):
        '''
        If the prefix at a column is not consistent across rows that have a
        value there, the column header falls back to "Level N".
        '''
        taxonomy = self._make_taxonomy({
            'id1': 'd__Bacteria;p__Firmicutes',
            'id2': 'd__Archaea;k__Other',
        })
        result, = self.taxonomy_to_metadata(taxonomy, cumulative=False)
        obs = self._to_dataframe(result)

        self.assertEqual(list(obs.columns), ['d', 'Level 2'])
        self.assertEqual(list(obs['d']), ['Bacteria', 'Archaea'])
        self.assertEqual(list(obs['Level 2']), ['Firmicutes', 'Other'])

    def test_empty_delimiter_errors(self):
        taxonomy = self._make_taxonomy({'id1': 'A;B'})

        with self.assertRaisesRegex(
            ValueError, '`level_delimiter` must not be empty'
        ):
            self.taxonomy_to_metadata(taxonomy, level_delimiter='')

    def test_returns_immutable_metadata_artifact(self):
        '''
        The registered output type is ImmutableMetadata.
        '''
        taxonomy = self._make_taxonomy({'id1': 'A;B'})
        result, = self.taxonomy_to_metadata(taxonomy)

        self.assertEqual(str(result.type), 'ImmutableMetadata')


if __name__ == '__main__':
    unittest.main()
