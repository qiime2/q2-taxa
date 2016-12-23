# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import biom
import pandas as pd


def _assemble_taxonomy_data(taxonomy, table):
    taxa = {}
    max_obs_lvl = 0
    for k, v in taxonomy.iteritems():
        levels = [x.strip() for x in v.split(';')]
        max_obs_lvl = len(levels) if len(levels) > max_obs_lvl else max_obs_lvl
        taxa[k] = {'taxonomy': levels}
    table.add_metadata(taxa, axis='observation')

    return table, max_obs_lvl


def _collapse_table(table, level, max_observed_level):
    def bin_f(id_, x):
        if len(x['taxonomy']) < max_observed_level:
            padding = ['__'] * (max_observed_level - len(x['taxonomy']))
            x['taxonomy'].extend(padding)
        return ';'.join(x['taxonomy'][:level])
    return table.collapse(bin_f, norm=False, min_group_size=1,
                          axis='observation')


def _extract_to_level(taxonomy, table, max_level=None):
    # Assemble the taxonomy data
    table, max_obs_lvl = _assemble_taxonomy_data(taxonomy, table)

    if max_level is None:
        max_level = max_obs_lvl

    if max_level > max_obs_lvl:
        raise ValueError('Requested max_level of %d is larger than max_level '
                         'available in taxonomy data (%d).' % (max_level,
                                                               max_obs_lvl))

    collapsed_tables = []
    # Collapse table at specified level
    for level in range(1, max_level + 1):
        collapsed_table = _collapse_table(table, level, max_obs_lvl)
        collapsed_tables.append(collapsed_table)

    return collapsed_tables


def collapse(table: biom.Table, taxonomy: pd.Series, level: int) -> biom.Table:
    if level < 1:
        raise ValueError('Requested level of %d is too low. Must be greater '
                         'than or equal to 1.' % level)

    # Assemble the taxonomy data
    table, max_observed_level = _assemble_taxonomy_data(taxonomy, table)

    if level > max_observed_level:
        raise ValueError('Requested level of %d is larger than the maximum '
                         'level available in taxonomy data (%d).' %
                         (level, max_observed_level))

    return _collapse_table(table, level, max_observed_level)
