# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
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


def _ids_to_keep_from_taxonomy(feature_ids, taxonomy, include, exclude,
                               query_delimiter, mode):
    if include is None and exclude is None:
        raise ValueError("At least one filtering term must be provided.")

    ids_without_taxonomy = set(feature_ids) - set(taxonomy.ids)
    if len(ids_without_taxonomy) > 0:
        raise ValueError("All features ids must be present in taxonomy, but "
                         "the following feature ids are not: %s"
                         % ', '.join(ids_without_taxonomy))

    # Remove feature ids from taxonomy that are not present in
    # feature_ids (this simplifies the actual filtering step downstream) by
    # ensuring that there are no "extra ids" in the returned ids_to_keep.
    taxonomy = taxonomy.filter_ids(feature_ids)

    if mode == 'exact':
        query_template = "Taxon='%s'"
    elif mode == 'contains':
        if include is not None:
            include = include.replace('_', '\\_')
        if exclude is not None:
            exclude = exclude.replace('_', '\\_')
        query_template = "Taxon LIKE '%%%s%%' ESCAPE '\\'"
    else:
        raise ValueError('Unknown mode: %s' % mode)

    # First identify the features that are included (if no includes are
    # provided, include all features).
    if include is not None:
        include = include.split(query_delimiter)
        ids_to_keep = set()
        for e in include:
            query = query_template % e
            # an sqlite database is being built for every query. if performance
            # becomes an issue, this is a target for refactoring.
            ids_to_keep |= set(taxonomy.get_ids(where=query))
    else:
        ids_to_keep = set(feature_ids)

    # Then, remove features that are excluded.
    if exclude is not None:
        exclude = exclude.split(query_delimiter)
        for e in exclude:
            query = query_template % e
            # an sqlite database is being built for every query. if performance
            # becomes an issue, this is a target for refactoring.
            ids_to_keep -= set(taxonomy.get_ids(where=query))

    return ids_to_keep


def filter_table(table: pd.DataFrame, taxonomy: qiime2.Metadata,
                 include: str = None, exclude: str = None,
                 query_delimiter: str = ',', mode: str = 'contains') \
                 -> pd.DataFrame:
    ids_to_keep = _ids_to_keep_from_taxonomy(
        table.columns, taxonomy, include, exclude, query_delimiter,
        mode)

    if len(ids_to_keep) == 0:
        raise ValueError("All features were filtered, resulting in an "
                         "empty table.")

    # filter the table to only the ids that should be retained
    table = table[list(ids_to_keep)]

    # drop samples that now have a zero-count
    table = table[table.T.sum() > 0]
    if table.shape[0] == 0:
        raise ValueError("All features with frequencies greater than zero "
                         "were filtered, resulting in an empty table.")

    return table


def filter_seqs(sequences: pd.Series, taxonomy: qiime2.Metadata,
                include: str = None, exclude: str = None,
                query_delimiter: str = ',', mode: str = 'contains') \
                -> pd.Series:
    ids_to_keep = _ids_to_keep_from_taxonomy(
        sequences.index, taxonomy, include, exclude, query_delimiter,
        mode)

    if len(ids_to_keep) == 0:
        raise ValueError("All features were filtered, resulting in an "
                         "empty collection of feature sequences.")

    return sequences[ids_to_keep]
