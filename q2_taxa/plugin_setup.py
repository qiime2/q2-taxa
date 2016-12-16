# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime.plugin

import q2_taxa

from q2_types.feature_data import FeatureData, Taxonomy
from q2_types.feature_table import FeatureTable, Frequency


from ._taxa_visualizer import barplot, tabulate
from ._util import collapse


plugin = qiime.plugin.Plugin(
    name='taxa',
    version=q2_taxa.__version__,
    website='https://github.com/qiime2/q2-taxa',
    package='q2_taxa',
    user_support_text=None,
    citation_text=None
)

plugin.methods.register_function(
    function=collapse,
    inputs={
        'taxonomy': FeatureData[Taxonomy],
        'table': FeatureTable[Frequency]
    },
    parameters={'level': qiime.plugin.Int},
    outputs=[('collapsed_table', FeatureTable[Frequency])],
    name='Collapse features by their taxonomy at the specified level',
    description='Collapse groups of features that have the same taxonomic '
                'assignment through the specified level. The frequencies of '
                'all features will be summed when they are collapsed.'
)

plugin.visualizers.register_function(
    function=barplot,
    inputs={
        'taxonomy': FeatureData[Taxonomy],
        'table': FeatureTable[Frequency]
    },
    parameters={'metadata': qiime.plugin.Metadata},
    name='Visualize taxonomy with an interactive bar plot',
    description='This visualizer produces an interactive barplot visualization'
                ' of taxonomies. Interactive features include multi-level '
                'sorting, plot recoloring, category selection/highlighting, '
                'sample relabeling, and SVG figure export.'
)

plugin.visualizers.register_function(
    function=tabulate,
    inputs={'data': FeatureData[Taxonomy]},
    parameters={},
    name='View taxonomy associated with each feature',
    description="Generate tabular view of feature identifier to taxonomic "
                "assignment mapping."
)
