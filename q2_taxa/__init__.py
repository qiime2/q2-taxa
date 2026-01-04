# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._method import collapse, filter_table, filter_seqs
from ._visualizer import barplot, barplot2

try:
    from ._version import __version__
except ModuleNotFoundError:
    __version__ = '0.0.0+notfound'

__all__ = ['barplot', 'barplot2', 'collapse', 'filter_table', 'filter_seqs']
