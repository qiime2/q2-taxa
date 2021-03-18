# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


def _get_max_level(taxonomy):
    return taxonomy.apply(lambda x: len(x.split(';'))).max()


def _get_padding_ranks(taxonomy):
    # get the maximum number of ranks
    max_obs_lvl = _get_max_level(taxonomy)
    # split the taxonomy
    taxonomy_split = taxonomy.str.split('; ', expand=True)
    # reduce ranks to strings before (and with) the first underscore(s)
    poss_ranks = taxonomy_split.apply(
        lambda x: x.str.extract('(.*?_+)', expand=True)[0], axis=1)
    # if strings found for every rank and same across taxa (None are ignored)
    if not poss_ranks.isna().all().sum() and poss_ranks.nunique().max() == 1:
        # return the list of ranks for padding
        return list(poss_ranks[~poss_ranks.isna().any(1)].values[0])
    # otherwise return None, which will not leave with blank padding


def _collapse_table(table, taxonomy, level, max_observed_level):
    table_ids = set(table.columns)
    taxonomy_ids = set(taxonomy.index)
    missing_ids = table_ids.difference(taxonomy_ids)
    if len(missing_ids) > 0:
        raise ValueError('Feature IDs found in the table are missing from the '
                         'taxonomy: {}'.format(missing_ids))

    table = table.copy()

    padding_ranks = _get_padding_ranks(taxonomy)

    def _collapse(tax):
        tax = [x.strip() for x in tax.split(';')]

        if len(tax) < max_observed_level:
            if padding_ranks:
                padding = [padding_ranks[x] for x in range(len(tax), max_observed_level)]
            else:
                # I suggest this situation gets fixed for a collapsing desire
                # (probably the taxa could be discarded?)
                padding = ['__'] * (max_observed_level - len(tax))
            tax.extend(padding)
        return ';'.join(tax[:level])

    table.columns = taxonomy.apply(_collapse)[table.columns]
    return table.groupby(table.columns, axis=1).agg(sum)


def _extract_to_level(taxonomy, table):
    # Assemble the taxonomy data
    max_obs_lvl = _get_max_level(taxonomy)

    collapsed_tables = []
    # Collapse table at specified level
    for level in range(1, max_obs_lvl + 1):
        collapsed_table = _collapse_table(table, taxonomy, level, max_obs_lvl)
        collapsed_tables.append(collapsed_table)

    return collapsed_tables
