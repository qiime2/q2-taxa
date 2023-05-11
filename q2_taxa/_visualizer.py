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

from ._util import _extract_to_level, _biom_to_df


TEMPLATES = pkg_resources.resource_filename('q2_taxa', 'assets')


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
            taxonomy = pd.Series(_ids, index=_ids)
    # Note: if a taxonomy is passed we will default to a semicolon delimiter.
    # This feels slightly dirty, but seems like a way to have our cake and eat
    # it too. i.e., we can add the level_delimiter parameter AND make the
    # default None (so that feature IDs are not automatically parsed) without
    # breaking the current behavior of barplot.
    # The user can override this behavior by just setting an arbitrary
    # delimiter (e.g., |) if they really want to make a barplot of a taxonomy
    # without splitting into levels, which feels like an edge case that might
    # not ever actually happen.
    else:
        if level_delimiter is None:
            level_delimiter = ';'

    num_metadata_cols = metadata.column_count
    metadata = metadata.to_dataframe()
    jsonp_files, csv_files = [], []
    if collapse:
        print(level_delimiter)
        collapsed_tables = _extract_to_level(
            taxonomy, table, level_delimiter=level_delimiter)
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
