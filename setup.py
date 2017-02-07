# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages


setup(
    name="q2-taxa",
    version="2017.3.0.dev",
    packages=find_packages(),
    install_requires=['qiime2 == 2017.3.*', 'q2-types == 2017.3.*',
                      'q2templates == 2017.3.*', 'pandas'],
    author="Matthew Ryan Dillon",
    author_email="matthewrdillon@gmail.com",
    url="https://qiime2.org",
    license="BSD-3-Clause",
    description="Taxonomic analysis and visualization.",
    entry_points={
        "qiime2.plugins":
        ["q2-taxa=q2_taxa.plugin_setup:plugin"]
    },
    package_data={'q2_taxa': ['assets/barplot/index.html',
                              'assets/barplot/dst/*',
                              'assets/tabulate/*']}
)
