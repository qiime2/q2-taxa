# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import qiime2

from ._util import _collapse_table, _get_max_level


def collapse(table: pd.DataFrame, taxonomy: pd.Series,
             level: int) -> pd.DataFrame:
    if level < 1:
        raise ValueError('Requested level of %d is too low. Must be greater '
                         'than or equal to 1.' % level)

    # Assemble the taxonomy data
    max_observed_level = _get_max_level(taxonomy)

    if level > max_observed_level:
        raise ValueError('Requested level of %d is larger than the maximum '
                         'level available in taxonomy data (%d).' %
                         (level, max_observed_level))

    return _collapse_table(table, taxonomy, level, max_observed_level)


def filter_table(table: pd.DataFrame, taxonomy: qiime2.Metadata,
                 include: str=None, exclude: str=None,
                 query_delimiter: str=',', exact_match: bool=False) \
                 -> pd.DataFrame:

    if include is None and exclude is None:
        raise ValueError("At least one filtering criterion must be provided.")

    if exact_match:
        query_template = "Taxon='%s'"
    else:
        query_template = "Taxon LIKE '%%%s%%'"

    # First identify the features that are included (if no includes are
    # provided, include all features).
    if include is not None:
        include = include.split(query_delimiter)
        ids_to_keep = set()
        for e in include:
            query = query_template % e
            ids_to_keep |= set(taxonomy.ids(where=query))
    else:
        ids_to_keep = set(table.columns)

    # Then, remove features that are excluded.
    if exclude is not None:
        exclude = exclude.split(query_delimiter)
        for e in exclude:
            query = query_template % e
            ids_to_keep -= set(taxonomy.ids(where=query))

    if len(ids_to_keep) == 0:
        raise ValueError("All features were filtered, resulting in an "
                         "empty table.")

    # filter the table to only the ids that should be retained
    table = table[list(ids_to_keep)]
    # drop samples that now have a zero-count
    table = table[table.T.sum() > 0]
    return table


def filter_seqs(seqs: pd.Series, taxonomy: qiime2.Metadata,
                 include: list, exclude: list,
                 include_exact: list, exclude_exact: list) -> pd.Series:
    pass
