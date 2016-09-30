import os.path
import shutil

import pandas as pd
import biom
from trender import TRender

from qiime import Metadata
from qiime.plugin.util import transform


def bar_plots(output_dir: str, taxonomy: pd.Series, table: biom.Table,
        metadata: Metadata) -> None:
    metadata = metadata.to_dataframe()

    # Assemble the taxonomy data
    taxa = {}
    for k, v in taxonomy.to_dict().items():
        taxa[k] = {'taxonomy': [x.strip() for x in v.split(';')]}
    table.add_metadata(taxa, axis='observation')

    # Pluck first to determine depth.
    # TODO: Is it safe to assume that the depth will be the same for
    # each sample?
    depth = len(list(taxa.values())[0]['taxonomy'])
    tsvs = []

    # Collapse table at specified level
    for level in range(1, depth+1):
        def bin_f(id_, x):
            return ';'.join(x['taxonomy'][:level])
        collapsedTable = table.collapse(bin_f, norm=False, min_group_size=1,
                                   axis='observation')
        # Join collapsed table with metadata
        df = transform(collapsedTable, to_type=pd.DataFrame)
        taxa_cols = df.columns.values.tolist()
        df = df.join(metadata, how='left')

        filename = 'lvl-%d.tsvp' % level
        tsvs.append(filename)

        with open(os.path.join(output_dir, filename), 'w') as fh:
            # TODO: fix SampleID column label in dataframe
            fh.write('load_data("Level %d",%s,`SampleID' % (level, taxa_cols))
            df.to_csv(fh, sep='\t', line_terminator='\n')
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
