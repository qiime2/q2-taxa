import qiime.plugin

import q2_taxa

from q2_types.feature_data import FeatureData, Taxonomy
from q2_types.feature_table import FeatureTable, Frequency


from ._taxa_visualizer import viz


plugin = qiime.plugin.Plugin(
    name='taxa',
    version=q2_taxa.__version__,
    website='https://github.com/qiime2/q2-taxa',
    package='q2_taxa',
    user_support_text=None,
    citation_text=None
)

plugin.visualizers.register_function(
    function=viz,
    inputs={
        'taxonomy': FeatureData[Taxonomy],
        'frequency': FeatureTable[Frequency]
    },
    parameters={'metadata': qiime.plugin.Metadata},
    name='Visualize taxonomy',
    description='This visualizer produces an interactive visualization of '
                'taxonomies.'
)
