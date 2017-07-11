# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin

import q2_taxa

from q2_types.feature_data import FeatureData, Taxonomy
from q2_types.feature_table import FeatureTable, Frequency


from . import barplot, collapse


plugin = qiime2.plugin.Plugin(
    name='taxa',
    version=q2_taxa.__version__,
    website='https://github.com/qiime2/q2-taxa',
    package='q2_taxa',
    user_support_text=None,
    citation_text=None,
    description=('This QIIME 2 plugin provides functionality for working with '
                 'and visualizing taxonomic annotations of features.'),
    short_description='Plugin for working with feature taxonomy annotations.'
)

plugin.methods.register_function(
    function=collapse,
    inputs={
        'taxonomy': FeatureData[Taxonomy],
        'table': FeatureTable[Frequency]
    },
    parameters={'level': qiime2.plugin.Int},
    outputs=[('collapsed_table', FeatureTable[Frequency])],
    input_descriptions={
        'taxonomy': ('Taxonomic annotations for features in the provided '
                     'feature table. All features in the feature table must '
                     'have a corresponding taxonomic annotation. Taxonomic '
                     'annotations that are not present in the feature table '
                     'will be ignored.'),
        'table': 'Feature table to be collapsed.'},
    parameter_descriptions={
        'level': ('The taxonomic level at which the features should be '
                  'collapsed. All ouput features will have exactly '
                  'this many levels of taxonomic annotation.')
    },
    output_descriptions={
        'collapsed_table': ('The resulting feature table, where all features '
                            'are now taxonomic annotations with the '
                            'user-specified number of levels.')
    },
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
    parameters={'metadata': qiime2.plugin.Metadata},
    input_descriptions={
        'taxonomy': ('Taxonomic annotations for features in the provided '
                     'feature table. All features in the feature table must '
                     'have a corresponding taxonomic annotation. Taxonomic '
                     'annotations that are not present in the feature table '
                     'will be ignored.'),
        'table': 'Feature table to visualize at various taxonomic levels.'},
    parameter_descriptions={'metadata': 'The sample metadata.'},
    name='Visualize taxonomy with an interactive bar plot',
    description='This visualizer produces an interactive barplot visualization'
                ' of taxonomies. Interactive features include multi-level '
                'sorting, plot recoloring, category selection/highlighting, '
                'sample relabeling, and SVG figure export.'
)
