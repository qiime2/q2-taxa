import os.path
import shutil

import pandas as pd
import biom
from trender import TRender

from qiime import Metadata
from qiime.plugin.util import transform


def viz(output_dir: str, taxonomy: pd.Series, frequency: biom.Table,
        metadata: Metadata) -> None:
    metadata = metadata.to_dataframe()
    taxa = {}
    for k, v in taxonomy.to_dict().items():
        taxa[k] = {'taxonomy': [x.strip() for x in v.split(';')]}
    frequency.add_metadata(taxa, axis='observation')

    depth = len(list(taxa.values())[0]['taxonomy'])
    tsvs = []

    for lvl in range(depth):
        def bin_f(id_, x):
            return ';'.join(x['taxonomy'][:lvl+1])

        table = frequency.collapse(bin_f, norm=False, min_group_size=1,
                                   axis='observation')
        df = transform(table, to_type=pd.DataFrame)
        taxa_cols = df.columns.values.tolist()
        df = df.join(metadata, how='left')

        filename = 'lvl-%d.tsvp' % lvl
        tsvs.append(filename)
        with open(os.path.join(output_dir, filename), 'w') as fh:
            # TODO: fix SampleID column label in dataframe
            fh.write('load_data("Level %d",%s,`SampleID' % (lvl, taxa_cols))
            df.to_csv(fh, sep='\t', line_terminator='\n')
            fh.write('`);')

    TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'assets')
    index = TRender('index.template', path=TEMPLATES)
    rendered_index = index.render({'tsvs': tsvs})
    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        fh.write(rendered_index)

    shutil.copytree(os.path.join(TEMPLATES, 'dst'),
                    os.path.join(output_dir, 'dist'))
