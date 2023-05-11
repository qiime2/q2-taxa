# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


def _get_max_level(taxonomy, level_delimiter):
    return taxonomy.apply(lambda x: len(x.split(level_delimiter))).max()


def _collapse_table(table, taxonomy, level, max_observed_level,
                    level_delimiter):
    table_ids = set(table.ids(axis='observation'))
    taxonomy_ids = set(taxonomy.index)
    missing_ids = table_ids.difference(taxonomy_ids)
    if len(missing_ids) > 0:
        raise ValueError('Feature IDs found in the table are missing from the '
                         'taxonomy: {}'.format(missing_ids))

    table = table.copy()

    def _collapse(id_, md, level_delimiter=level_delimiter):
        tax = taxonomy.loc[id_]
        tax = [x.strip() for x in tax.split(level_delimiter)]
        if len(tax) < max_observed_level:
            padding = ['__'] * (max_observed_level - len(tax))
            tax.extend(padding)
        return level_delimiter.join(tax[:level])

    return table.collapse(_collapse, axis='observation', norm=False)


def _extract_to_level(taxonomy, table, level_delimiter):
    # Assemble the taxonomy data
    max_obs_lvl = _get_max_level(taxonomy, level_delimiter)

    collapsed_tables = []
    # Collapse table at specified level
    for level in range(1, max_obs_lvl + 1):
        collapsed_table = _collapse_table(
            table, taxonomy, level, max_obs_lvl, level_delimiter)
        as_df = _biom_to_df(collapsed_table)
        collapsed_tables.append(as_df)

    return collapsed_tables


def _biom_to_df(table):
    return table.transpose().to_dataframe(dense=True)
