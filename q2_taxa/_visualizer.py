# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json
import os.path
import pkg_resources
import shutil

import pandas as pd
import q2templates

from qiime2 import Metadata

from ._util import _extract_to_level


TEMPLATES = pkg_resources.resource_filename('q2_taxa', 'assets')


def barplot(output_dir: str, table: pd.DataFrame, taxonomy: pd.Series,
            metadata: Metadata) -> None:
    metadata = metadata.to_dataframe()
    filenames = []
    collapsed_tables = _extract_to_level(taxonomy, table)

    for level, df in enumerate(collapsed_tables, 1):
        # Join collapsed table with metadata
        taxa_cols = df.columns.values.tolist()
        df = df.join(metadata, how='left')
        df = df.reset_index(drop=False)  # Move SampleID index into columns
        df = df.fillna('')  # JS sort works best with empty strings vs null
        all_cols = df.columns.values.tolist()

        filename = 'lvl-%d.jsonp' % level
        filenames.append(filename)

        with open(os.path.join(output_dir, filename), 'w') as fh:
            fh.write("load_data('Level %d'," % level)
            json.dump(taxa_cols, fh)
            fh.write(",")
            json.dump(all_cols, fh)
            fh.write(",")
            df.to_json(fh, orient='records')
            fh.write(");")

    # Now that the tables have been collapsed, write out the index template
    index = os.path.join(TEMPLATES, 'barplot', 'index.html')
    q2templates.render(index, output_dir, context={'filenames': filenames})

    # Copy assets for rendering figure
    shutil.copytree(os.path.join(TEMPLATES, 'barplot', 'dst'),
                    os.path.join(output_dir, 'dist'))


def tabulate(output_dir: str, data: pd.Series) -> None:
    prepped = []
    for _id, taxa in data.iteritems():
        prepped.append({'id': _id, 'taxa': taxa})

    index = os.path.join(TEMPLATES, 'tabulate', 'index.html')
    q2templates.render(index, output_dir, context={'data': prepped})
