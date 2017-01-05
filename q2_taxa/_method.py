# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd


def _collapse_pd_table(table, taxonomy, level, max_observed_level):
    def _collapse(tax):
        tax = [x.strip() for x in tax.split(';')]
        if len(tax) < max_observed_level:
            padding = ['__'] * (max_observed_level - len(tax))
            tax.extend(padding)
        return ';'.join(tax[:level])
    table.columns = taxonomy.apply(_collapse)[table.columns]
    return table.groupby(table.columns, axis=1).agg(sum)


def collapse(table: pd.DataFrame, taxonomy: pd.Series,
             level: int) -> pd.DataFrame:
    if level < 1:
        raise ValueError('Requested level of %d is too low. Must be greater '
                         'than or equal to 1.' % level)

    # Assemble the taxonomy data
    max_observed_level = taxonomy.apply(lambda x: len(x.split(';'))).max()

    if level > max_observed_level:
        raise ValueError('Requested level of %d is larger than the maximum '
                         'level available in taxonomy data (%d).' %
                         (level, max_observed_level))

    return _collapse_pd_table(table, taxonomy, level, max_observed_level)
