import json
import os.path
import pkg_resources
import shutil

import pandas as pd
import biom
from trender import TRender

from qiime import Metadata
from qiime.plugin.util import transform

from ._util import _extract_to_level


def barplot(output_dir: str, table: biom.Table, taxonomy: pd.Series,
            metadata: Metadata) -> None:
    metadata = metadata.to_dataframe()
    filenames = []
    collapsed_tables = _extract_to_level(taxonomy, table)

    for level, collapsed_table in enumerate(collapsed_tables, 1):
        # Join collapsed table with metadata
        df = transform(collapsed_table, to_type=pd.DataFrame)
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
    TEMPLATES = pkg_resources.resource_filename('q2_taxa', 'assets')
    index = TRender('index.template', path=TEMPLATES)
    rendered_index = index.render({'filenames': filenames})
    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        fh.write(rendered_index)

    # Copy assets for rendering figure
    shutil.copytree(os.path.join(TEMPLATES, 'dst'),
                    os.path.join(output_dir, 'dist'))
