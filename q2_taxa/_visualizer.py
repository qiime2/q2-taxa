# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json
import os.path
from pathlib import Path
import importlib
import shutil

import biom
import pandas as pd
import q2templates

from qiime2 import Metadata

from ._util import _extract_to_level, _biom_to_df


TEMPLATES = importlib.resources.files('q2_taxa') / 'assets'


def barplot(output_dir: str, table: biom.Table, taxonomy: pd.Series = None,
            metadata: Metadata = None, level_delimiter: str = None) -> None:

    if metadata is None:
        metadata = Metadata(
            pd.DataFrame({'id': table.ids(axis='sample')}).set_index('id'))

    ids_not_in_metadata = set(table.ids(axis='sample')) - set(metadata.ids)
    if ids_not_in_metadata:
        raise ValueError('Sample IDs found in the table are missing in the '
                         f'metadata: {ids_not_in_metadata!r}.')

    collapse = True
    if taxonomy is None:
        if level_delimiter is None:
            collapse = False
        else:
            _ids = table.ids('observation')
            ranks = [r.replace(level_delimiter, ';') for r in _ids]
            taxonomy = pd.Series(ranks, index=_ids)

    num_metadata_cols = metadata.column_count
    metadata = metadata.to_dataframe()
    jsonp_files, csv_files = [], []
    if collapse:
        collapsed_tables = _extract_to_level(taxonomy, table)
    else:
        collapsed_tables = [_biom_to_df(table)]

    for level, df in enumerate(collapsed_tables, 1):
        # Stash column labels before manipulating dataframe
        taxa_cols = df.columns.values.tolist()
        # Join collapsed table with metadata
        df = df.join(metadata, how='left')
        df = df.reset_index(drop=False)  # Move index into columns
        # Our JS sort works best with empty strings vs nulls
        df = df.fillna('')
        all_cols = df.columns.values.tolist()

        jsonp_file = 'level-%d.jsonp' % level
        csv_file = 'level-%d.csv' % level

        jsonp_files.append(jsonp_file)
        csv_files.append(csv_file)

        df.to_csv(os.path.join(output_dir, csv_file), index=False)

        with open(os.path.join(output_dir, jsonp_file), 'w') as fh:
            fh.write('load_data(%d,' % level)
            json.dump(taxa_cols, fh)
            fh.write(',')
            json.dump(all_cols, fh)
            fh.write(',')
            df.to_json(fh, orient='records')
            fh.write(');')

    # Now that the tables have been collapsed, write out the index template
    index = os.path.join(TEMPLATES, 'barplot', 'index.html')
    q2templates.render(index, output_dir,
                       context={'jsonp_files': jsonp_files,
                                'num_metadata_cols': num_metadata_cols})

    # Copy assets for rendering figure
    shutil.copytree(os.path.join(TEMPLATES, 'barplot', 'dist'),
                    os.path.join(output_dir, 'dist'))


def barplot2(
    output_dir: str,
    table: pd.DataFrame,
    taxonomy: pd.Series = None,
    metadata: pd.DataFrame = None,
    level_delimiter: str | None = None
) -> None:
    '''
    '''
    dist_dir = (
        importlib.resources.files('q2_taxa') / '_barplot_visualizer' / 'dist'
    )
    shutil.copytree(str(dist_dir), output_dir, dirs_exist_ok=True)

    non_empty = table.sum(axis=1) > 0
    table = table.loc[non_empty, :]
    if len(table) == 0:
        msg = 'There are no non-empty samples in your feature table.'
        raise ValueError(msg)

    table.to_csv(Path(output_dir) / 'table.csv', index_label="sampleID")

    if metadata is not None:
        unexpected_ids = set(table.index) - set(metadata.ids)
        if unexpected_ids:
            msg = (
                'There are sample IDs in the feature table that are not '
                f'accounted for in the metadata. These are {unexpected_ids}.'
            )
            raise ValueError(msg)

        # manually recreate types header
        types_header = ["#q2:types"]
        for column in metadata.columns:
            column = metadata.get_column(column)
            types_header.append(column.type)

        metadata_df = metadata.to_dataframe()
        metadata_df.index.name = 'sampleID'
        metadata_df.reset_index(inplace=True)

        col_to_type = zip(list(metadata_df.columns), types_header)
        types_df = pd.DataFrame({col: [val] for col, val in col_to_type})
        metadata_df = pd.concat([types_df, metadata_df], ignore_index=True)

        metadata_df.to_csv(Path(output_dir) / 'metadata.csv', index=False)
    else:
        dummy_metadata = pd.DataFrame({
            'sampleID': ['#q2:types'] + list(table.index)
        })
        dummy_metadata.to_csv(Path(output_dir) / 'metadata.csv', index=False)

    if taxonomy is not None:
        unexpected_ids = set(table.columns) - set(taxonomy.index)
        if unexpected_ids:
            msg = (
                'There are feature IDs in the feature table that are not '
                f'accounted for in the taxonomy. These are {unexpected_ids}.'
            )
            raise ValueError(msg)

        taxonomy.to_csv(Path(output_dir) / 'taxonomy.csv')
    else:
        index = pd.Index(list(table.columns), name='Feature ID')

        if level_delimiter is not None:
            ids = list(table.columns)
            ids = [id.replace(';', ':') for id in ids]
            ids = [id.replace(level_delimiter, ';') for id in ids]

            dummy_taxonomy = pd.Series(ids, index=index, name='Taxon')
        else:
            dummy_taxonomy = pd.Series(
                table.columns, index=index, name='Taxon'
            )

        dummy_taxonomy.to_csv(Path(output_dir) / 'taxonomy.csv')
