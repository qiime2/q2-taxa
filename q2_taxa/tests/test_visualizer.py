# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import tempfile
from unittest.mock import patch

import biom
import numpy as np
import pandas as pd
import qiime2
from qiime2.sdk import Artifact
from qiime2.plugin.testing import TestPluginBase

from q2_taxa import _barplot, collapse
from q2_taxa._visualizer import _call_relative_frequency


class BarplotTests(TestPluginBase):
    package = 'q2_taxa'

    def setUp(self):
        super().setUp()

        self.barplot = self.plugin.pipelines['barplot']
        self._call_relative_frequency = _call_relative_frequency

        self.table = biom.Table(
            np.array([[2.0, 2.0], [1.0, 1.0], [9.0, 8.0], [0.0, 4.0]]),
            ['A', 'B', 'C', 'D'],
            ['feat1', 'feat2']
        ).transpose()

        self.rel_table = self.table.norm(axis='sample', inplace=False)

        self.taxonomy = pd.Series(
            ['a; b; c', 'a; b; d'], index=['feat1', 'feat2']
        )

        self.metadata = qiime2.Metadata(pd.DataFrame(
            {'val1': ['1.0', '2.0', '3.0', '4.0']},
            index=pd.Index(['A', 'B', 'C', 'D'], name='id')
        ))

    def test_barplot_visualizer(self):
        with tempfile.TemporaryDirectory() as output_dir:
            _barplot(
                output_dir,
                self.table,
                self.rel_table,
                self.taxonomy,
                self.metadata
            )

            index_fp = os.path.join(output_dir, 'index.html')
            self.assertTrue(os.path.exists(index_fp))
            self.assertTrue("src='level-1.jsonp?callback=load_data'" in
                            open(index_fp).read())
            csv_lvl3_fp = os.path.join(output_dir, 'level-3.csv')
            self.assertTrue(os.path.exists(csv_lvl3_fp))
            self.assertTrue('val1' in open(csv_lvl3_fp).read())

    @patch('q2_taxa._visualizer._call_relative_frequency')
    def test_barplot_pipeline_absolute_frequency(
        self, relative_frequency_mock
    ):
        relative_frequency_mock.side_effect = self._call_relative_frequency
        table = Artifact.import_data(
            'FeatureTable[Frequency]', self.table, view_type=biom.Table
        )
        self.barplot(table=table)

        # should be normalized
        relative_frequency_mock.assert_called_once()

    @patch('q2_taxa._visualizer._call_relative_frequency')
    def test_barplot_pipeline_relative_frequency(
        self, relative_frequency_mock
    ):
        relative_frequency_mock.side_effect = self._call_relative_frequency
        table = Artifact.import_data(
            'FeatureTable[RelativeFrequency]',
            self.rel_table,
            view_type=biom.Table
        )
        self.barplot(table=table)

        # should not be redundantly normalized
        relative_frequency_mock.assert_not_called()

    def test_barplot_metadata_extra_id(self):
        metadata = qiime2.Metadata(
            pd.DataFrame({'val1': ['1.0', '2.0', '3.0', '4.0', '5.0']},
                         index=pd.Index(['A', 'B', 'C', 'D', 'E'], name='id')))

        with tempfile.TemporaryDirectory() as output_dir:
            _barplot(
                output_dir,
                self.table,
                self.rel_table,
                self.taxonomy,
                metadata
            )
            index_fp = os.path.join(output_dir, 'index.html')
            self.assertTrue(os.path.exists(index_fp))
            self.assertTrue("src='level-1.jsonp?callback=load_data'" in
                            open(index_fp).read())
            csv_lvl3_fp = os.path.join(output_dir, 'level-3.csv')
            self.assertTrue(os.path.exists(csv_lvl3_fp))

    def test_barplot_metadata_missing_id(self):
        metadata = qiime2.Metadata(
            pd.DataFrame({'val1': ['1.0', '2.0', '3.0']},
                         index=pd.Index(['A', 'B', 'C'], name='id')))

        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(ValueError, 'missing.*D'):
                _barplot(
                    output_dir,
                    self.table,
                    self.rel_table,
                    self.taxonomy,
                    metadata
                )

    def test_barplot_no_metadata(self):
        with tempfile.TemporaryDirectory() as output_dir:
            _barplot(
                output_dir,
                self.table,
                self.rel_table,
                self.taxonomy,
            )
            index_fp = os.path.join(output_dir, 'index.html')
            self.assertTrue(os.path.exists(index_fp))
            self.assertTrue("src='level-1.jsonp?callback=load_data'" in
                            open(index_fp).read())
            csv_lvl3_fp = os.path.join(output_dir, 'level-3.csv')
            self.assertTrue(os.path.exists(csv_lvl3_fp))
            self.assertTrue('val1' not in open(csv_lvl3_fp).read())

    def test_barplot_no_taxonomy(self):
        with tempfile.TemporaryDirectory() as output_dir:
            _barplot(
                output_dir,
                self.table,
                self.rel_table,
                metadata=self.metadata
            )
            index_fp = os.path.join(output_dir, 'index.html')
            self.assertTrue(os.path.exists(index_fp))
            self.assertTrue("src='level-1.jsonp?callback=load_data'" in
                            open(index_fp).read())
            csv_lvl1_fp = os.path.join(output_dir, 'level-1.csv')
            self.assertTrue(os.path.exists(csv_lvl1_fp))
            self.assertTrue('val1' in open(csv_lvl1_fp).read())

    def test_barplot_collapsed_table(self):
        with tempfile.TemporaryDirectory() as output_dir:
            collapsed_table = collapse(self.table, self.taxonomy, 3)
            rel_table = collapsed_table.norm(axis='sample', inplace=False)
            _barplot(
                output_dir,
                collapsed_table,
                rel_table,
                level_delimiter=';'
            )
            # if level three tables exist, the taxonomy was parsed
            # correctly from the collapsed table.
            csv_lvl3_fp = os.path.join(output_dir, 'level-3.csv')
            self.assertTrue(os.path.exists(csv_lvl3_fp))
            self.assertTrue('val1' not in open(csv_lvl3_fp).read())
