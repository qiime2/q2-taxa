# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin

import q2_taxa

from q2_types.feature_data import (
    FeatureData, Taxonomy, Sequence, AlignedSequence
)
from q2_types.feature_table import (
    FeatureTable, Frequency, RelativeFrequency, PresenceAbsence,
    Composition,
)


from . import (
    barplot, barplot2, collapse, feature_ids_to_taxonomy, filter_table,
    filter_seqs
)
import q2_taxa._examples as ex

T1 = qiime2.plugin.TypeMatch([Frequency, PresenceAbsence])
T2 = qiime2.plugin.TypeMatch([Sequence, AlignedSequence])

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
                'all features will be summed when they are collapsed.',
    examples={
        'collapse': ex.collapse_example,
    },
)

plugin.methods.register_function(
    function=feature_ids_to_taxonomy,
    inputs={
        'table': FeatureTable[
            Frequency | RelativeFrequency | PresenceAbsence | Composition
        ]
    },
    parameters={
        'delimiter': qiime2.plugin.Str,
        'strict': qiime2.plugin.Bool,
        'semicolon_replacement': qiime2.plugin.Str,
    },
    outputs=[('taxonomy', FeatureData[Taxonomy])],
    input_descriptions={
        'table': (
            'The table containing the feature IDs to be parsed into a '
            'taxonomy.'
        )
    },
    parameter_descriptions={
        'delimiter': (
            'The character(s) that delimit taxonomic levels in the feature '
            'IDs.'
        ),
        'strict': (
            'Whether to parse the feature IDs in strict mode. If True, then '
            'no occurences of semicolons are allowed in the feature IDs, at '
            'least one ID must contain `delimiter`, and no empty levels are '
            'allowed in the converted taxonomic strings. If False, none of '
            'these conditions are enforced.'
        ),
        'semicolon_replacement': (
            'The character to use to replace semicolons before replacing '
            'occurences of `delimiter` with semicolons. Ignored if `strict` '
            'parsing is enabled.'
        )
    },
    output_descriptions={
        'taxonomy': (
            'The taxonomy parsed from the table\'s feature IDs with the Taxon '
            'column using the typical semicolon delimitation.'
        )
    },
    name='Create a taxonomy from hierarchical feature IDs in a feature table.',
    description=(
        'This method converts feature IDs in a feature table into a taxonomy '
        'by splitting IDs on a delimiter and joining levels with semicolons.'
    )
)

plugin.methods.register_function(
    function=filter_table,
    inputs={
        'taxonomy': FeatureData[Taxonomy],
        'table': FeatureTable[T1]
    },
    parameters={'include': qiime2.plugin.Str,
                'exclude': qiime2.plugin.Str,
                'mode':
                    qiime2.plugin.Str % qiime2.plugin.Choices(
                        ['exact', 'contains']),
                'query_delimiter': qiime2.plugin.Str},
    outputs=[('filtered_table', FeatureTable[T1])],
    input_descriptions={
        'taxonomy': ('Taxonomic annotations for features in the provided '
                     'feature table. All features in the feature table must '
                     'have a corresponding taxonomic annotation. Taxonomic '
                     'annotations for features that are not present in the '
                     'feature table will be ignored.'),
        'table': 'Feature table to be filtered.'},
    parameter_descriptions={
        'include': ('One or more search terms that indicate which taxa should '
                    'be included in the resulting table. If providing '
                    'more than one term, terms should be delimited by the '
                    'query-delimiter character. By default, all taxa '
                    'will be included.'),
        'exclude': ('One or more search terms that indicate which taxa should '
                    'be excluded from the resulting table. If providing '
                    'more than one term, terms should be delimited by the '
                    'query-delimiter character. By default, no taxa '
                    'will be excluded.'),
        'mode': ('Mode for determining if a search term matches a taxonomic '
                 'annotation. "contains" requires that the annotation '
                 'has the term as a substring; "exact" requires that the '
                 'annotation is a perfect match to a search term.'),
        'query_delimiter': ('The string used to delimit multiple search terms '
                            'provided to include or exclude. This parameter '
                            'should only need to be modified if the default '
                            'delimiter (a comma) is used in the provided '
                            'taxonomic annotations.')
    },
    output_descriptions={
        'filtered_table': ('The taxonomy-filtered feature table.')
    },
    name='Taxonomy-based feature table filter.',
    description=('This method filters features from a table based on their '
                 'taxonomic annotations. Features can be retained in the '
                 'resulting table by specifying one or more include search '
                 'terms, and can be filtered out of the resulting table by '
                 'specifying one or more exclude search terms. If both '
                 'include and exclude are provided, the inclusion critera '
                 'will be applied before the exclusion critera. Either '
                 'include or exclude terms (or both) must be provided. Any '
                 'samples that have a total frequency of zero after filtering '
                 'will be removed from the resulting table.')
)

plugin.methods.register_function(
    function=filter_seqs,
    inputs={
        'taxonomy': FeatureData[Taxonomy],
        'sequences': FeatureData[T2]
    },
    parameters={'include': qiime2.plugin.Str,
                'exclude': qiime2.plugin.Str,
                'mode':
                    qiime2.plugin.Str % qiime2.plugin.Choices(
                        ['exact', 'contains']),
                'query_delimiter': qiime2.plugin.Str},
    outputs=[('filtered_sequences', FeatureData[T2])],
    input_descriptions={
        'taxonomy': ('Taxonomic annotations for features in the provided '
                     'feature sequences. All features in the feature '
                     'sequences must have a corresponding taxonomic '
                     'annotation. Taxonomic annotations for features that are '
                     'not present in the feature sequences will be ignored.'),
        'sequences': 'Feature sequences or aligned sequences to be filtered.'},
    parameter_descriptions={
        'include': ('One or more search terms that indicate which taxa should '
                    'be included in the resulting sequences. If providing '
                    'more than one term, terms should be delimited by the '
                    'query-delimiter character. By default, all taxa '
                    'will be included.'),
        'exclude': ('One or more search terms that indicate which taxa should '
                    'be excluded from the resulting sequences. If providing '
                    'more than one term, terms should be delimited by the '
                    'query-delimiter character. By default, no taxa '
                    'will be excluded.'),
        'mode': ('Mode for determining if a search term matches a taxonomic '
                 'annotation. "contains" requires that the annotation '
                 'has the term as a substring; "exact" requires that the '
                 'annotation is a perfect match to a search term.'),
        'query_delimiter': ('The string used to delimit multiple search terms '
                            'provided to include or exclude. This parameter '
                            'should only need to be modified if the default '
                            'delimiter (a comma) is used in the provided '
                            'taxonomic annotations.')
    },
    output_descriptions={
        'filtered_sequences': ('The taxonomy-filtered feature sequences.')
    },
    name='Taxonomy-based feature sequence filter.',
    description=('This method filters sequences based on their '
                 'taxonomic annotations. Features can be retained in the '
                 'result by specifying one or more include search '
                 'terms, and can be filtered out of the result by '
                 'specifying one or more exclude search terms. If both '
                 'include and exclude are provided, the inclusion critera '
                 'will be applied before the exclusion critera. Either '
                 'include or exclude terms (or both) must be provided.')
)

plugin.visualizers.register_function(
    function=barplot,
    inputs={
        'taxonomy': FeatureData[Taxonomy],
        'table': FeatureTable[Frequency | PresenceAbsence]
    },
    parameters={'metadata': qiime2.plugin.Metadata,
                'level_delimiter': qiime2.plugin.Str},
    input_descriptions={
        'taxonomy': ('Taxonomic annotations for features in the provided '
                     'feature table. All features in the feature table must '
                     'have a corresponding taxonomic annotation. Taxonomic '
                     'annotations that are not present in the feature table '
                     'will be ignored. If no taxonomy is provided, the '
                     'feature IDs will be used as labels.'),
        'table': 'Feature table to visualize at various taxonomic levels.'},
    parameter_descriptions={
        'metadata': 'The sample metadata.',
        'level_delimiter': 'Attempt to parse hierarchical taxonomic '
                           'information from feature IDs by separating '
                           'levels with this character. This parameter '
                           'is ignored if a taxonomy is provided as input.'
        },
    name='Visualize taxonomy with an interactive bar plot',
    description='This visualizer produces an interactive barplot visualization'
                ' of taxonomies. Interactive features include multi-level '
                'sorting, plot recoloring, sample relabeling, and SVG '
                'figure export.\n\nThis visualizer is planned to be replaced '
                'with the current `barplot2` visualizer in this plugin. We '
                'are interested in user feedback on `barplot2`, so please '
                'consider trying it out and letting us know how it works for '
                'you.',
    examples={
        'barplot': ex.barplot_example,
    }
)

plugin.visualizers.register_function(
    function=barplot2,
    inputs={
        'taxonomy': FeatureData[Taxonomy],
        'table': FeatureTable[Frequency | PresenceAbsence | RelativeFrequency]
    },
    parameters={'metadata': qiime2.plugin.Metadata,
                'level_delimiter': qiime2.plugin.Str},
    input_descriptions={
        'taxonomy': ('Taxonomic annotations for features in the provided '
                     'feature table. All features in the feature table must '
                     'have a corresponding taxonomic annotation. Taxonomic '
                     'annotations that are not present in the feature table '
                     'will be ignored. If no taxonomy is provided, the '
                     'feature IDs will be used as labels.'),
        'table': 'Feature table to visualize at various taxonomic levels.'
    },
    parameter_descriptions={
        'metadata': 'The sample metadata.',
        'level_delimiter': 'Attempt to parse hierarchical taxonomic '
                           'information from feature IDs by separating '
                           'levels with this character. This parameter '
                           'is ignored if a taxonomy is provided as input.'
    },
    name='Experimental interactive stacked bar plot of per-sample taxa.',
    description=("This is an early release of a replacement for the `barplot` "
                 "visualizer in this plugin. As of 2025.10, this should be "
                 "considered experimental, and we are very interested in "
                 "community feedback on this new visualizer. This command "
                 "will eventually be removed when this visualizer replaces "
                 "the `barplot` visualizer."),
    deprecated=True,
    examples={
        'barplot': ex.barplot2_example,
    },
)
