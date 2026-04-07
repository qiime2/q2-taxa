# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import biom
import qiime2

from ._util import _collapse_table, _get_max_level


def collapse(table: biom.Table, taxonomy: pd.Series,
             level: int) -> biom.Table:
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


def _format_invalid_ids(ids: list[str], max_examples: int = 5):
    examples = ', '.join(repr(id_) for id_ in ids[:max_examples])
    if len(ids) > max_examples:
        examples = f'{examples}, ...'

    return f'{len(ids)} feature IDs. Examples: {examples}'


def feature_ids_to_taxonomy(
    table: biom.Table,
    delimiter: str = ';',
    strict: bool = True,
    semicolon_replacement: str | None = None,
) -> pd.DataFrame:
    '''
    Convert the feature IDs of `table` into a taxonomy that maps those
    feature IDs to the typical semicolon representation. No confidence column
    is stored in the taxonomy.

    Parameters
    ----------
    table : biom.Table
        The table containing the feature IDs to be parsed into a taxonomy.
    delimiter : str
        The character(s) that delimit taxonomic levels in the feature IDs.
    strict : bool
        Whether to parse the feature IDs in strict mode. If True, then no
        occurences of semicolons are allowed in the to-be-converted IDs,
        at least one feature ID must contain `delimiter`, and no empty levels
        are allowed in the converted taxonomic string. If False, none of these
        conditions are enforced.
    semicolon_replacement : str
        The character to use to replace semicolons before replacing
        occurences of `delimiter` with semicolons.

    Returns
    --------
    pd.DataFrame
        The taxonomy parsed from the table's feature IDs with the Taxon column
        using the typical semicolon delimitation.
    '''
    if delimiter == '':
        raise ValueError('The `delimiter` must not be empty.')

    feature_ids = list(table.ids(axis='observation'))

    if strict:
        semicolon_containing_ids = [id_ for id_ in feature_ids if ';' in id_]
        if delimiter != ';' and semicolon_containing_ids:
            raise ValueError(
                f'Strict parsing with delimiter {delimiter} does not allow '
                'feature IDs that already contain ";". Found '
                f'{_format_invalid_ids(semicolon_containing_ids)}.'
            )

        ids_with_delimiter = [
            id_ for id_ in feature_ids if delimiter in id_
        ]
        if not ids_with_delimiter:
            raise ValueError(
                'Strict parsing requires at least one feature ID to contain '
                f'the delimiter {delimiter}. Found none.'
            )

        empty_level_ids = [
            id_ for id_ in feature_ids if '' in id_.split(delimiter)
        ]
        if empty_level_ids:
            raise ValueError(
                'Strict parsing found empty taxonomic levels after splitting '
                f'on delimiter {delimiter}. Found '
                f'{_format_invalid_ids(empty_level_ids)}'
            )

        taxa = [';'.join(id_.split(delimiter)) for id_ in feature_ids]

    else:
        taxa = []
        empty_level_ids = []
        for id_ in feature_ids:
            if delimiter != ';' and ';' in id_:
                if semicolon_replacement is None:
                    raise ValueError(
                        'One or more semicolons detected in the following '
                        f'id: "{id_}", and no `semicolon_replacement` was '
                        'specified.'
                    )
                if semicolon_replacement == ';':
                    raise ValueError(
                        'The `semicolon_replacement` parameter can not be '
                        'a semicolon.'
                    )

                parsed_id = id_.replace(';', semicolon_replacement)
            else:
                parsed_id = id_

            levels = parsed_id.split(delimiter)
            non_empty_levels = [level for level in levels if level != '']
            if not non_empty_levels:
                empty_level_ids.append(id_)
            else:
                taxa.append(';'.join(non_empty_levels))

        if empty_level_ids:
            raise ValueError(
                'Unable to construct non-empty taxonomy strings for '
                f'{_format_invalid_ids(empty_level_ids)}. After semicolon '
                f'replacement and splitting on delimiter {delimiter}, '
                'all parsed levels were empty. This can occur if a feature ID '
                'was empty to begin with or contained only semicolons and/or '
                'delimiters.'
            )

    taxonomy = pd.DataFrame(
        {'Taxon': taxa},
        index=pd.Index(feature_ids, name='Feature ID', dtype=object)
    )

    return taxonomy


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

    return list(ids_to_keep)


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
