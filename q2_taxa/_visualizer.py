# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json
import os.path
import pkg_resources
import shutil

import biom
import pandas as pd
import q2templates

from qiime2 import Metadata
from q2_types.feature_table import FeatureTable, RelativeFrequency

from ._util import _extract_to_level, _biom_to_df


TEMPLATES = pkg_resources.resource_filename('q2_taxa', 'assets')


def _barplot(
    output_dir: str,
    table: biom.Table,
    relative_table: biom.Table,
    taxonomy: pd.Series = None,
    metadata: Metadata = None,
    level_delimiter: str = None
) -> None:

    if metadata is None:
        metadata = Metadata(
            pd.DataFrame({'id': table.ids(axis='sample')}).set_index('id')
        )

    ids_not_in_metadata = set(table.ids(axis='sample')) - set(metadata.ids)
    if ids_not_in_metadata:
        raise ValueError('Sample IDs found in the table are missing in the '
                         f'metadata: {ids_not_in_metadata!r}.')

    collapse = True
    if taxonomy is None:
        if level_delimiter is None:
            collapse = False
        else:
            _ids = relative_table.ids('observation')
            ranks = [r.replace(level_delimiter, ';') for r in _ids]
            taxonomy = pd.Series(ranks, index=_ids)

    num_metadata_cols = metadata.column_count
    metadata = metadata.to_dataframe()
    jsonp_files, csv_files = [], []
    if collapse:
        collapsed_relative_tables = _extract_to_level(taxonomy, relative_table)
        collapsed_tables = _extract_to_level(taxonomy, table)
    else:
        collapsed_relative_tables = [_biom_to_df(relative_table)]
        collapsed_tables = [_biom_to_df(table)]

    for level, (rel_df, og_df) in enumerate(
        zip(collapsed_relative_tables, collapsed_tables), 1
    ):
        # Stash column labels before manipulating dataframe
        taxa_cols = rel_df.columns.values.tolist()

        # Join collapsed table with metadata
        rel_df = rel_df.join(metadata, how='left')
        og_df = og_df.join(metadata, how='left')

        # Move index into columns
        rel_df = rel_df.reset_index(drop=False)
        og_df = og_df.reset_index(drop=False)

        # Our JS sort works best with empty strings vs nulls
        rel_df = rel_df.fillna('')
        all_cols = rel_df.columns.values.tolist()

        jsonp_file = 'level-%d.jsonp' % level
        csv_file = 'level-%d.csv' % level

        jsonp_files.append(jsonp_file)
        csv_files.append(csv_file)

        og_df.to_csv(os.path.join(output_dir, csv_file), index=False)

        with open(os.path.join(output_dir, jsonp_file), 'w') as fh:
            fh.write('load_data(%d,' % level)
            json.dump(taxa_cols, fh)
            fh.write(',')
            json.dump(all_cols, fh)
            fh.write(',')
            rel_df.to_json(fh, orient='records')
            fh.write(');')

    # Now that the tables have been collapsed, write out the index template
    index = os.path.join(TEMPLATES, 'barplot', 'index.html')
    q2templates.render(index, output_dir,
                       context={'jsonp_files': jsonp_files,
                                'num_metadata_cols': num_metadata_cols})

    # Copy assets for rendering figure
    shutil.copytree(os.path.join(TEMPLATES, 'barplot', 'dist'),
                    os.path.join(output_dir, 'dist'))


def barplot(ctx, table, taxonomy=None, metadata=None, level_delimiter=None):
    _barplot = ctx.get_action('taxa', '_barplot')

    if table.type <= FeatureTable[RelativeFrequency]:
        relative_table = table
    else:
        relative_frequency = ctx.get_action(
            'feature_table', 'relative_frequency'
        )
        relative_table, = relative_frequency(table=table)

    visualization, = _barplot(
        table=table,
        relative_table=relative_table,
        taxonomy=taxonomy,
        metadata=metadata,
        level_delimiter=level_delimiter
    )

    return (visualization)
