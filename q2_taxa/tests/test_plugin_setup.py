# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from unittest import TestCase, main

from q2_taxa.plugin_setup import plugin


class PluginTests(TestCase):

    def test_plugin(self):
        self.assertEqual(plugin.name, 'taxa')


if __name__ == "__main__":
    main()
