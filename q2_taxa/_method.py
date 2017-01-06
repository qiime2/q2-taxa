# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

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
