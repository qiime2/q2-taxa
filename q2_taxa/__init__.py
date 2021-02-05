# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._method import collapse, filter_table, filter_seqs
from ._visualizer import barplot
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

__all__ = ['barplot', 'collapse', 'filter_table', 'filter_seqs']
