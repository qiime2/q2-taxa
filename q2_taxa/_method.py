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
                 include_contains: str=None, exclude_contains: str=None,
                 include_exact: str=None, exclude_exact: str=None,
                 query_delimiter: str=',') \
                 -> pd.DataFrame:
    queries = []
    if include_contains is not None:
        include_contains = include_contains.split(query_delimiter)
        for e in include_contains:
            queries.append("Taxon LIKE '%%%s%%'" % e)
    if exclude_contains is not None:
        exclude_contains = exclude_contains.split(query_delimiter)
        for e in exclude_contains:
            queries.append("Taxon NOT LIKE '%%%s%%'" % e)
    if include_exact is not None:
        include_exact = include_exact.split(query_delimiter)
        for e in include_exact:
            queries.append("Taxon='%s'" % e)
    if exclude_exact is not None:
        exclude_exact = exclude_exact.split(query_delimiter)
        for e in exclude_exact:
            queries.append("NOT Taxon='%s'" % e)

    if len(queries) == 0:
        raise ValueError("At least one filtering criterion must be provided.")

    ids_to_keep = set(table.columns)
    for e in queries:
        ids_to_keep &= set(taxonomy.ids(where=e))

    if len(ids_to_keep) == 0:
        raise ValueError("All features were filtered, resulting in an "
                         "empty table.")

    table = table[list(ids_to_keep)]
    # drop samples that now have a zero-count
    return table[table.T.sum() > 0]


def filter_seqs(seqs: pd.Series, taxonomy: qiime2.Metadata,
                 include_contains: list, exclude_contains: list,
                 include_exact: list, exclude_exact: list) -> pd.Series:
    pass
