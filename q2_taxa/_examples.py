# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2

epoch = qiime2.__release__
m_p_base = f'https://docs.qiime2.org/{epoch}/data/tutorials/moving-pictures/'
table_url = m_p_base + 'gut-table.qza'
taxonomy_url = m_p_base + 'taxonomy.qza'

metadata_url = 'https://data.qiime2.org/{epoch}/tutorials/moving-pictures/' \
    'sample_metadata.tsv'


def collapse_example(use):
    table = use.init_artifact_from_url('table', table_url)
    taxonomy = use.init_artifact_from_url('taxonomy', taxonomy_url)

    collapsed, = use.action(
        use.UsageAction('taxa', 'collapse'),
        use.UsageInputs(
            table=table,
            taxonomy=taxonomy,
            level=6,
        ),
        use.UsageOutputNames(
            collapsed_table='collapsed_table_l6',
        )
    )

    collapsed.assert_output_type('FeatureTable[Frequency]')


def barplot_example(use):
    table = use.init_artifact_from_url('table', table_url)
    taxonomy = use.init_artifact_from_url('taxonomy', taxonomy_url)
    md = use.init_metadata_from_url('sample-metadata', metadata_url)

    viz, = use.action(
        use.UsageAction('taxa', 'barplot'),
        use.UsageInputs(
            table=table,
            taxonomy=taxonomy,
            metadata=md,
        ),
        use.UsageOutputNames(
            visualization='taxa-bar-plots',
        )
    )

    viz.assert_output_type('Visualization')
