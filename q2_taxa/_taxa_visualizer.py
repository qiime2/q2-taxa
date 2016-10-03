import os.path
import shutil

import pandas as pd
import biom
from trender import TRender

from qiime import Metadata
from qiime.plugin.util import transform

from ._util import _extract_to_level


def barplot(output_dir: str, taxonomy: pd.Series, table: biom.Table,
            metadata: Metadata) -> None:
    metadata = metadata.to_dataframe()
    tsvs = []
    collapsed_tables = _extract_to_level(taxonomy, table)

    for level, collapsed_table in enumerate(collapsed_tables, 1):
        # Join collapsed table with metadata
        df = transform(collapsed_table, to_type=pd.DataFrame)
        taxa_cols = df.columns.values.tolist()
        df = df.join(metadata, how='left')
        df['SampleID'] = df.index
        df = df.fillna('')  # D3 sort works best with empty strings vs null
        all_cols = df.columns.values.tolist()
        # viz relies on first column being `SampleID`
        all_cols.insert(0, all_cols.pop(all_cols.index('SampleID')))

        filename = 'lvl-%d.jsonp' % level
        tsvs.append(filename)

        with open(os.path.join(output_dir, filename), 'w') as fh:
            fh.write('load_data("Level %d",%s,%s,`' % (level, taxa_cols,
                                                       all_cols))
            df.to_json(fh, orient='records')
            fh.write('`);')

    # Now that the tables have been collapsed, write out the index template
    TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'assets')
    index = TRender('index.template', path=TEMPLATES)
    rendered_index = index.render({'tsvs': tsvs})
    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        fh.write(rendered_index)

    # Copy assets for rendering figure
    shutil.copytree(os.path.join(TEMPLATES, 'dst'),
                    os.path.join(output_dir, 'dist'))
