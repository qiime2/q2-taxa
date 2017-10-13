# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import biom
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

def _get_biom_filter_function(ids_to_keep):
    ids_to_keep = set(ids_to_keep)

    def f(data_vector, id_, metadata):
        return (id_ in ids_to_keep)

    return f

def filter_table(table: biom.Table, taxonomy: qiime2.Metadata,
                 include_contains: str=None, exclude_contains: str=None,
                 include_exact: str=None, exclude_exact: str=None) \
                 -> biom.Table:
    queries = []
    if include_contains is not None:
        queries.append("Taxon LIKE '%%%s%%'" % include_contains)
    if exclude_contains is not None:
        queries.append("Taxon NOT LIKE '%%%s%%'" % exclude_contains)
    if include_exact is not None:
        queries.append("Taxon='%s'" % include_exact)
    if exclude_exact is not None:
        queries.append("NOT Taxon='%s'" % exclude_exact)

    if len(queries) == 0:
        raise ValueError("At least one filtering criterion must be provided.")

    ids_to_keep = set(table.ids(axis='observation'))
    for e in queries:
        ids_to_keep &= set(taxonomy.ids(where=e))

    filter_fn = _get_biom_filter_function(ids_to_keep)
    table.filter(filter_fn, axis='observation', inplace=True)

    return table




def filter_seqs(seqs: pd.Series, taxonomy: pd.Series,
                 include_contains: list, exclude_contains: list,
                 include_exact: list, exclude_exact: list) -> pd.Series:
    pass
