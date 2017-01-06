# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


def _get_max_level(taxonomy):
    return taxonomy.apply(lambda x: len(x.split(';'))).max()


def _collapse_table(table, taxonomy, level, max_observed_level):
    table = table.copy()

    def _collapse(tax):
        tax = [x.strip() for x in tax.split(';')]
        if len(tax) < max_observed_level:
            padding = ['__'] * (max_observed_level - len(tax))
            tax.extend(padding)
        return ';'.join(tax[:level])

    table.columns = taxonomy.apply(_collapse)[table.columns]
    return table.groupby(table.columns, axis=1).agg(sum)


def _extract_to_level(taxonomy, table, max_level=None):
    # Assemble the taxonomy data
    max_obs_lvl = _get_max_level(taxonomy)

    if max_level is None:
        max_level = max_obs_lvl

    if max_level > max_obs_lvl:
        raise ValueError('Requested max_level of %d is larger than max_level '
                         'available in taxonomy data (%d).' % (max_level,
                                                               max_obs_lvl))

    collapsed_tables = []
    # Collapse table at specified level
    for level in range(1, max_level + 1):
        collapsed_table = _collapse_table(table, taxonomy, level, max_obs_lvl)
        collapsed_tables.append(collapsed_table)

    return collapsed_tables
