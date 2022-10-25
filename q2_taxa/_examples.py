# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

m_p_base = 'https://docs.qiime2.org/{epoch}/data/tutorials/moving-pictures/'
table_url = m_p_base + 'gut-table.qza'
taxonomy_url = m_p_base + 'taxonomy.qza'


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
